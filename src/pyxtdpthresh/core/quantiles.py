"""Empirical quantiles and equally spaced points with the conventions of the Stata packages.

``xthenreg`` places its threshold grid on quantiles computed by moremata's ``mm_quantile()``
(its default estimator, method 2, "averaged inverse cdf"), while ``xtdpthresh`` uses its own
helper ``xdpt2_quantile`` (Hyndman-Fan type 7, linear interpolation).  The two differ, so
both are provided and each is validated against Stata.
"""

from __future__ import annotations

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import FloatArray


def _sorted_complete(x: FloatArray) -> FloatArray:
    arr = np.asarray(x, dtype=np.float64).ravel()
    return np.sort(arr)


def mm_quantile(x: FloatArray, p: float | FloatArray) -> FloatArray:
    """Quantiles of ``x`` as moremata's ``mm_quantile(x, 1, p)`` (method 2, unweighted).

    With ``n`` observations, ``j`` is the smallest rank with ``j >= p * n``; the quantile is
    ``x_(j)``, or the mean of ``x_(j)`` and ``x_(j+1)`` where ``p * n`` is exactly an integer
    below ``n`` (the empirical cdf is flat there).  Probabilities at or below 0 give the
    minimum, at or above 1 the maximum.

    Parameters
    ----------
    x
        Data without missing values (Mata raises an error on missing values, so does this).
    p
        Probability or array of probabilities.

    Returns
    -------
    numpy.ndarray
        Array of the shape of ``p`` (a 0-d array for a scalar ``p``); NaN if ``x`` is empty.
    """
    # Stata: mm_quantile (moremata), method 2 = default
    xs = _sorted_complete(x)
    if np.isnan(xs).any():
        raise DataError(message("quantile_missing"))
    probs = np.asarray(p, dtype=np.float64)
    n = xs.size
    if n == 0:
        return np.full(probs.shape, np.nan)
    pn = probs * n
    rank = np.clip(np.ceil(pn), 1, n).astype(np.int64)
    lower = xs[rank - 1]
    upper = xs[np.minimum(rank, n - 1)]
    flat = (pn == rank) & (rank < n)
    return np.asarray(np.where(flat, (lower + upper) / 2.0, lower), dtype=np.float64)


def quantile_type7(x: FloatArray, p: float | FloatArray) -> FloatArray:
    """Quantiles of ``x`` as ``xdpt2_quantile`` of xtdpthresh (Hyndman-Fan type 7).

    Missing values are ignored.  ``h = 1 + (n - 1) p`` and linear interpolation between
    ``x_(floor(h))`` and the next order statistic; ``p <= 0`` gives the minimum and
    ``p >= 1`` the maximum.

    Returns
    -------
    numpy.ndarray
        Array of the shape of ``p``; NaN if no non-missing value remains.
    """
    # Stata: xdpt2_quantile (xtdpthresh.ado:4807)
    arr = np.asarray(x, dtype=np.float64).ravel()
    xs = np.sort(arr[~np.isnan(arr)])
    probs = np.asarray(p, dtype=np.float64)
    n = xs.size
    if n == 0:
        return np.full(probs.shape, np.nan)
    h = 1.0 + (n - 1) * probs
    j = np.floor(h)
    g = h - j
    j_idx = np.clip(j, 1, n).astype(np.int64)
    interior = (probs > 0.0) & (probs < 1.0) & (j_idx < n)
    value = (1.0 - g) * xs[j_idx - 1] + g * xs[np.minimum(j_idx, n - 1)]
    out = np.where(interior, value, np.where(probs <= 0.0, xs[0], xs[-1]))
    return np.asarray(out, dtype=np.float64)


def rangen(a: float, b: float, n: int) -> FloatArray:
    """``n`` equally spaced points from ``a`` to ``b``, the last one exactly ``b``.

    ``n <= 1`` gives the single point ``a``.
    """
    # Stata: rangen (Mata built-in) and xdpt2_rangen (xtdpthresh.ado:2480)
    if n <= 1:
        return np.array([a], dtype=np.float64)
    out = a + (b - a) * np.arange(n, dtype=np.float64) / (n - 1)
    out[-1] = b
    return out
