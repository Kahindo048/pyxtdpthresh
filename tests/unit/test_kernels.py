"""Numba kernels against their NumPy references."""

import os
import subprocess
import sys
import textwrap

import numpy as np
import pytest
from scipy import sparse

from pyxtdpthresh._config import option_context
from pyxtdpthresh.kernels import moments, sweep, units
from pyxtdpthresh.kernels._jit import set_threads
from pyxtdpthresh.kernels.reference import moments as ref_moments
from pyxtdpthresh.kernels.reference import sweep as ref_sweep
from pyxtdpthresh.kernels.reference import units as ref_units
from pyxtdpthresh.kernels.warmup import warmup


def make_problem(seed=0, n_units=30, rows_per_unit=4, n_instr=12, n_reg=3, n_grid=17, density=0.4):
    """Random equation rows with sparse instruments and 1 to 3 level pairs per row."""
    rng = np.random.default_rng(seed)
    n_eq = n_units * rows_per_unit
    n_level = n_units * (rows_per_unit + 1)
    z = rng.standard_normal((n_eq, n_instr)) * (rng.random((n_eq, n_instr)) < density)
    n_pairs = rng.integers(0, 4, size=n_eq)  # some rows have no pair at all
    pair_ptr = np.concatenate([[0], np.cumsum(n_pairs)])
    pair_lev = rng.integers(0, n_level, size=pair_ptr[-1])
    pair_w = rng.choice([-1.0, 1.0, 0.5], size=pair_ptr[-1])
    w_level = rng.standard_normal((n_level, n_reg))
    q_level = np.round(rng.standard_normal(n_level), 1)  # many ties
    grid = np.sort(np.round(rng.standard_normal(n_grid), 1))  # grid values equal to some q
    unit_ptr = np.arange(0, n_eq + 1, rows_per_unit)
    return z, pair_ptr, pair_lev, pair_w, w_level, q_level, grid, unit_ptr


@pytest.mark.parametrize("seed", range(5))
def test_regime_moments_equal_reference(seed):
    z, ptr, lev, w, wl, q, grid, _ = make_problem(seed)
    fast = moments.regime_moments(z, ptr, lev, w, wl, q, grid)
    slow = ref_moments.regime_moments(z, ptr, lev, w, wl, q, grid)
    assert fast.shape == (grid.size, z.shape[1], wl.shape[1])
    np.testing.assert_allclose(fast, slow, rtol=1e-12, atol=1e-12)


def test_regime_moments_strict_inequality_at_grid_values():
    # one pair, q exactly equal to grid[1]: counts for grid[0] only
    z = np.array([[1.0]])
    out = moments.regime_moments(
        z,
        np.array([0, 1]),
        np.array([0]),
        np.array([1.0]),
        np.array([[2.0]]),
        np.array([5.0]),
        np.array([4.0, 5.0, 6.0]),
    )
    assert out[:, 0, 0].tolist() == [2.0, 0.0, 0.0]


def test_regime_moments_missing_q_never_counts_and_extremes():
    z = np.array([[1.0], [1.0], [1.0]])
    ptr, lev, w = np.array([0, 1, 2, 3]), np.array([0, 1, 2]), np.ones(3)
    wl = np.ones((3, 1))
    q = np.array([np.nan, -10.0, 10.0])  # NaN, below grid, above grid
    out = moments.regime_moments(z, ptr, lev, w, wl, q, np.array([0.0, 1.0]))
    assert out[:, 0, 0].tolist() == [1.0, 1.0]  # only the q = 10 row


def test_regime_moments_accepts_sparse_and_degenerate_shapes():
    z, ptr, lev, w, wl, q, grid, _ = make_problem(3, n_reg=1)
    ref = ref_moments.regime_moments(z, ptr, lev, w, wl, q, grid[:1])
    got = moments.regime_moments(sparse.csr_matrix(z), ptr, lev, w, wl, q, grid[:1])
    np.testing.assert_allclose(got, ref, rtol=1e-12, atol=1e-12)
    assert got.shape == (1, z.shape[1], 1)


def test_regime_moments_rejects_unsorted_grid_and_bad_pointer():
    z, ptr, lev, w, wl, q, grid, _ = make_problem(1)
    with pytest.raises(ValueError, match="sorted"):
        moments.regime_moments(z, ptr, lev, w, wl, q, grid[::-1])
    with pytest.raises(ValueError, match="pair_ptr"):
        moments.regime_moments(z, ptr[:-1], lev, w, wl, q, grid)


def test_regime_moments_is_deterministic_across_thread_counts():
    args = make_problem(2, n_units=200, n_instr=40)[:7]
    with option_context(threads=1):
        one = moments.regime_moments(*args)
    with option_context(threads=4):
        four = moments.regime_moments(*args)
    np.testing.assert_array_equal(one, four)  # each thread owns its slice: bit-identical


@pytest.mark.parametrize("seed", range(4))
def test_unit_moments_equal_reference(seed):
    z, *_rest, unit_ptr = make_problem(seed)
    resid = np.random.default_rng(seed).standard_normal(z.shape[0])
    fast = units.unit_moments(z, resid, unit_ptr)
    np.testing.assert_allclose(fast, ref_units.unit_moments(z, resid, unit_ptr), atol=1e-12)
    # summing the units gives Z' resid
    np.testing.assert_allclose(fast.sum(axis=0), z.T @ resid, atol=1e-10)


def test_unit_moments_unequal_units_and_errors():
    z = np.arange(12.0).reshape(6, 2)
    ptr = np.array([0, 1, 1, 6])  # an empty unit in the middle
    resid = np.ones(6)
    out = units.unit_moments(z, resid, ptr)
    np.testing.assert_allclose(out, [z[0], [0.0, 0.0], z[1:].sum(axis=0)])
    with pytest.raises(ValueError):
        units.unit_moments(z, resid[:5], ptr)


@pytest.mark.parametrize(("n", "rank"), [(1, 1), (5, 5), (30, 10), (60, 60), (100, 40)])
def test_sweep_equals_reference_including_dropped_pivots(n, rank):
    x = np.random.default_rng(n).standard_normal((n, rank))
    a = x @ x.T
    floor = np.maximum(1e-9 * np.diag(a), 9e-20)
    inv, dropped = sweep.sweep(a, floor)
    ref_inv, ref_dropped = ref_sweep.sweep(a, floor)
    np.testing.assert_array_equal(dropped, ref_dropped)
    np.testing.assert_allclose(inv, ref_inv, rtol=1e-13, atol=1e-13)
    assert dropped.sum() == max(n - rank, 0)


def test_sweep_nan_diagonal_and_bad_shapes():
    a = np.array([[2.0, 0.0, 0.0], [0.0, np.nan, 0.0], [0.0, 0.0, 3.0]])
    floor = np.full(3, 1e-9)
    inv, dropped = sweep.sweep(a, floor)
    ref_inv, ref_dropped = ref_sweep.sweep(a, floor)
    np.testing.assert_array_equal(dropped, ref_dropped)
    np.testing.assert_array_equal(inv, ref_inv)
    with pytest.raises(ValueError):
        sweep.sweep(np.ones((2, 3)), np.ones(2))
    with pytest.raises(ValueError):
        sweep.sweep(np.eye(3), np.ones(2))


def test_kernels_agree_with_jit_disabled():
    """The reference test of A.3.2: same answers with NUMBA_DISABLE_JIT=1."""
    code = textwrap.dedent(
        """
        import sys
        import numpy as np
        sys.path.insert(0, ".")
        from tests.unit.test_kernels import make_problem
        from pyxtdpthresh.kernels import moments, sweep, units
        z, ptr, lev, w, wl, q, grid, up = make_problem(9)
        a = moments.regime_moments(z, ptr, lev, w, wl, q, grid)
        b = units.unit_moments(z, np.arange(float(z.shape[0])), up)
        np.save(sys.argv[1], a); np.save(sys.argv[2], b)
        x = np.random.default_rng(3).standard_normal((40, 15)); m = x @ x.T
        np.save(sys.argv[3], sweep.sweep(m, np.maximum(1e-9 * np.diag(m), 9e-20))[0])
        """
    )
    import tempfile

    z, ptr, lev, w, wl, q, grid, up = make_problem(9)
    with tempfile.TemporaryDirectory() as tmp:
        fa, fb, fc = (os.path.join(tmp, f"{n}.npy") for n in "abc")
        env = {**os.environ, "NUMBA_DISABLE_JIT": "1"}
        subprocess.run([sys.executable, "-c", code, fa, fb, fc], check=True, env=env)
        x = np.random.default_rng(3).standard_normal((40, 15))
        m = x @ x.T
        expected, _ = sweep.sweep(m, np.maximum(1e-9 * np.diag(m), 9e-20))
        np.testing.assert_allclose(np.load(fc), expected, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(
            np.load(fa), moments.regime_moments(z, ptr, lev, w, wl, q, grid), rtol=1e-12, atol=1e-12
        )
        np.testing.assert_allclose(
            np.load(fb), units.unit_moments(z, np.arange(float(z.shape[0])), up), atol=1e-12
        )


def test_set_threads_and_warmup():
    assert set_threads(1) == 1
    assert set_threads(None) >= 1
    warmup()  # must run without error once the kernels are compiled
