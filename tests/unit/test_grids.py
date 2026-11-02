"""Tests of core.quantiles and core.grids: properties and error handling."""

import numpy as np
import pytest

from pyxtdpthresh._errors import DataError, SpecificationError
from pyxtdpthresh.core import grids, quantiles


# ---------------------------------------------------------------- mm_quantile
def test_mm_quantile_matches_numpy_averaged_inverted_cdf():
    rng = np.random.default_rng(0)
    x = np.round(rng.standard_normal(257), 1)  # ties
    p = np.linspace(0.0, 1.0, 41)
    np.testing.assert_allclose(
        quantiles.mm_quantile(x, p), np.quantile(x, p, method="averaged_inverted_cdf")
    )


def test_mm_quantile_small_cases():
    x = np.array([3.0, 1.0, 2.0, 4.0])
    assert quantiles.mm_quantile(x, 0.5) == 2.5  # p*n = 2 exactly: mean of 2 and 3
    assert quantiles.mm_quantile(x, 0.6) == 3.0
    assert quantiles.mm_quantile(x, 0.0) == 1.0
    assert quantiles.mm_quantile(x, 1.0) == 4.0
    assert quantiles.mm_quantile(x, -0.3) == 1.0 and quantiles.mm_quantile(x, 7.0) == 4.0


def test_mm_quantile_rejects_missing_and_handles_empty():
    with pytest.raises(DataError):
        quantiles.mm_quantile(np.array([1.0, np.nan]), 0.5)
    assert np.isnan(quantiles.mm_quantile(np.array([]), 0.5))


def test_mm_quantile_does_not_modify_input():
    x = np.array([3.0, 1.0, 2.0])
    quantiles.mm_quantile(x, 0.5)
    assert x.tolist() == [3.0, 1.0, 2.0]


# -------------------------------------------------------------- type 7
def test_type7_matches_numpy_linear_and_ignores_missing():
    rng = np.random.default_rng(1)
    x = rng.standard_normal(101)
    p = np.linspace(0.0, 1.0, 23)
    np.testing.assert_allclose(quantiles.quantile_type7(x, p), np.quantile(x, p))
    with_nan = np.concatenate([x, [np.nan, np.nan]])
    np.testing.assert_allclose(quantiles.quantile_type7(with_nan, p), np.quantile(x, p))
    assert np.isnan(quantiles.quantile_type7(np.array([np.nan]), 0.5))


def test_the_two_estimators_differ_so_both_are_needed():
    x = np.arange(1.0, 11.0)
    assert quantiles.mm_quantile(x, 0.1) == 1.5
    assert quantiles.quantile_type7(x, 0.1) == pytest.approx(1.9)


# ------------------------------------------------------------------ rangen
def test_rangen_endpoints_and_spacing():
    r = quantiles.rangen(-1.0, 2.0, 7)
    assert r[0] == -1.0 and r[-1] == 2.0 and r.size == 7
    np.testing.assert_allclose(np.diff(r), 0.5)
    assert quantiles.rangen(3.0, 9.0, 1).tolist() == [3.0]


def test_rangen_last_point_is_exactly_the_bound():
    a, b = 0.1, 0.7
    assert quantiles.rangen(a, b, 3)[-1] == b


# --------------------------------------------------------------- the grids
def test_xthenreg_grid_trims_with_mm_quantile():
    q = np.arange(1.0, 101.0)
    g = grids.xthenreg_grid(q, 0.4, 50)
    assert g.size == 50
    assert g[0] == quantiles.mm_quantile(q, 0.2) and g[-1] == quantiles.mm_quantile(q, 0.8)


def test_quantile_grid_is_sorted_unique_and_collapses_ties():
    q = np.repeat(np.arange(5.0), 40)
    g = grids.quantile_grid(q, 0.1, 0.9, 30)
    assert g.size < 30 and np.all(np.diff(g) > 0)


def test_threshold_grid_uniform_and_quantile():
    q = np.random.default_rng(2).standard_normal(500)
    u = grids.threshold_grid(q, 0.2, 40)
    assert u.grid.size == 40 and u.grid[0] == u.q_lo and u.grid[-1] == u.q_hi
    z = grids.threshold_grid(q, 0.2, 40, grid_type="quantile")
    assert z.grid[0] == pytest.approx(u.q_lo) and z.grid[-1] == pytest.approx(u.q_hi)
    assert u.min_regime == u.min_regime_default >= 2


def test_min_regime_can_only_raise_the_default_floor():
    q = np.random.default_rng(3).standard_normal(400)
    base = grids.threshold_grid(q, 0.2, 20)
    low = grids.threshold_grid(q, 0.2, 20, min_regime=2)
    high = grids.threshold_grid(q, 0.2, 20, min_regime=base.min_regime_default + 25)
    assert low.min_regime == base.min_regime_default
    assert high.min_regime == base.min_regime_default + 25


def test_threshold_grid_errors():
    with pytest.raises(SpecificationError):
        grids.threshold_grid(np.arange(30.0), 0.2, 10, min_regime=16)
    with pytest.raises(DataError) as few:
        grids.threshold_grid(np.arange(10.0), 0.2, 10)
    assert few.value.stata_code == 498
    with pytest.raises(DataError):
        grids.threshold_grid(np.ones(50), 0.2, 10)


def test_admissible_counts_each_side():
    q = np.arange(1.0, 101.0)
    grid = np.array([0.5, 9.0, 10.0, 50.0, 90.0, 95.0, 100.0])
    ok = grids.admissible(grid, q, 10)
    assert ok.tolist() == [False, False, True, True, True, False, False]
