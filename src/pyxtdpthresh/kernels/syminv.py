"""Admission and inverse of many small symmetric matrices (``xdpt2_syminv``), one per thread.

The bootstrap inverts one ``p x p`` normal matrix (``p`` is the number of coefficients, a handful)
for every candidate threshold in every draw: several hundred thousand matrices per run.  Calling
LAPACK through NumPy for each costs eight microseconds, mostly in overhead; here each matrix is
handled by plain loops, in parallel across matrices.

The decision is that of ``syminv``: equilibrate by the diagonal, positive definite, 2-norm
condition number at most ``1e12`` (eigenvalues by Jacobi rotations, accurate for the smallest one
of a positive definite matrix), inverse checked against the identity within
``max(1e-8, 10 p eps cond)``.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.kernels._jit import apply_threads, njit, pjit, prange

#: Largest ``p`` the kernel is meant for (beyond it LAPACK is faster than Jacobi rotations).
MAX_SIZE = 12
_EPS = 2.220446049250313e-16
_MAX_COND = 1e12
_MAX_SWEEPS = 100


@njit
def _finite_positive(a: FloatArray) -> bool:
    """Every entry is finite and every diagonal entry is positive."""
    p = a.shape[0]
    for i in range(p):
        if not a[i, i] > 0.0:
            return False
        for j in range(p):
            if not np.isfinite(a[i, j]):
                return False
    return True


@njit
def _inverse_error(equil: FloatArray, inv: FloatArray, p: int) -> float:
    """Largest entry of ``equil @ inv - I``."""
    error = 0.0
    for i in range(p):
        for j in range(p):
            total = 0.0
            for k in range(p):
                total += equil[i, k] * inv[k, j]
            if i == j:
                total -= 1.0
            error = max(error, abs(total))
    return error


@njit
def _invert_one(a: FloatArray, out: FloatArray) -> bool:
    """Write the inverse of ``a`` into ``out`` and return whether ``a`` is admitted."""
    p = a.shape[0]
    if not _finite_positive(a):
        return False
    scale = np.empty(p)
    for i in range(p):
        scale[i] = np.sqrt(a[i, i])
    equil = np.empty((p, p))
    for i in range(p):
        for j in range(p):
            equil[i, j] = (a[i, j] / (scale[i] * scale[j]) + a[j, i] / (scale[j] * scale[i])) / 2.0
    low, high = _extreme_eigenvalues(equil, p)
    if not low > 0.0 or not high / low <= _MAX_COND:
        return False
    cond = high / low
    inv = np.empty((p, p))
    if not _gauss_jordan(equil, inv, p):
        return False
    if not _inverse_error(equil, inv, p) <= max(1e-8, 10.0 * p * _EPS * cond):
        return False
    for i in range(p):
        for j in range(p):
            value = inv[i, j] / (scale[i] * scale[j])
            if not np.isfinite(value):
                return False
            out[i, j] = value
    return True


@pjit
def _syminv_kernel(a: FloatArray, ok: BoolArray, inverse: FloatArray) -> None:
    """Fill ``ok`` and ``inverse`` for every matrix of ``a`` ``(G, p, p)``."""
    for g in prange(a.shape[0]):
        ok[g] = _invert_one(a[g], inverse[g])
        if not ok[g]:
            inverse[g] = np.nan


@njit
def _extreme_eigenvalues(matrix: FloatArray, p: int) -> tuple[float, float]:
    """Smallest and largest eigenvalue of a symmetric matrix by cyclic Jacobi rotations."""
    w = matrix.copy()
    for _ in range(_MAX_SWEEPS):
        rotated = False
        for r in range(p - 1):
            for c in range(r + 1, p):
                off = w[r, c]
                if abs(off) <= 1e-17 * np.sqrt(abs(w[r, r] * w[c, c])) or off == 0.0:
                    continue
                rotated = True
                theta = (w[c, c] - w[r, r]) / (2.0 * off)
                t = (1.0 if theta >= 0.0 else -1.0) / (abs(theta) + np.sqrt(theta * theta + 1.0))
                cos = 1.0 / np.sqrt(t * t + 1.0)
                sin = t * cos
                for k in range(p):
                    wr, wc = w[k, r], w[k, c]
                    w[k, r] = cos * wr - sin * wc
                    w[k, c] = sin * wr + cos * wc
                for k in range(p):
                    wr, wc = w[r, k], w[c, k]
                    w[r, k] = cos * wr - sin * wc
                    w[c, k] = sin * wr + cos * wc
        if not rotated:
            break
    low, high = w[0, 0], w[0, 0]
    for i in range(1, p):
        low = min(low, w[i, i])
        high = max(high, w[i, i])
    return low, high


@njit
def _exchange_rows(work: FloatArray, inverse: FloatArray, first: int, second: int) -> None:
    """Swap two rows of both matrices."""
    for j in range(work.shape[0]):
        work[first, j], work[second, j] = work[second, j], work[first, j]
        inverse[first, j], inverse[second, j] = inverse[second, j], inverse[first, j]


@njit
def _gauss_jordan(matrix: FloatArray, inverse: FloatArray, p: int) -> bool:
    """Invert ``matrix`` into ``inverse`` with partial pivoting; ``False`` if it is singular."""
    work = matrix.copy()
    for i in range(p):
        for j in range(p):
            inverse[i, j] = 1.0 if i == j else 0.0
    for col in range(p):
        pivot_row = col
        for r in range(col + 1, p):
            if abs(work[r, col]) > abs(work[pivot_row, col]):
                pivot_row = r
        if work[pivot_row, col] == 0.0:
            return False
        if pivot_row != col:
            _exchange_rows(work, inverse, col, pivot_row)
        pivot = work[col, col]
        for j in range(p):
            work[col, j] /= pivot
            inverse[col, j] /= pivot
        for r in range(p):
            factor = work[r, col]
            if r != col and factor != 0.0:
                for j in range(p):
                    work[r, j] -= factor * work[col, j]
                    inverse[r, j] -= factor * inverse[col, j]
    return True


def syminv_many(a: FloatArray) -> tuple[BoolArray, FloatArray]:
    """Admission and inverse of the symmetric matrices ``a`` ``(G, p, p)``, ``p <= MAX_SIZE``.

    Returns
    -------
    ok, inverse
        Admission mask ``(G,)`` and the inverses (``nan`` where not admitted).
    """
    arr = np.ascontiguousarray(a, dtype=np.float64)
    if arr.ndim != 3 or arr.shape[1] != arr.shape[2] or not 0 < arr.shape[1] <= MAX_SIZE:
        raise ValueError(f"expected matrices of size 1 to {MAX_SIZE}, got shape {arr.shape}")
    apply_threads()
    ok = np.zeros(arr.shape[0], dtype=np.bool_)
    inverse = np.full(arr.shape, np.nan)
    _syminv_kernel(arr, ok, inverse)
    return ok, inverse
