"""Smallest value of the criterion profile of many bootstrap draws, in one pass.

The unit bootstrap looks, for every draw, for the threshold with the smallest criterion among
the candidates of the grid.  Done draw by draw in Python this loop was a quarter of the time of
the bootstrap; the kernel scans the whole ``(draws, candidates)`` array at once.  Ties within the
relative tolerance ``1e-12`` go to the smaller threshold, as in ``xdpt2_coef_bootstrap``.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._types import FloatArray, IntArray
from pyxtdpthresh.kernels._jit import njit

#: Relative tolerance under which two criterion values are the same value.
TIE = 1e-12


@njit
def _profile_rows_kernel(
    values: FloatArray, gammas: FloatArray, best: IntArray, count: IntArray, high: FloatArray
) -> None:
    """Fill ``best``, ``count`` and ``high`` for every row of ``values``."""
    for row in range(values.shape[0]):
        top = np.nan
        chosen = -1
        n = 0
        for i in range(values.shape[1]):
            v = values[row, i]
            if not np.isfinite(v):
                continue
            n += 1
            if np.isnan(top) or v > top:
                top = v
            if chosen < 0:
                chosen = i
                continue
            incumbent = values[row, chosen]
            scale = max(abs(v), abs(incumbent))
            tol = 0.0 if scale == 0.0 else TIE * scale
            if v < incumbent - tol or (abs(v - incumbent) <= tol and gammas[i] < gammas[chosen]):
                chosen = i
        best[row] = chosen
        count[row] = n
        high[row] = top


def profile_rows(values: FloatArray, gammas: FloatArray) -> tuple[IntArray, IntArray, FloatArray]:
    """Return the smallest finite value of each row: position, number of finite values, largest.

    Parameters
    ----------
    values
        ``(B, G)`` criterion of each candidate in each draw (``nan`` where not available).
    gammas
        ``(G,)`` threshold of each candidate.

    Returns
    -------
    best, count, high
        Position of the smallest finite value (``-1`` without any), number of finite values and
        the largest one (``nan`` without any), per row.
    """
    table = np.ascontiguousarray(values, dtype=np.float64)
    thresholds = np.ascontiguousarray(gammas, dtype=np.float64)
    if table.ndim != 2 or thresholds.shape != (table.shape[1],):
        raise ValueError("values must be (draws, candidates) and gammas (candidates,)")
    best = np.empty(table.shape[0], dtype=np.int64)
    count = np.empty(table.shape[0], dtype=np.int64)
    high = np.empty(table.shape[0], dtype=np.float64)
    _profile_rows_kernel(table, thresholds, best, count, high)
    return best, count, high
