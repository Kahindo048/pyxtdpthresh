"""Regime moments ``Z' dW(gamma)`` for a whole grid of thresholds in one pass.

In the stacked GMM system only the regime columns depend on the threshold.  Each equation row
``e`` (a unit and an equation period) is linked to a few *level* observations ``l`` with a
weight ``w`` (``+1 / -1`` for first differences, longer lists for forward orthogonal
deviations).  Whatever the model, the regime moment of instrument ``j`` and regressor ``k`` is

    S[g, j, k] = sum_e Z[e, j] * sum_{(l, w) of e} w * W[l, k] * 1(q[l] > gamma_g)

An observation with ``q[l]`` above ``m`` grid points contributes to the first ``m`` grid
points only.  The kernel therefore adds each contribution once, to the bucket ``m``, and a
reverse cumulative sum over the buckets gives all the grid points: the cost is
O(pairs * nnz_per_column * K + G * L * K) instead of O(G * pairs * L * K).

The kernel loops over instruments (``prange``), each thread owning the slice ``S[:, j, :]``,
and reads ``Z`` in compressed-column form so that block-sparse instruments cost nothing.
"""

from __future__ import annotations

import numpy as np
from scipy import sparse

from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.kernels._jit import apply_threads, pjit, prange


@pjit
def _regime_moments_kernel(
    z_ptr: IntArray,
    z_row: IntArray,
    z_val: FloatArray,
    pair_ptr: IntArray,
    pair_lev: IntArray,
    pair_w: FloatArray,
    pair_bucket: IntArray,
    w_level: FloatArray,
    n_grid: int,
    out: FloatArray,
) -> None:
    """Fill ``out[g, j, :]`` for every grid point ``g`` and instrument ``j``."""
    n_instr = z_ptr.shape[0] - 1
    n_reg = w_level.shape[1]
    for j in prange(n_instr):
        acc = np.zeros((n_grid + 1, n_reg))
        for idx in range(z_ptr[j], z_ptr[j + 1]):
            e = z_row[idx]
            z = z_val[idx]
            for p in range(pair_ptr[e], pair_ptr[e + 1]):
                bucket = pair_bucket[p]
                if bucket == 0:
                    continue  # q at or below the whole grid: never in the upper regime
                weight = z * pair_w[p]
                lev = pair_lev[p]
                for k in range(n_reg):
                    acc[bucket, k] += weight * w_level[lev, k]
        run = np.zeros(n_reg)
        for g in range(n_grid - 1, -1, -1):
            for k in range(n_reg):
                run[k] += acc[g + 1, k]
                out[g, j, k] = run[k]


def pair_buckets(q_level: FloatArray, pair_lev: IntArray, grid: FloatArray) -> IntArray:
    """Count the grid points strictly below ``q`` of each pair's level observation.

    A missing ``q`` is placed in bucket 0, so that it is never above the threshold.
    """
    q = np.asarray(q_level, dtype=np.float64)[pair_lev]
    bucket = np.searchsorted(grid, q, side="left").astype(np.int64)
    bucket[np.isnan(q)] = 0
    return bucket


def _check(
    grid: FloatArray, pair_ptr: IntArray, pair_lev: IntArray, n_eq: int, n_level: int
) -> None:
    """Validate the inputs: the compiled kernel does no bounds checking."""
    if grid.ndim != 1 or np.any(np.diff(grid) < 0):
        raise ValueError("grid must be a sorted one-dimensional array")
    if pair_ptr.shape != (n_eq + 1,) or pair_ptr[0] != 0 or np.any(np.diff(pair_ptr) < 0):
        raise ValueError("pair_ptr must start at 0, not decrease, and have n_eq + 1 entries")
    if pair_ptr[-1] != pair_lev.size:
        raise ValueError("pair_ptr must end at the number of pairs")
    if pair_lev.size and (np.min(pair_lev) < 0 or np.max(pair_lev) >= n_level):
        raise ValueError("pair_lev holds an index outside the level observations")


def regime_moments(
    z: FloatArray | sparse.spmatrix,
    pair_ptr: IntArray,
    pair_lev: IntArray,
    pair_w: FloatArray,
    w_level: FloatArray,
    q_level: FloatArray,
    grid: FloatArray,
) -> FloatArray:
    """Regime moments ``S[g, j, k]`` for every grid point (see the module docstring).

    Parameters
    ----------
    z
        Instruments of the equation rows, ``(n_eq, L)``, dense or scipy sparse.
    pair_ptr, pair_lev, pair_w
        CSR description of the level observations of each equation row: row ``e`` owns the
        pairs ``pair_ptr[e]:pair_ptr[e + 1]``, each with a level index and a weight.
    w_level
        Regressors at the level observations, ``(n_level, K)``.
    q_level
        Threshold variable at the level observations, ``(n_level,)``.
    grid
        Candidate thresholds in increasing order, ``(G,)``.

    Returns
    -------
    numpy.ndarray
        ``(G, L, K)`` array.
    """
    apply_threads()
    z_csc = sparse.csc_matrix(z, dtype=np.float64)
    z_csc.sort_indices()
    grid_arr = np.ascontiguousarray(grid, dtype=np.float64)
    ptr = np.ascontiguousarray(pair_ptr, dtype=np.int64)
    lev = np.ascontiguousarray(pair_lev, dtype=np.int64)
    w_arr = np.ascontiguousarray(w_level, dtype=np.float64)
    _check(grid_arr, ptr, lev, z_csc.shape[0], w_arr.shape[0])
    if np.shape(q_level) != (w_arr.shape[0],):
        raise ValueError("q_level must have one entry per level observation")
    out = np.zeros((grid_arr.size, z_csc.shape[1], w_arr.shape[1]))
    _regime_moments_kernel(
        z_csc.indptr.astype(np.int64),
        z_csc.indices.astype(np.int64),
        z_csc.data,
        ptr,
        lev,
        np.ascontiguousarray(pair_w, dtype=np.float64),
        pair_buckets(q_level, lev, grid_arr),
        w_arr,
        grid_arr.size,
        out,
    )
    return out
