"""Variance, specification tests and post-estimation on simulated panels (block G)."""

import math
import warnings

import numpy as np
import pytest
from scipy import stats
from test_search import simulate, stack_of

from pyxtdpthresh._errors import PyxdpthreshWarning
from pyxtdpthresh.core.gmm import sandwich
from pyxtdpthresh.core.linalg import psd_ok, syminv
from pyxtdpthresh.instruments.matrix import InstrumentMatrix
from pyxtdpthresh.models.xtdpthresh.coefficients import (
    coefficient_names,
    slope_names,
    upper_regime,
)
from pyxtdpthresh.models.xtdpthresh.diagnostics import (
    ARSample,
    EstimationRows,
    ar_test,
    hansen_test,
)
from pyxtdpthresh.models.xtdpthresh.estimator import moments_by_unit, omega_of, problem_at
from pyxtdpthresh.models.xtdpthresh.fit import fit_point
from pyxtdpthresh.models.xtdpthresh.search import search_threshold, threshold_support
from pyxtdpthresh.models.xtdpthresh.variance import final_variance, windmeijer


def fitted(kink=False, seed=3, center=True):
    stack = stack_of(simulate(kink=kink, seed=seed), kink=kink)
    result = search_threshold(stack, grid=30, center=center)
    support, _ = threshold_support(stack, False)
    return stack, result, support


# ------------------------------------------------------------------------------------ Windmeijer
def explicit_windmeijer(stack, step_1, step_2, fit, resid_1, omega_1, center):
    """The formula with explicit L x L derivative matrices, as the Stata command writes it."""
    n, k = stack.n_rows, step_2.zw.shape[1]
    w1, w2 = stack.first_weight.weight, fit.weight
    b2 = np.linalg.inv(step_2.zw.T @ w2 @ step_2.zw)
    b1_inv = np.linalg.inv(step_1.zw.T @ w1 @ step_1.zw)
    gbar = stack.zy - step_2.zw @ fit.theta
    gm = moments_by_unit(stack, resid_1)
    d = np.empty((k, k))
    for j in range(k):
        hj = moments_by_unit(stack, step_1.regressors[:, j])
        dom = -(hj.T @ gm + gm.T @ hj) / n
        if center:
            hs, gs = hj.sum(axis=0), gm.sum(axis=0)
            dom = dom + (np.outer(hs, gs) + np.outer(gs, hs)) / (stack.n_units * n)
        d[:, j] = -b2 @ (step_2.zw.T @ (w2 @ (dom @ (w2 @ gbar))))
    m = b2 @ step_2.zw.T @ w2 + d @ (b1_inv @ step_1.zw.T @ w1)
    return m @ omega_1 @ m.T / n


@pytest.mark.parametrize("center", [True, False])
def test_windmeijer_without_the_derivative_matrix_equals_the_explicit_formula(center):
    stack, result, _ = fitted(center=center)
    fit = result.fit
    step_1, step_2 = problem_at(stack, result.stage1_gamma), problem_at(stack, fit.gamma)
    resid_1 = step_1.residual(stack, fit.first_theta)
    omega_1 = omega_of(stack, resid_1, center=center)
    got = windmeijer(
        stack, zw1=step_1.zw, x1=step_1.regressors, zw2=step_2.zw,
        w1=stack.first_weight.weight, w2=fit.weight, omega1=omega_1, resid1=resid_1,
        gbar2=stack.zy - step_2.zw @ fit.theta, center=center,
    )  # fmt: skip
    want = explicit_windmeijer(stack, step_1, step_2, fit, resid_1, omega_1, center)
    assert got is not None
    np.testing.assert_allclose(got, (want + want.T) / 2, rtol=1e-9, atol=1e-12)


def test_windmeijer_is_reported_only_for_a_second_step_fit_and_keeps_the_same_estimate():
    stack, result, support = fitted()
    common = dict(stage1_gamma=result.stage1_gamma, bw_scale=1.5, center=True, support=support)
    robust = final_variance(stack, result.fit, vce="robust", **common)
    wind = final_variance(stack, result.fit, vce="windmeijer", **common)
    assert not robust.wind_applied and wind.wind_applied
    assert not np.allclose(robust.cov, wind.cov)
    np.testing.assert_allclose(robust.robust, wind.robust)  # the uncorrected variance is kept
    assert psd_ok(wind.cov) and psd_ok(wind.full)


# ------------------------------------------------------------------------------ joint variance
def test_the_joint_variance_adds_the_threshold_as_a_parameter():
    stack, result, support = fitted()
    var = final_variance(
        stack, result.fit, result.stage1_gamma, vce="robust", bw_scale=1.5, center=True,
        support=support,
    )  # fmt: skip
    k = result.fit.theta.size
    assert var.joint and var.full is not None and var.full.shape == (k + 1, k + 1)
    np.testing.assert_allclose(var.cov, var.full[:k, :k])
    np.testing.assert_allclose(var.cond, result.fit.cov)
    assert var.full[k, k] > 0  # variance of the threshold
    # bandwidth rule: scale * 1.06 * s_q * n^(-1/5)
    assert var.bandwidth == pytest.approx(1.5 * 1.06 * stack.q_sd * stack.n_units**-0.2)
    assert math.isnan(var.same_threshold)


def test_the_bandwidth_is_proportional_to_bwscale_and_changes_the_variance():
    stack, result, support = fitted()

    def run(scale):
        return final_variance(
            stack, result.fit, result.stage1_gamma, vce="robust", bw_scale=scale, center=True,
            support=support,
        )  # fmt: skip

    narrow, wide = run(0.5), run(2.0)
    assert wide.bandwidth == pytest.approx(4 * narrow.bandwidth)
    assert not np.allclose(narrow.cov, wide.cov)
    np.testing.assert_allclose(narrow.cond, wide.cond)


def test_the_kink_model_has_an_analytic_derivative_and_no_bandwidth():
    stack, result, support = fitted(kink=True)
    var = final_variance(
        stack, result.fit, result.stage1_gamma, vce="robust", bw_scale=1.5, center=True,
        support=support,
    )  # fmt: skip
    assert var.joint and math.isnan(var.bandwidth) and math.isnan(var.q_nvals_bw)
    derivative = stack.regime_derivative(result.fit.gamma, result.fit.theta, math.nan)
    above = (stack.level_q > result.fit.gamma).astype(float)
    np.testing.assert_allclose(derivative, -result.fit.theta[-1] * stack.transform_levels(above))


def test_the_kernel_derivative_is_the_derivative_of_the_expected_moment():
    # E[1(q > g)] = P(q > g); its derivative in g is minus the density, which the kernel estimates
    stack, result, _ = fitted()
    gamma, h = result.fit.gamma, stack.bandwidth(1.5)
    k = stack.level_x.shape[1]
    theta = np.zeros(2 * k + 1)
    theta[k] = 1.0  # only the intercept shift: x_g = -T(phi_h(q - gamma))
    column = stack.regime_derivative(gamma, theta, h)
    u = (stack.level_q - gamma) / h
    density = np.exp(-0.5 * u * u) / (math.sqrt(2 * math.pi) * h)
    np.testing.assert_allclose(column, -stack.transform_levels(density))
    assert abs(np.mean(density) - np.mean(stats.norm.pdf(u) / h)) < 1e-12


# --------------------------------------------------------------------------------------- Hansen
def test_hansen_uses_the_second_step_criterion_and_one_degree_less_for_the_threshold():
    test = hansen_test(20.0, n_instruments=15, n_parameters=3, twostep=True)
    assert test.df == 11
    assert test.p_value == pytest.approx(stats.chi2.sf(20.0, 11))
    assert all(math.isnan(v) for v in hansen_test(20.0, 15, 3, twostep=False))
    assert all(math.isnan(v) for v in hansen_test(20.0, 4, 3, twostep=True))  # not identified


# ------------------------------------------------------------------------------------------ AR
def naive_ar_pieces(order, unit, time, resid, n_units):
    """b0, T1 and pairs by direct loops over units (the algorithm of the Stata command)."""
    b0 = t1 = pairs = clusters = 0
    sums = np.zeros(n_units)
    for u in range(n_units):
        rows = np.flatnonzero(unit == u)
        by_time = {int(time[r]): r for r in rows}
        c, found = 0.0, 0
        for r in rows:
            partner = by_time.get(int(time[r]) - order)
            if partner is not None:
                c += resid[r] * resid[partner]
                found += 1
        b0, t1, pairs = b0 + c, t1 + c * c, pairs + found
        clusters += found > 0
        sums[u] = c
    return b0, t1, pairs, clusters, sums


def random_ar_problem(seed):
    rng = np.random.default_rng(seed)
    n_units, n_inst, p = 30, 6, 3
    unit, time = [], []
    for u in range(n_units):
        periods = np.sort(rng.choice(np.arange(1, 9), size=rng.integers(3, 8), replace=False))
        unit += [u] * periods.size
        time += periods.tolist()
    unit, time = np.array(unit), np.array(time)
    n = unit.size
    z = InstrumentMatrix(rng.normal(size=(n, n_inst)))
    x = rng.normal(size=(n, p))
    resid = rng.normal(size=n)
    weight = np.linalg.inv(np.cov(rng.normal(size=(n_inst, 50))) + np.eye(n_inst))
    cov = np.cov(rng.normal(size=(p, 40))) + np.eye(p) * 0.1
    return unit, time, x, resid, z, weight, cov, n_units


@pytest.mark.parametrize("order", [1, 2])
@pytest.mark.parametrize("seed", range(3))
def test_ar_statistic_equals_the_per_unit_loops_of_the_definition(order, seed):
    unit, time, x, resid, z, weight, cov, n_units = random_ar_problem(seed)
    rows = ARSample(resid, x, unit, time)
    est = EstimationRows(resid, x, z, unit, weight, n_units)
    got = ar_test(order, rows, est, cov)
    b0, t1, pairs, clusters, sums = naive_ar_pieces(order, unit, time, resid, n_units)
    assert (got.b0, got.t1, got.n_pairs, got.n_clusters) == pytest.approx((b0, t1, pairs, clusters))
    # estimation-error terms written out with explicit sums
    g = x.T @ np.array([resid[np.flatnonzero((unit == unit[r]) & (time == time[r] - order))[0]]
                        if np.any((unit == unit[r]) & (time == time[r] - order)) else 0.0
                        for r in range(unit.size)])  # fmt: skip
    s = z.dense.T @ (resid * sums[unit])
    moments = x.T @ z.dense
    inv = np.linalg.inv(moments @ weight @ moments.T)
    t2 = -2 * g @ (inv @ moments @ weight @ s)
    t3 = g @ cov @ g
    assert got.tt == pytest.approx(t2 + t3)
    assert got.statistic == pytest.approx(b0 / math.sqrt(t1 + t2 + t3))
    assert got.p_value == pytest.approx(2 * stats.norm.sf(abs(got.statistic)))


def test_ar_needs_five_pairs_in_five_units_and_otherwise_reports_nothing():
    unit = np.repeat(np.arange(3), 4)
    time = np.tile(np.arange(1, 5), 3)
    resid = np.random.default_rng(0).normal(size=12)
    est = EstimationRows(resid, np.ones((12, 1)), InstrumentMatrix(np.ones((12, 2))),
                         unit, np.eye(2), 3)  # fmt: skip
    got = ar_test(1, ARSample(resid, np.ones((12, 1)), unit, time), est, np.eye(1))
    assert math.isnan(got.statistic) and math.isnan(got.n_pairs) and got.n_clusters == 3


# ---------------------------------------------------------------------------------- coefficients
def test_coefficient_names_follow_the_equations_of_the_command():
    labels = ("L.y", "x", "L.q")
    assert coefficient_names(labels, kink=False, q="q") == (
        "lower:L.y", "lower:x", "lower:L.q",
        "change:_cons", "change:L.y", "change:x", "change:L.q",
    )  # fmt: skip
    assert coefficient_names(labels, kink=True, q="q")[-1] == "change:q"


def test_names_that_are_not_variables_are_made_valid_and_unique():
    assert slope_names(("L(1)x", "L(1)x")) == ("L1x", "L1x_1")
    assert slope_names(("a.b/c",)) == ("a_b_c",)
    assert len(slope_names(("x" * 40 + "/",))[0]) == 32


def test_upper_slopes_are_the_sum_of_lower_and_change():
    names = coefficient_names(("a",), kink=False, q="q")  # lower:a, change:_cons, change:a
    cov = np.diag([1.0, 2.0, 3.0])
    up = upper_regime(np.array([1.0, 10.0, 0.5]), cov, names, kink=False, q="q")
    assert up is not None and up.names == ("upper:a",)
    np.testing.assert_allclose(up.b, [1.5])
    np.testing.assert_allclose(up.cov, [[1.0 + 3.0]])


def test_kink_has_an_upper_slope_only_when_q_is_a_regressor():
    with_q = coefficient_names(("L.y", "q"), kink=True, q="q")
    up = upper_regime(np.array([1.0, 2.0, 0.5]), np.eye(3), with_q, kink=True, q="q")
    assert up is not None and up.names == ("upper:q",)
    np.testing.assert_allclose(up.b, [2.5])
    np.testing.assert_allclose(up.cov, [[2.0]])
    without_q = coefficient_names(("L.y", "x"), kink=True, q="q")
    assert upper_regime(np.array([1.0, 2.0, 0.5]), np.eye(3), without_q, kink=True, q="q") is None


# ----------------------------------------------------------------------------- end to end
def run(df, **options):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(df, "y", ("x",), q="q", id="id", time="t", bootstrap=False,
                         collapse=True, grid=30, **options)  # fmt: skip


def test_the_fit_exposes_the_stored_results_under_the_names_of_stata():
    fit = run(simulate())
    scalars = fit.scalars
    for name in ("N", "N_units", "N_clust", "N_switch", "N_iv", "gamma", "obj", "hansen",
                 "hansen_p", "ar1", "ar2", "joint_vce", "gamma_bw", "vce_applied",
                 "estimator_twostep", "level", "q_lo", "q_hi", "grid_admitted"):  # fmt: skip
        assert name in scalars
    assert scalars["N_clust"] == scalars["N_units"] == fit.n_units
    assert scalars["level"] == 95.0 and scalars["joint_vce"] == 1.0
    assert fit.upper is not None and fit.upper.names == ("upper:L.y", "upper:x")


def test_a_discrete_threshold_variable_warns_that_the_joint_variance_assumes_a_density():
    df = simulate(q_values=[0.1, 0.3, 0.55, 0.8])
    with pytest.warns(PyxdpthreshWarning, match="distinct values"):
        fit_point(df, "y", ("x",), q="q", id="id", time="t", bootstrap=False, collapse=True,
                  grid=10)  # fmt: skip
    assert run(df).variance.q_nvals_bw < 10


def test_the_windmeijer_request_is_reported_when_it_is_applied():
    fit = run(simulate(), vce="windmeijer")
    assert fit.variance.wind_applied and fit.scalars["vce_applied"] == 1.0
    assert fit.variance.cov.shape == fit.variance.cond.shape


def test_predict_returns_the_series_aligned_with_the_frame():
    df = simulate()
    fit = run(df)
    resid, xb = fit.predict("residuals", df), fit.predict("xb", df)
    assert resid.index.equals(df.index) and resid.notna().sum() == fit.n_obs
    placed = np.full(len(df), np.nan)
    placed[fit.data.source_row[fit.stack.row]] = fit.stack.dy
    np.testing.assert_allclose((resid + xb).to_numpy(), placed)
    regime = fit.predict("regime", df)
    assert set(regime.dropna().unique()) <= {0.0, 1.0}
    np.testing.assert_array_equal(regime.to_numpy() == 1.0, (df["q"] > fit.search.fit.gamma))


def test_sandwich_of_the_conditional_variance_is_what_the_fit_reports():
    stack, result, _ = fitted()
    fit = result.fit
    step = problem_at(stack, fit.gamma)
    omega = omega_of(stack, step.residual(stack, fit.theta), center=True)
    np.testing.assert_allclose(sandwich(step.zw, fit.weight, omega, stack.n_rows), fit.cov)
    assert syminv(fit.weight).ok
