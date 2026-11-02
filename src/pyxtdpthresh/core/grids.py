"""Threshold grids: where the candidate values of gamma are placed and which are admissible."""

from __future__ import annotations

from typing import NamedTuple

import numpy as np

from pyxtdpthresh._errors import DataError, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, GridType
from pyxtdpthresh.core.quantiles import mm_quantile, quantile_type7, rangen

#: Fewest usable values of the threshold variable accepted by ``xtdpthresh``.
MIN_SUPPORT = 20


class ThresholdGrid(NamedTuple):
    """Grid of ``xtdpthresh`` with the bounds and trimming floors that define it."""

    grid: FloatArray
    q_lo: float
    q_hi: float
    min_regime_default: int
    min_regime: int


def xthenreg_grid(q: FloatArray, trim_rate: float, grid_num: int) -> FloatArray:
    """Uniform grid of ``xthenreg``: ``rangen`` between two ``mm_quantile`` trim bounds.

    Parameters
    ----------
    q
        Threshold variable over the estimation sample.
    trim_rate
        Total trimmed share; ``trim_rate / 2`` is cut in each tail.
    grid_num
        Number of grid points.
    """
    # Stata: xthenreg.ado:878-881
    lower = float(mm_quantile(q, trim_rate / 2.0))
    upper = float(mm_quantile(q, 1.0 - trim_rate / 2.0))
    return rangen(lower, upper, grid_num)


def quantile_grid(q: FloatArray, p_lo: float, p_hi: float, n: int) -> FloatArray:
    """``n`` points on the empirical quantiles of ``q`` between two probabilities.

    Duplicate quantiles caused by ties are collapsed, so the grid can have fewer than ``n``
    points; the result is sorted.
    """
    # Stata: xdpt2_quantile_grid (xtdpthresh.ado:2467)
    if n <= 1:
        return np.atleast_1d(quantile_type7(q, p_lo))
    probs = p_lo + (p_hi - p_lo) * np.arange(n, dtype=np.float64) / (n - 1)
    return np.unique(quantile_type7(q, probs))


def min_regime_floor(
    q_support: FloatArray, q_lo: float, q_hi: float, user: int = 0
) -> tuple[int, int]:
    """Smallest number of observations a regime must have at every candidate threshold.

    The default floor is the size of the smaller trimmed tail, ``min(#{q <= q_lo},
    #{q > q_hi})``, and at least 2; ``user`` (``minregime()``) can only raise it.

    Returns
    -------
    tuple of int
        The default floor and the floor applied.
    """
    # Stata: xtdpthresh.ado:8861-8863
    q = np.asarray(q_support, dtype=np.float64)
    default = max(2, int(min(np.sum(q <= q_lo), np.sum(q > q_hi))))
    return default, max(default, int(user))


def threshold_grid(
    q_support: FloatArray,
    trim_rate: float,
    grid_num: int,
    grid_type: GridType = "uniform",
    min_regime: int = 0,
) -> ThresholdGrid:
    """Grid of ``xtdpthresh`` over the effective support of the threshold variable.

    Parameters
    ----------
    q_support
        Values of ``q`` that enter the retained GMM rows (``gridsample``).
    trim_rate
        Total trimmed share; ``trim_rate / 2`` is cut in each tail.
    grid_num
        Number of grid points (before ties are collapsed for a quantile grid).
    grid_type
        ``"uniform"`` (equally spaced between the trim bounds) or ``"quantile"``.
    min_regime
        ``minregime()``: floor on the regime size, applied together with the default floor.

    Raises
    ------
    SpecificationError
        If ``min_regime`` leaves no admissible split.
    DataError
        If the support has too few values or no variation.
    """
    # Stata: xtdpthresh.ado:8829-8879
    q = np.asarray(q_support, dtype=np.float64)
    q = q[~np.isnan(q)]
    if min_regime > 0 and 2 * min_regime > q.size:
        raise SpecificationError(message("minregime_no_split", floor=min_regime, n=q.size))
    if q.size < MIN_SUPPORT:
        raise DataError(message("q_too_few"), stata_code=498)
    q_lo = float(quantile_type7(q, trim_rate / 2.0))
    q_hi = float(quantile_type7(q, 1.0 - trim_rate / 2.0))
    if q_lo >= q_hi:
        raise DataError(message("q_no_variation"), stata_code=498)
    default, applied = min_regime_floor(q, q_lo, q_hi, min_regime)
    if grid_type == "quantile":
        grid = quantile_grid(q, trim_rate / 2.0, 1.0 - trim_rate / 2.0, grid_num)
    else:
        grid = rangen(q_lo, q_hi, grid_num)
    return ThresholdGrid(grid, q_lo, q_hi, default, applied)


def admissible(grid: FloatArray, q_support: FloatArray, min_regime: int) -> BoolArray:
    """Flag the grid points that leave at least ``min_regime`` observations on each side.

    A point ``gamma`` splits the support into ``q <= gamma`` and ``q > gamma``.
    """
    # Stata: xtdpthresh.ado:4507-4508
    q = np.sort(np.asarray(q_support, dtype=np.float64))
    n_low = np.searchsorted(q, np.asarray(grid, dtype=np.float64), side="right")
    return np.asarray((n_low >= min_regime) & (q.size - n_low >= min_regime), dtype=np.bool_)
