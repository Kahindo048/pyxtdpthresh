"""Threshold search on a simulated panel with a known threshold."""

import warnings

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import DataError, PyxdpthreshWarning
from pyxtdpthresh.models.xtdpthresh.design import check_specification
from pyxtdpthresh.models.xtdpthresh.sample import prepare_data
from pyxtdpthresh.models.xtdpthresh.search import search_threshold
from pyxtdpthresh.models.xtdpthresh.stack import build_stack

TRUE_GAMMA = 0.5


def simulate(n=400, t=8, seed=3, q_values=None, kink=False):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        alpha = rng.normal()
        y_prev = rng.normal()
        for period in range(t):
            q = rng.uniform() if q_values is None else rng.choice(q_values)
            x = rng.normal()
            above = q > TRUE_GAMMA
            slope = 4.0 * (q - TRUE_GAMMA) * above if kink else 3.0 * above
            y = 0.4 * y_prev + 1.0 * x + slope * x + 2.0 * above + alpha + 0.3 * rng.normal()
            rows.append((i, period, y, x, q))
            y_prev = y
    return pd.DataFrame(rows, columns=["id", "t", "y", "x", "q"])


def stack_of(df, **options):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        spec = check_specification(
            y="y", x=("x",), q="q", bootstrap=False, collapse=True, **options
        )
        data = prepare_data(df, spec, id="id", time="t")
    return build_stack(data)


def test_the_search_recovers_a_known_jump_threshold():
    stack = stack_of(simulate())
    result = search_threshold(stack, grid=60)
    assert abs(result.fit.gamma - TRUE_GAMMA) < 0.15
    assert result.fit.twostep and result.fit.theta.size == 2 * stack.dx.shape[1] + 1
    assert result.grid_requested == 60 == result.grid_effective
    assert 0 < result.grid_admitted <= 60
    assert result.admitted_lo <= result.fit.gamma <= result.admitted_hi
    # the reported variance is a covariance matrix
    assert np.all(np.linalg.eigvalsh(result.fit.cov) > -1e-12)


def test_refine_adds_observed_values_between_the_neighbours_and_never_worsens_the_fit():
    stack = stack_of(simulate())
    plain = search_threshold(stack, grid=12)
    refined = search_threshold(stack, grid=12, refine=3)
    assert refined.refine is not None and refined.refine.added > 0
    assert refined.grid_effective == 12 + refined.refine.added
    assert refined.fit.obj <= plain.fit.obj * (1 + 1e-10)
    assert refined.grid_admitted == plain.grid_admitted  # stage 1 uses the initial grid only


def test_kink_refinement_moves_the_estimate_off_the_grid_and_lowers_the_criterion():
    stack = stack_of(simulate(kink=True), kink=True)
    result = search_threshold(stack, grid=10)
    # the continuous criterion is minimised between the grid neighbours: one point is added
    # exactly when that point beats the grid minimiser
    assert result.grid_effective == 10 + int(result.kink_refined)
    assert result.kink_refined == (result.fit.gamma not in result.grid[:10])
    assert result.fit.theta.size == stack.dx.shape[1] + 1


def test_quantile_grid_and_minimum_regime_restrict_the_admitted_points():
    stack = stack_of(simulate())
    wide = search_threshold(stack, grid=30)
    narrow = search_threshold(stack, grid=30, min_regime=900)
    assert narrow.grid_admitted < wide.grid_admitted
    on_quantiles = search_threshold(stack, grid=20, grid_type="quantile")
    assert on_quantiles.grid_effective == 20


def test_a_threshold_variable_with_two_values_has_a_flat_profile():
    stack = stack_of(simulate(q_values=[0.2, 0.8]))
    with pytest.raises(DataError) as raised:
        search_threshold(stack, grid=20)
    assert raised.value.key in {"xd_profile_flat", "xd_no_gamma", "q_no_variation"}
    assert raised.value.stata_code == 498


def test_centering_changes_only_the_variance():
    stack = stack_of(simulate())
    centred = search_threshold(stack, grid=30, center=True)
    uncentred = search_threshold(stack, grid=30, center=False)
    assert not np.allclose(centred.fit.cov, uncentred.fit.cov, rtol=1e-9, atol=0)
    assert centred.fit.gamma == pytest.approx(uncentred.fit.gamma, abs=0.2)
