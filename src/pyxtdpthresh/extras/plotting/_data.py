"""Series the plots read from a fit (no estimation: values the fit already holds)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import BoolArray, FloatArray, IntArray

if TYPE_CHECKING:
    from pyxtdpthresh.models.xtdpthresh.fit import PointFit


def equation_threshold(fit: PointFit) -> tuple[IntArray, IntArray, FloatArray]:
    """Return the unit index, period and threshold variable of each equation."""
    stack = fit.stack
    return stack.unit, stack.time, np.asarray(stack.level_q[stack.current_level], dtype=np.float64)


def upper_regime_flag(fit: PointFit) -> tuple[BoolArray, BoolArray]:
    """Whether each equation is in the upper regime, and whether its threshold value is finite."""
    _, _, q = equation_threshold(fit)
    finite = np.isfinite(q)
    return (q > fit.search.fit.gamma) & finite, finite


def confidence_segments(fit: PointFit) -> FloatArray:
    """Return the accepted runs ``[lower, upper]`` of the threshold confidence set, ``(S, 2)``."""
    ci = fit.bootstrap.ci if fit.bootstrap is not None else None
    if ci is None or ci.segments.size == 0:
        return np.empty((0, 2))
    return np.asarray(np.atleast_2d(ci.segments), dtype=np.float64)[:, :2]


def window(q: FloatArray, gamma: float, trim: float) -> tuple[float, float]:
    """Return the central window of ``q`` (``trim`` cut from each tail) that holds ``gamma``.

    A heavy-tailed threshold variable would squeeze the plot into a corner; the window keeps the
    range readable, and the estimated threshold always stays inside it.
    """
    low, high = (float(v) for v in np.quantile(q[np.isfinite(q)], [trim, 1.0 - trim]))
    return min(low, gamma), max(high, gamma)
