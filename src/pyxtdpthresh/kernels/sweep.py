"""Pivoted sweep: the generalised inverse behind Mata's ``invsym()``.

Each step pivots on the largest remaining diagonal element and applies a rank-one update to the
whole matrix; a pivot at or below its floor (or NaN) is dropped and its row and column are set
to zero.  The loop is inherently sequential (pivot ``k`` depends on pivot ``k - 1``) and costs
``n`` passes over an ``n x n`` matrix, so the NumPy version is bound by memory traffic and
temporary arrays; the compiled loop updates the matrix in place.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray
from pyxtdpthresh.kernels._jit import njit


@njit
def _sweep_kernel(work: FloatArray, floor: FloatArray, dropped: BoolArray) -> None:
    """Sweep ``work`` in place and flag the dropped pivots."""
    n = work.shape[0]
    pending = np.ones(n, dtype=np.bool_)
    row = np.empty(n)
    col = np.empty(n)
    for _ in range(n):
        # argmax of the remaining diagonal: first maximum, and the first NaN wins (NumPy rule)
        k = -1
        best = -np.inf
        for i in range(n):
            if pending[i]:
                v = work[i, i]
                if np.isnan(v):
                    k = i
                    break
                if k < 0 or v > best:
                    k = i
                    best = v
        pending[k] = False
        pivot = work[k, k]
        if not pivot > floor[k]:
            work[k, :] = 0.0
            work[:, k] = 0.0
            dropped[k] = True
            continue
        for j in range(n):
            row[j] = work[k, j] / pivot
            col[j] = work[j, k]
        col[k] = 0.0
        for i in range(n):
            c = col[i]
            for j in range(n):
                work[i, j] -= c * row[j]
        for j in range(n):
            work[k, j] = row[j]
            work[j, k] = -col[j] / pivot
        work[k, k] = 1.0 / pivot


def sweep(a: FloatArray, floor: FloatArray) -> tuple[FloatArray, BoolArray]:
    """Generalised inverse of the symmetric matrix ``a`` by pivoted sweep.

    Parameters
    ----------
    a
        Symmetric ``(n, n)`` matrix (both triangles are read).
    floor
        Smallest pivot kept at each position, ``(n,)``.

    Returns
    -------
    inverse, dropped
        The symmetrised inverse and the mask of dropped pivots.
    """
    work = np.array(a, dtype=np.float64, order="C", copy=True)
    floor = np.ascontiguousarray(floor, dtype=np.float64)
    if work.ndim != 2 or work.shape[0] != work.shape[1] or floor.shape != (work.shape[0],):
        raise ValueError("a must be square and floor must have one entry per row")
    dropped = np.zeros(work.shape[0], dtype=np.bool_)
    _sweep_kernel(work, floor, dropped)
    return (work + work.T) / 2.0, dropped
