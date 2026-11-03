"""Bootstrap building blocks and statistical behaviour (block H)."""

import math
import warnings

import numpy as np
import pytest
from test_search import TRUE_GAMMA, simulate

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.core.linalg import syminv, syminv_batch
from pyxtdpthresh.inference.bootstrap.draws import OFFSETS, BootstrapStreams, mammen_weights
from pyxtdpthresh.inference.bootstrap.objective import (
    criterion,
    critical_value,
    is_degenerate,
    make_family,
    profile_min,
    sample_moments,
)
from pyxtdpthresh.inference.bootstrap.rng import StataRNG, component_seed
from pyxtdpthresh.models.xtdpthresh.fit import fit_point


# ------------------------------------------------------------------------------- draws
def test_mammen_weights_have_two_values_mean_zero_and_unit_variance():
    weights = mammen_weights(StataRNG(7), 4000, 50)
    phi = (math.sqrt(5) - 1) / 2
    low, high = -phi, 1 / phi
    assert set(np.unique(weights)) == {low, high}
    assert abs(weights.mean()) < 0.02 and abs(weights.var() - 1.0) < 0.03
    assert weights.shape == (4000, 50)


def test_weights_are_drawn_replication_after_replication_from_the_stata_stream():
    rng = StataRNG(11)
    stream = rng.copy().uniform(5 * 3)
    weights = mammen_weights(rng, 5, 3)
    p_low = (math.sqrt(5) + 1) / (2 * math.sqrt(5))
    expected = np.where(stream < p_low, -(math.sqrt(5) - 1) / 2, 2 / (math.sqrt(5) - 1))
    # column b holds the draws 5b .. 5b + 4 of the stream
    np.testing.assert_allclose(weights, expected.reshape(3, 5).T)


def test_with_a_seed_each_component_restarts_at_its_own_offset():
    streams = BootstrapStreams(2026)
    first = streams.stream("linearity").uniform(3)
    streams.stream("threshold").uniform(100)  # another component must not move it
    again = streams.stream("linearity").uniform(3)
    np.testing.assert_array_equal(first, again)
    np.testing.assert_array_equal(
        first, StataRNG(component_seed(2026, OFFSETS["linearity"])).uniform(3)
    )
    assert streams.component_seed("citest") == (2026 + 477377) % 2**31


def test_without_a_seed_the_components_share_one_stream():
    streams = BootstrapStreams(None)
    assert streams.stream("threshold") is streams.stream("linearity")
    assert streams.component_seed("threshold") is None
    with pytest.raises(KeyError):
        streams.stream("other")


# ---------------------------------------------------------------------------- criterion
def naive_criterion(zw, weight, moments, n_rows):
    """GMM at fixed weight written out for one candidate and one sample."""
    bread = zw.T @ weight @ zw
    theta = np.linalg.solve(bread, zw.T @ weight @ moments)
    g = moments - zw @ theta
    return n_rows * g @ weight @ g


def random_family(seed, candidates=6, moments_n=8, params=3):
    rng = np.random.default_rng(seed)
    zws = [rng.normal(size=(moments_n, params)) for _ in range(candidates)]
    a = rng.normal(size=(moments_n, moments_n))
    return zws, a @ a.T + moments_n * np.eye(moments_n), rng


@pytest.mark.parametrize("seed", range(3))
def test_batched_criterion_equals_the_one_sample_one_candidate_formula(seed):
    zws, weight, rng = random_family(seed)
    family = make_family(zws, weight, 3)
    moments = rng.normal(size=(8, 5))
    got = criterion(family, moments, 200)
    for g, zw in enumerate(zws):
        for b in range(5):
            assert got[g, b] == pytest.approx(
                naive_criterion(zw, weight, moments[:, b], 200), rel=1e-10
            )
    # the same without the quadratic forms (the memory-saving path)
    plain = type(family)(family.zw, family.solver, family.solvable, family.weight, None)
    np.testing.assert_allclose(criterion(plain, moments, 200), got, rtol=1e-10)


def test_a_candidate_that_cannot_be_solved_has_no_criterion():
    zws, weight, rng = random_family(0, candidates=3)
    zws[1] = np.zeros_like(zws[1])  # singular normal matrix
    zws[2] = None  # not admitted
    family = make_family(zws, weight, 3)
    assert family.solvable.tolist() == [True, False, False]
    out = criterion(family, rng.normal(size=(8, 4)), 100)
    assert np.isfinite(out[0]).all() and np.isnan(out[1:]).all()


def test_sample_moments_equal_the_moments_of_the_resampled_dependent_variable():
    rng = np.random.default_rng(1)
    n_units, per_unit, n_moments = 7, 4, 5
    unit = np.repeat(np.arange(n_units), per_unit)
    z = rng.normal(size=(unit.size, n_moments))
    fitted, resid = rng.normal(size=unit.size), rng.normal(size=unit.size)
    eta = rng.normal(size=(n_units, 6))
    per = np.zeros((n_units, n_moments))
    np.add.at(per, unit, z * resid[:, None])
    got = sample_moments(z.T @ fitted / unit.size, per, eta, unit.size)
    y_star = fitted[:, None] + resid[:, None] * eta[unit]
    np.testing.assert_allclose(got, z.T @ y_star / unit.size)


# ----------------------------------------------------------------------- critical value
def test_critical_value_is_the_order_statistic_of_rank_ceil_p_times_n_plus_one():
    values = np.arange(1.0, 100.0)  # n = 99
    assert critical_value(values, 0.95) == 95.0  # ceil(.95 * 100) = 95
    assert critical_value(np.arange(1.0, 20.0), 0.95) == 19.0  # ceil(19) = 19 (n = 19)
    assert critical_value(np.arange(1.0, 19.0), 0.95) == math.inf  # rank 19 > n = 18
    assert math.isnan(critical_value(np.array([np.nan]), 0.95))
    assert critical_value(np.array([3.0, np.nan, 1.0, 2.0]), 0.5) == 2.0  # ceil(2) = 2


def test_accept_if_distance_below_the_critical_value_is_the_add_one_rule():
    rng = np.random.default_rng(2)
    draws = rng.normal(size=299) ** 2
    crit = critical_value(draws, 0.95)
    for statistic in np.linspace(0.05, 8, 40):
        p_value = (1 + np.sum(draws >= statistic)) / (1 + draws.size)
        assert (statistic <= crit) == (p_value > 0.05)


def test_profile_minimum_breaks_ties_towards_the_smaller_threshold():
    values = np.array([3.0, 1.0, 1.0 + 1e-14, 2.0, np.nan])
    gammas = np.array([0.1, 0.5, 0.2, 0.3, 0.4])
    best, count, high = profile_min(values, gammas)
    assert (best, count, high) == (2, 4, 3.0)  # a tie within 1e-12: the smaller gamma wins
    assert is_degenerate(1.0, 1.0 + 1e-13, 3) and is_degenerate(1.0, 2.0, 1)
    assert not is_degenerate(1.0, 2.0, 3)


# --------------------------------------------------------------------------- batched syminv
def test_syminv_batch_takes_the_decisions_of_syminv():
    rng = np.random.default_rng(3)
    mats = []
    for _ in range(30):
        a = rng.normal(size=(4, 4))
        mats.append(a @ a.T + 0.05 * np.eye(4))
    mats.append(np.zeros((4, 4)))  # singular
    mats.append(-np.eye(4))  # not positive definite
    mats.append(np.diag([1.0, 1.0, 1.0, 1e-15]))  # condition above 1e12
    bad = mats[0].copy()
    bad[0, 0] = np.nan
    mats.append(bad)
    arr = np.stack(mats)
    ok, inverse = syminv_batch(arr)
    for i, matrix in enumerate(arr):
        single = syminv(matrix)
        assert ok[i] == single.ok
        if single.ok:
            np.testing.assert_allclose(inverse[i], single.inv, rtol=1e-8, atol=1e-10)
        else:
            assert np.isnan(inverse[i]).all()


# ----------------------------------------------------------------------- end to end
def run(df, **options):
    options = {"collapse": True, "grid": 25, "grid_ci": 25, **options}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(df, "y", ("x",), q="q", id="id", time="t", **options)


def test_the_same_seed_gives_the_same_inference_and_a_different_seed_does_not():
    df = simulate(n=250, t=7)
    one = run(df, seed=5, n_boot=49)
    two = run(df, seed=5, n_boot=49)
    other = run(df, seed=6, n_boot=49)
    np.testing.assert_array_equal(one.bootstrap.ci.table, two.bootstrap.ci.table)
    assert one.bootstrap.linearity.p_value == two.bootstrap.linearity.p_value
    assert not np.array_equal(one.bootstrap.ci.table[:, 2], other.bootstrap.ci.table[:, 2])


def test_asking_for_one_component_does_not_change_the_others_when_seeded():
    df = simulate(n=250, t=7)
    full = run(df, seed=9, n_boot=49)
    only_ci = run(df, seed=9, n_boot=49, linearity_test=False)
    np.testing.assert_array_equal(full.bootstrap.ci.table, only_ci.bootstrap.ci.table)
    assert only_ci.bootstrap.linearity is None


def test_the_confidence_set_contains_the_estimate_and_the_true_threshold():
    fit = run(simulate(n=500, t=8, seed=4), seed=3, n_boot=99)
    ci = fit.bootstrap.ci
    assert ci.n_unresolved == 0 and ci.empty == 0
    assert ci.lo <= fit.search.fit.gamma <= ci.hi
    assert ci.lo - 0.05 <= TRUE_GAMMA <= ci.hi + 0.05


def test_unit_resampling_gives_a_confidence_set_that_contains_the_estimate():
    df = simulate(n=250, t=7)
    fit = run(df, seed=1, n_boot=19, boot_type="unit")
    assert fit.bootstrap.ci.table.shape[1] == 6
    assert fit.bootstrap.ci.lo <= fit.search.fit.gamma <= fit.bootstrap.ci.hi


def test_the_bootstrap_scalars_are_exposed_under_the_names_of_stata():
    fit = run(simulate(n=250, t=7), seed=5, n_boot=49)
    scalars = fit.scalars
    for name in (
        "gamma_lo",
        "gamma_hi",
        "ci_empty",
        "ci_nseg",
        "ci_incomplete",
        "pval_lin",
        "rseed",
    ):
        assert name in scalars
    assert scalars["rseed"] == 5.0 and 0 < scalars["pval_lin"] <= 1


# ----------------------------------------------------------------- statistical coherence
@pytest.mark.slow
def test_linearity_test_has_the_right_size_and_power_on_simulated_panels():
    def linear_panel(seed):
        rng = np.random.default_rng(seed)
        rows = []
        for i in range(120):
            alpha, y_prev = rng.normal(), rng.normal()
            for t in range(6):
                q, x = rng.uniform(), rng.normal()
                y = 0.4 * y_prev + x + alpha + 0.4 * rng.normal()
                rows.append((i, t, y, x, q))
                y_prev = y
        import pandas as pd

        return pd.DataFrame(rows, columns=["id", "t", "y", "x", "q"])

    pvalues = [
        run(linear_panel(s), seed=s, n_boot=39, grid_ci=10).bootstrap.linearity.p_value
        for s in range(40)
    ]
    assert all(0 < p <= 1 for p in pvalues)
    assert np.mean(np.array(pvalues) <= 0.10) <= 0.25  # nominal 10 %, sampling noise allowed
    rejections = [
        run(
            simulate(n=300, t=6, seed=100 + s), seed=s, n_boot=39, grid_ci=10, collapse=False
        ).bootstrap.linearity.p_value
        for s in range(10)
    ]
    assert np.mean(np.array(rejections) <= 0.10) >= 0.3  # power of the distance test is modest


def test_the_progress_indicator_is_silent_by_default_and_reports_when_asked(capsys):
    from pyxtdpthresh._config import option_context

    df = simulate(n=200, t=6)
    run(df, seed=1, n_boot=19, grid_ci=10, linearity_test=False)
    assert capsys.readouterr().err == ""
    with option_context(progress=True):
        run(df, seed=1, n_boot=19, grid_ci=10, linearity_test=False)
    err = capsys.readouterr().err
    assert "confidence set" in err and "done" in err and "left" in err
