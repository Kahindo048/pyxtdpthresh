"""Threshold grids and quantiles with Stata/moremata conventions."""

from __future__ import annotations

import numpy as np


def mm_quantile(x: np.ndarray, p: float, definition: int = 2) -> float:
    """Quantile as moremata's ``mm_quantile(x, 1, p, def)``.

    ``definition=2`` (moremata's default) averages at discontinuities, which is
    numpy's ``averaged_inverted_cdf``.  The other definitions are the usual
    inverted-cdf (1) and nearest-rank (0, 3) variants.
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    methods = {
        0: "inverted_cdf",
        1: "inverted_cdf",
        2: "averaged_inverted_cdf",
        3: "closest_observation",
    }
    return float(np.quantile(x, p, method=methods[definition]))


def rangen(a: float, b: float, n: int) -> np.ndarray:
    """Mata ``rangen(a, b, n)``: ``n`` equally spaced points from ``a`` to ``b``."""
    if n <= 1:
        return np.array([a], dtype=float)
    out = a + (b - a) * np.arange(n) / (n - 1)
    out[-1] = b
    return out
