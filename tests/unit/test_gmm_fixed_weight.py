"""GMM with a fixed weight, cluster covariance of the moments, sandwich and first-step weight."""

import numpy as np
import pytest

from pyxtdpthresh.core.gmm import MIN_EQUATIONS, cluster_omega, sandwich, solve_fixed_weight
from pyxtdpthresh.core.weights import stacked_ma1_weight


def system(seed=0, n=60, k=3, n_inst=5):
    rng = np.random.default_rng(seed)
    z = rng.normal(size=(n, n_inst))
    x = z[:, :k] + 0.3 * rng.normal(size=(n, k))
    theta = np.array([1.0, -2.0, 0.5])
    y = x @ theta + 0.1 * rng.normal(size=n)
    return z, x, y, theta


def test_just_identified_system_is_instrumental_variables():
    z, x, y, _ = system(n_inst=3)
    zw, zy = z.T @ x / 60, z.T @ y / 60
    fit = solve_fixed_weight(zw, zy, np.eye(3), 60)
    assert fit.ok
    np.testing.assert_allclose(fit.theta, np.linalg.solve(z.T @ x, z.T @ y), rtol=1e-9)
    assert fit.obj == pytest.approx(0.0, abs=1e-18)


def test_overidentified_estimate_and_criterion_follow_the_formulas():
    z, x, y, _ = system()
    n = 60
    zw, zy, w = z.T @ x / n, z.T @ y / n, np.linalg.inv(z.T @ z / n)
    fit = solve_fixed_weight(zw, zy, w, n)
    expected = np.linalg.solve(zw.T @ w @ zw, zw.T @ w @ zy)
    np.testing.assert_allclose(fit.theta, expected, rtol=1e-9)
    gbar = zy - zw @ expected
    assert fit.obj == pytest.approx(n * gbar @ w @ gbar, rel=1e-9)
    np.testing.assert_allclose(fit.cov, np.linalg.inv(zw.T @ w @ zw) / n, rtol=1e-9)


def test_too_few_equations_or_singular_bread_are_rejected():
    z, x, y, _ = system()
    zw, zy = z.T @ x / 60, z.T @ y / 60
    assert not solve_fixed_weight(zw, zy, np.eye(5), MIN_EQUATIONS - 1).ok
    assert not solve_fixed_weight(zw, zy, np.zeros((5, 5)), 60).ok
    assert not solve_fixed_weight(zw, zy, np.eye(4), 60).ok  # wrong shape


def test_cluster_omega_sums_by_unit_and_scales_by_equations():
    g = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, 1.0]])
    plain = cluster_omega(g, n_rows=6, n_clusters=3, center=False)
    np.testing.assert_allclose(plain, g.T @ g / 6)
    mean = g.sum(axis=0)
    centred = cluster_omega(g, n_rows=6, n_clusters=3, center=True)
    np.testing.assert_allclose(centred, g.T @ g / 6 - np.outer(mean, mean) / (3 * 6))
    # a unit without equations is a zero row and changes nothing
    padded = np.vstack([g, np.zeros((1, 2))])
    np.testing.assert_allclose(cluster_omega(padded, 6, 3, True), centred)
    assert np.isnan(cluster_omega(np.array([[np.inf, 0.0]]), 1, 1, False)).all()


def test_sandwich_of_the_efficient_weight_is_the_inverse_of_the_bread():
    z, x, _, _ = system()
    n = 60
    zw = z.T @ x / n
    omega = np.cov(z.T) + np.eye(5)
    w = np.linalg.inv(omega)
    cov = sandwich(zw, w, omega, n)
    np.testing.assert_allclose(cov, np.linalg.inv(zw.T @ w @ zw) / n, rtol=1e-8)
    assert sandwich(zw, w, np.eye(4), n) is None
    assert sandwich(zw, np.zeros((5, 5)), omega, n) is None


def test_first_step_weight_falls_back_to_plain_inverse_then_identity():
    second = np.diag([2.0, 3.0])
    ok = stacked_ma1_weight(second, np.array([[0.1, 0.0], [0.0, 0.1]]))
    assert ok.fallback == 0
    np.testing.assert_allclose(ok.weight, np.linalg.inv(2 * second - 0.2 * np.eye(2)))
    # 2 W2 - W1 - W1' is singular but W2 is not
    plain = stacked_ma1_weight(second, second)
    assert plain.fallback == 1
    np.testing.assert_allclose(plain.weight, np.linalg.inv(second))
    singular = stacked_ma1_weight(np.zeros((2, 2)), np.zeros((2, 2)))
    assert singular.fallback == 2
    np.testing.assert_array_equal(singular.weight, np.eye(2))
