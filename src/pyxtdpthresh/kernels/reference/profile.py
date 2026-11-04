"""NumPy reference of :func:`pyxtdpthresh.kernels.profile.profile_rows`."""

from __future__ import annotations

import math

import numpy as np

from pyxtdpthresh._types import FloatArray, IntArray


def profile_rows(values: FloatArray, gammas: FloatArray) -> tuple[IntArray, IntArray, FloatArray]:
    """Smallest finite value of each row, one row and one value at a time."""
    table = np.asarray(values, dtype=np.float64)
    best = np.full(table.shape[0], -1, dtype=np.int64)
    count = np.zeros(table.shape[0], dtype=np.int64)
    high = np.full(table.shape[0], np.nan)
    for r in range(table.shape[0]):
        for i in np.flatnonzero(np.isfinite(table[r])):
            value = float(table[r, i])
            count[r] += 1
            if math.isnan(high[r]) or value > high[r]:
                high[r] = value
            if best[r] < 0:
                best[r] = i
                continue
            incumbent = float(table[r, best[r]])
            scale = max(abs(value), abs(incumbent))
            tol = 0.0 if scale == 0.0 else 1e-12 * scale
            if value < incumbent - tol or (
                abs(value - incumbent) <= tol and gammas[i] < gammas[best[r]]
            ):
                best[r] = i
    return best, count, high
