"""core.gmm.solve_grid against the formula written one grid point at a time."""

import numpy as np
import pytest

from pyxtdpthresh.core import linalg
from pyxtdpthresh.core.gmm import moment_covariance, solve_grid


def literal(a, y, w):
    """Mata's GMM_cal, step by step for each grid point."""
    out = []
    for g in range(a.shape[0]):
        wg = w[g] if w.ndim == 3 else w
        est = linalg.invsym(a[g].T @ wg @ a[g]) @ (a[g].T @ wg @ y)
        gbar = y - a[g] @ est
        out.append((est, gbar, gbar @ wg @ gbar))
    return out


def problem(seed=0, n_grid=9, n_mom=14, n_par=5, per_point_weight=False):
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((n_grid, n_mom, n_par))
    y = rng.standard_normal(n_mom)

    def spd():
        m = rng.standard_normal((n_mom, n_mom))
        return m @ m.T + n_mom * np.eye(n_mom)

    w = np.stack([spd() for _ in range(n_grid)]) if per_point_weight else spd()
    return a, y, w


@pytest.mark.parametrize("per_point", [False, True])
def test_solve_grid_equals_the_literal_formula(per_point):
    a, y, w = problem(per_point_weight=per_point)
    sol = solve_grid(a, y, w)
    for g, (est, gbar, crit) in enumerate(literal(a, y, w)):
        np.testing.assert_allclose(sol.theta[g], est, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(sol.gbar[g], gbar, rtol=1e-9, atol=1e-12)
        assert sol.crit[g] == pytest.approx(crit, rel=1e-9)


def test_empty_regime_columns_are_dropped_like_mata():
    a, y, w = problem(1)
    a[2, :, 3:] = 0.0  # regime columns empty at this grid point (extreme threshold)
    a[5, :, 4] = 0.0
    sol = solve_grid(a, y, w)
    assert np.all(sol.theta[2, 3:] == 0.0) and sol.theta[5, 4] == 0.0
    for g, (est, _gbar, crit) in enumerate(literal(a, y, w)):
        np.testing.assert_allclose(sol.theta[g], est, rtol=1e-9, atol=1e-12)
        assert sol.crit[g] == pytest.approx(crit, rel=1e-9)


def test_exactly_identified_system_has_zero_criterion():
    rng = np.random.default_rng(2)
    a = rng.standard_normal((4, 6, 6))
    y = rng.standard_normal(6)
    sol = solve_grid(a, y, np.eye(6))
    np.testing.assert_allclose(sol.crit, 0.0, atol=1e-18)
    for g in range(4):
        np.testing.assert_allclose(a[g] @ sol.theta[g], y, atol=1e-8)


def test_bread_inverse_is_returned():
    a, y, w = problem(3)
    sol = solve_grid(a, y, w)
    np.testing.assert_allclose(sol.bread_inv[0], np.linalg.inv(a[0].T @ w @ a[0]), rtol=1e-8)


def test_shape_errors():
    a, y, w = problem()
    with pytest.raises(ValueError):
        solve_grid(a, y[:-1], w)
    with pytest.raises(ValueError):
        solve_grid(a, y, np.stack([w, w]))


def test_moment_covariance_is_the_biased_sample_covariance():
    g = np.random.default_rng(4).standard_normal((50, 6)) + 3.0
    np.testing.assert_allclose(moment_covariance(g), np.cov(g.T, bias=True), atol=1e-12)
    np.testing.assert_allclose(moment_covariance(g, center=False), g.T @ g / 50, atol=1e-12)
