"""Kernel for many small symmetric inverses against the NumPy reference."""

import os
import subprocess
import sys
import tempfile
import textwrap

import numpy as np
import pytest

from pyxtdpthresh.core.linalg import syminv, syminv_batch
from pyxtdpthresh.kernels.reference.syminv import syminv_many as reference
from pyxtdpthresh.kernels.syminv import MAX_SIZE, syminv_many

EPS = float(np.finfo(float).eps)


def matrices(seed, size=5, count=300):
    """Positive definite matrices of every conditioning, then the ones that must be refused."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(count):
        x = rng.normal(size=(size, size))
        out.append(x @ x.T + 10.0 ** rng.uniform(-6, 1) * np.eye(size))
    u, _ = np.linalg.qr(rng.normal(size=(size, size)))
    for k in (1, 4, 8, 11, 12, 13, 14):  # smallest eigenvalue 10^-k: the limit is 1e12
        out.append(u @ np.diag([1.0] * (size - 1) + [10.0**-k]) @ u.T)
    bad = np.eye(size)
    out += [np.zeros((size, size)), -np.eye(size), np.full((size, size), np.nan)]
    out += [np.diag([1.0] * (size - 1) + [-1.0]), np.where(bad == 0, np.inf, 1.0)]
    out.append(np.ones((size, size)))  # singular
    return np.array(out)


@pytest.mark.parametrize("size", [1, 2, 3, 5, 8, MAX_SIZE])
def test_the_decisions_and_the_inverses_equal_the_reference(size):
    a = matrices(size, size)
    ok, inverse = syminv_many(a)
    ref_ok, ref_inverse = reference(a)
    np.testing.assert_array_equal(ok, ref_ok)
    assert ok.sum() > 100 and (~ok).sum() >= 4
    assert np.all(np.isnan(inverse[~ok]))
    both = np.flatnonzero(ok)
    cond = np.linalg.cond(a[both])
    gap = np.max(np.abs(inverse[both] - ref_inverse[both]), axis=(1, 2))
    scale = np.max(np.abs(ref_inverse[both]), axis=(1, 2))
    assert np.all(gap <= 10 * size * EPS * cond * scale + 1e-300)  # within the conditioning error


def test_the_inverse_is_an_inverse():
    a = matrices(0)
    ok, inverse = syminv_many(a)
    product = np.matmul(a[ok], inverse[ok])
    cond = np.linalg.cond(a[ok])
    error = np.max(np.abs(product - np.eye(5)), axis=(1, 2))
    assert np.all(error <= np.maximum(1e-8, 50 * EPS * cond))


def test_a_single_matrix_decision_is_that_of_syminv():
    for matrix in matrices(2)[:60]:
        single = syminv(matrix)
        ok, inverse = syminv_many(matrix[None])
        assert bool(ok[0]) == single.ok
        if single.ok:
            np.testing.assert_allclose(inverse[0], single.inv, rtol=1e-6, atol=1e-8)


def test_syminv_batch_sends_small_matrices_to_the_kernel_and_large_ones_to_numpy():
    small, large = matrices(1, 4, 40), matrices(1, MAX_SIZE + 3, 40)
    for a in (small, large):
        ok, inverse = syminv_batch(a)
        ref_ok, ref_inverse = reference(a)
        np.testing.assert_array_equal(ok, ref_ok)
        cond = np.linalg.cond(a[ok])
        gap = np.max(np.abs(inverse[ok] - ref_inverse[ok]), axis=(1, 2))
        scale = np.max(np.abs(ref_inverse[ok]), axis=(1, 2))
        assert np.all(gap <= 10 * a.shape[1] * EPS * cond * scale)
    with pytest.raises(ValueError):
        syminv_many(large)


def test_the_shape_is_checked():
    with pytest.raises(ValueError):
        syminv_many(np.eye(3))
    with pytest.raises(ValueError):
        syminv_many(np.ones((2, 3, 4)))


def test_the_kernel_agrees_with_jit_disabled():
    code = textwrap.dedent(
        """
        import sys
        import numpy as np
        sys.path.insert(0, ".")
        from tests.unit.test_syminv_kernel import matrices
        from pyxtdpthresh.kernels.syminv import syminv_many
        ok, inverse = syminv_many(matrices(7, 4, 40))
        np.savez(sys.argv[1], ok=ok, inverse=inverse)
        """
    )
    ok, inverse = syminv_many(matrices(7, 4, 40))
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "out.npz")
        env = {**os.environ, "NUMBA_DISABLE_JIT": "1"}
        subprocess.run([sys.executable, "-c", code, path], check=True, env=env)
        with np.load(path) as saved:
            np.testing.assert_array_equal(saved["ok"], ok)
            np.testing.assert_allclose(saved["inverse"], inverse, rtol=1e-10, equal_nan=True)
