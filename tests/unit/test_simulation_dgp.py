"""Data generating processes (block I.5.1): the moments of the draws are those of the design."""

import warnings

import numpy as np
import pandas as pd
import pytest

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh.extras.simulation import DESIGNS, Design, resolve_design, simulate_panel
from pyxtdpthresh.models.xtdpthresh.fit import fit_point

# A panel large enough for the sample moments to be within a few standard errors.
N, T = 20000, 6


def wide(frame, column):
    """``column`` as an (n, t) array of a balanced panel."""
    return frame[column].to_numpy().reshape(-1, frame["t"].nunique())


# --------------------------------------------------------------------------------- shape
def test_the_panel_is_long_balanced_and_ordered():
    frame = simulate_panel("gong_seo", n=30, t=6, seed=1)
    assert list(frame.columns) == ["id", "t", "y", "q"]
    assert len(frame) == 180
    assert frame["id"].is_monotonic_increasing and frame.groupby("id")["t"].apply(list).iloc[0] == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]
    assert frame.notna().all().all()


def test_every_design_returns_the_same_four_columns():
    for name in DESIGNS:
        frame = simulate_panel(name, n=20, t=5, seed=1)
        assert list(frame.columns) == ["id", "t", "y", "q"], name
        assert len(frame) == 100 and frame.notna().all().all()


def test_the_panel_is_a_function_of_the_seed():
    a = simulate_panel("gong_seo", n=50, t=6, seed=7)
    b = simulate_panel("gong_seo", n=50, t=6, seed=7)
    c = simulate_panel("gong_seo", n=50, t=6, seed=8)
    pd.testing.assert_frame_equal(a, b)
    assert not np.allclose(a["y"], c["y"])
    d = simulate_panel("gong_seo", n=50, t=6, seed=np.random.SeedSequence(7))
    pd.testing.assert_frame_equal(a, d)


# ------------------------------------------------------------------------ the moments
def test_q_is_stationary_with_the_variance_of_an_ar1():
    frame = simulate_panel("gong_seo", n=N, t=T, seed=2)
    q = wide(frame, "q")
    rho, u_sd = 0.7, 1.0
    assert np.var(q[:, 0]) == pytest.approx(u_sd**2 / (1 - rho**2), rel=0.03)
    assert np.var(q[:, -1]) == pytest.approx(u_sd**2 / (1 - rho**2), rel=0.03)
    corr = np.corrcoef(q[:, 2], q[:, 3])[0, 1]
    assert corr == pytest.approx(rho, abs=0.02)


def test_the_weak_design_pairs_the_error_with_the_next_innovation():
    """``q_{t+1}`` carries ``rho_eu`` of ``e_t`` and ``q_t`` is clean of ``e_t``."""
    spec = resolve_design("gong_seo", sigma=1.0, beta_y=0.0, beta_x=0.0, delta0=0.0, delta_x=0.0)
    frame = simulate_panel(spec, n=N, t=T, seed=3)
    y, q = wide(frame, "y"), wide(frame, "q")  # y_t = e_t when every slope is zero
    innovation = q[:, 1:] - 0.7 * q[:, :-1]  # u_{t+1}
    assert np.corrcoef(y[:, :-1].ravel(), innovation.ravel())[0, 1] == pytest.approx(0.5, abs=0.02)
    assert np.corrcoef(y[:, 1:].ravel(), innovation.ravel())[0, 1] == pytest.approx(0.0, abs=0.02)
    assert np.corrcoef(y.ravel(), q.ravel())[0, 1] == pytest.approx(0.0, abs=0.02)


def test_the_endogenous_design_pairs_the_error_with_the_same_innovation():
    spec = resolve_design(
        "gong_seo_endog", sigma=1.0, beta_y=0.0, beta_x=0.0, delta0=0.0, delta_x=0.0
    )
    frame = simulate_panel(spec, n=N, t=T, seed=3)
    y, q = wide(frame, "y"), wide(frame, "q")
    innovation = q[:, 1:] - 0.7 * q[:, :-1]
    assert np.corrcoef(y[:, 1:].ravel(), innovation.ravel())[0, 1] == pytest.approx(0.5, abs=0.02)
    assert np.corrcoef(y[:, :-1].ravel(), innovation.ravel())[0, 1] == pytest.approx(0.0, abs=0.02)


def test_the_conditional_mean_is_the_regression_function_of_the_design():
    """OLS of y on y(-1), q and the regime interactions recovers the lower/upper slopes."""
    spec = resolve_design("gong_seo", sigma=0.1, rho_eu=0.0)
    frame = simulate_panel(spec, n=N, t=T, seed=4)
    y, q = wide(frame, "y"), wide(frame, "q")
    above = (q[:, 1:] > spec.gamma).ravel()
    lag, now, out = y[:, :-1].ravel(), q[:, 1:].ravel(), y[:, 1:].ravel()
    design = np.column_stack(
        [lag, now, np.ones_like(lag), lag * above, now * above, above.astype(float)]
    )
    coef = np.linalg.lstsq(design, out, rcond=None)[0]
    expected = [spec.beta_y, spec.beta_x, 0.0, spec.delta_y, spec.delta_x, spec.delta0]
    np.testing.assert_allclose(coef, expected, atol=0.02)


# ------------------------------------------------------------------- Seo and Shin (2016)
#: Equations (16) and (17) of the paper: (intercept, slope) below and above the threshold.
SEO_SHIN = {
    "seo_shin_jump": (0.0, (0.7, -0.5), (-1.8, 0.7), 1.0),
    "seo_shin_cont": (0.8, (0.52, 0.6), (1.48, -0.6), 0.5),
    "seo_shin_jump_common": (1.5, (0.7, -0.5), (0.7, 0.7), 1.0),
    "seo_shin_cont_common": (0.4, (0.52, 0.6), (0.52, -0.6), 0.5),
}


@pytest.mark.parametrize("name", list(SEO_SHIN))
def test_the_self_exciting_designs_have_the_papers_regression_function(name):
    gamma, below, above, sigma = SEO_SHIN[name]
    design = DESIGNS[name]
    assert design.gamma == gamma and design.sigma == sigma
    assert (design.beta0, design.beta_y) == below
    assert design.beta0 + design.delta0 == pytest.approx(above[0])
    assert design.beta_y + design.delta_y == pytest.approx(above[1])
    assert design.threshold_kind == "lag_y" and design.x_name is None


def test_the_papers_parameters_beta_and_delta():
    """Section 6.1: beta = -0.5, (d1, d2) = (-2.5, 1.2) and beta = 0.6, (d1, d2) = (0.96, -1.2)."""
    jump, cont = DESIGNS["seo_shin_jump"], DESIGNS["seo_shin_cont"]
    assert (jump.beta_y, jump.delta0, jump.delta_y) == (-0.5, -2.5, 1.2)
    assert (cont.beta_y, cont.delta0, cont.delta_y) == (0.6, 0.96, -1.2)
    assert jump.jump == pytest.approx(-2.5) and cont.jump == pytest.approx(0.0)  # Chan-Tsay: a kink
    assert set(jump.truth) == {
        "lower:L.y", "change:_cons", "change:L.y", "upper:L.y", "gamma",
    }  # fmt: skip


@pytest.mark.parametrize("name", ["seo_shin_jump", "seo_shin_cont"])
def test_the_threshold_variable_is_the_lagged_outcome(name):
    frame = simulate_panel(name, n=300, t=10, seed=3)
    y, q = wide(frame, "y"), wide(frame, "q")
    np.testing.assert_array_equal(q[:, 1:], y[:, :-1])  # q_t = y_{t-1} within each unit
    assert np.isfinite(q[:, 0]).all()  # the first q is the outcome of the unobserved period 0


@pytest.mark.parametrize("name", list(SEO_SHIN))
def test_the_simulated_outcome_follows_the_regression_function(name):
    """Each regime's OLS on y(-1) recovers its intercept and slope when the noise is small."""
    gamma, below, above, _ = SEO_SHIN[name]
    frame = simulate_panel(name, n=4000, t=10, seed=5, sigma=0.01)
    y, q = wide(frame, "y"), wide(frame, "q")
    lag, now, out = y[:, :-1].ravel(), q[:, 1:].ravel(), y[:, 1:].ravel()
    for regime, (intercept, slope) in ((now <= gamma, below), (now > gamma, above)):
        if regime.sum() > 50:
            coef = np.polyfit(lag[regime], out[regime], 1)
            np.testing.assert_allclose(coef, [slope, intercept], atol=0.03)


def test_the_exogenous_threshold_is_uniform_and_independent_of_the_outcome():
    frame = simulate_panel("seo_shin_exogenous", n=N, t=T, seed=8)
    q = wide(frame, "q")
    assert q.min() >= -1.0 and q.max() <= 1.0
    assert q.mean() == pytest.approx(0.0, abs=0.01) and q.var() == pytest.approx(1 / 3, rel=0.03)
    y = wide(frame, "y")
    assert np.corrcoef(q[:, 1:].ravel(), y[:, :-1].ravel())[0, 1] == pytest.approx(0.0, abs=0.02)
    assert np.corrcoef(q[:, 1:].ravel(), q[:, :-1].ravel())[0, 1] == pytest.approx(0.0, abs=0.02)
    design = DESIGNS["seo_shin_exogenous"]
    assert design.threshold_kind == "uniform" and design.gamma == 0.0
    assert design.jump == design.delta0 == -2.5  # the intercept change: the slope is on y(-1)


def test_the_errors_of_the_self_exciting_design_have_the_requested_scale():
    """With no regime effect left, the innovations of the model are sigma times N(0, 1)."""
    spec = resolve_design("seo_shin_jump", beta0=0.0, beta_y=0.0, delta0=0.0, delta_y=0.0)
    frame = simulate_panel(spec, n=N, t=T, seed=9, sigma=0.5)
    assert frame["y"].std() == pytest.approx(0.5, rel=0.02)


# ------------------------------------------------------------------------ truth and jump
def test_the_truth_is_keyed_like_the_coefficients_of_a_fit():
    design = DESIGNS["gong_seo"]
    truth = design.truth
    assert truth["gamma"] == 0.25
    assert truth["lower:L.y"] == 0.6 and truth["lower:q"] == 1.0
    assert truth["change:_cons"] == -0.3 and truth["change:q"] == 2.0
    assert truth["upper:q"] == 3.0 and truth["upper:L.y"] == 0.6
    assert "lower:q" not in DESIGNS["seo_shin_jump"].truth


def test_the_jump_sets_the_intercept_change():
    for jump in (0.0, 0.1, 1.0):
        design = resolve_design("gong_seo", jump=jump)
        assert design.jump == pytest.approx(jump)
    assert resolve_design("gong_seo", jump=0.0).delta0 == pytest.approx(-0.5)  # d1 = -d3 g
    assert resolve_design("gong_seo", jump=0.5).delta0 == pytest.approx(0.0)


def test_the_continuous_design_has_no_jump_in_the_mean():
    """At jump = 0 the regression function is continuous at the threshold: a kink."""
    d = resolve_design("gong_seo", jump=0.0)
    below = d.beta_x * d.gamma
    above = d.beta_x * d.gamma + d.delta0 + d.delta_x * d.gamma
    assert above == pytest.approx(below)


def test_the_linear_design_has_no_threshold():
    design = DESIGNS["linear"]
    assert not design.has_threshold and np.isnan(design.truth["gamma"])
    assert design.truth["change:q"] == 0.0 and design.truth["upper:q"] == design.truth["lower:q"]
    linear = simulate_panel("linear", n=N, t=T, seed=6)
    shifted = simulate_panel("linear", n=N, t=T, seed=6, gamma=-3.0)
    pd.testing.assert_frame_equal(linear, shifted)  # the threshold plays no role


# ---------------------------------------------------------------------- unbalanced panel
def test_unbalanced_panels_keep_the_values_of_the_balanced_one():
    balanced = simulate_panel("gong_seo", n=200, t=8, seed=9)
    gaps = simulate_panel("gong_seo", n=200, t=8, seed=9, unbalanced=0.25)
    assert len(gaps) < len(balanced)
    assert 0.65 < len(gaps) / len(balanced) < 0.85
    merged = gaps.merge(balanced, on=["id", "t"], suffixes=("_g", ""))
    assert len(merged) == len(gaps)
    np.testing.assert_array_equal(merged["y_g"], merged["y"])
    np.testing.assert_array_equal(merged["q_g"], merged["q"])
    assert (gaps.groupby("id").size() >= 3).all()
    assert gaps.groupby("id").size().nunique() > 1  # the number of periods varies
    assert gaps.groupby("id")["t"].apply(lambda s: s.diff().max() > 1).any()  # real gaps


def test_the_panel_with_gaps_is_estimated():
    frame = simulate_panel("gong_seo", n=300, t=8, seed=9, unbalanced=0.15)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        fit = fit_point(frame, "y", id="id", time="t", n_boot=19, **DESIGNS["gong_seo"].arguments())
    assert fit.scalars["N_units"] > 0.9 * frame["id"].nunique()


# -------------------------------------------------------------------- the estimator's view
@pytest.mark.parametrize("name", list(DESIGNS))
def test_every_design_is_estimated_with_its_own_arguments(name):
    design = DESIGNS[name]
    frame = simulate_panel(design, n=250, t=6, seed=11)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        fit = fit_point(frame, "y", id="id", time="t", n_boot=19, grid=30, **design.arguments())
    assert np.isfinite(fit.search.fit.gamma)
    expected = {k for k in design.truth if k != "gamma" and not k.startswith("upper:")}
    assert expected <= set(fit.names)


def test_the_instruments_of_the_paper_are_not_collapsed():
    assert DESIGNS["gong_seo"].arguments()["collapse"] is False
    assert DESIGNS["gong_seo"].arguments()["predetermined"] == ("q",)
    assert DESIGNS["gong_seo_endog"].arguments()["endogenous"] == ("q",)


# ----------------------------------------------------------------------------- refusals
@pytest.mark.parametrize(
    ("call", "key"),
    [
        (lambda: simulate_panel("nope"), "sim_unknown_design"),
        (lambda: simulate_panel("gong_seo", gamma_x=1.0), "sim_unknown_parameter"),
        (lambda: simulate_panel("gong_seo", n=1), "sim_bad_size"),
        (lambda: simulate_panel("gong_seo", t=1), "sim_bad_size"),
        (lambda: simulate_panel("gong_seo", burn=-1), "sim_bad_size"),
        (lambda: simulate_panel("gong_seo", unbalanced=1.0), "sim_bad_share"),
        (lambda: simulate_panel("gong_seo", rho_eu=1.0), "sim_bad_correlation"),
    ],
)
def test_bad_requests_are_refused_with_their_key(call, key):
    with pytest.raises(SpecificationError) as caught:
        call()
    assert caught.value.key == key


def test_a_design_instance_is_accepted_and_overridden():
    custom = Design("mine", gamma=0.5, roles={"predetermined": ("q",)})
    frame = simulate_panel(custom, n=40, t=4, seed=1, sigma=0.2)
    assert len(frame) == 160
    assert resolve_design(custom, sigma=0.2).sigma == 0.2
