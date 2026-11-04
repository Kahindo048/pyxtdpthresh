"""``plot("residuals")``: transformed residuals by period and the serial-correlation tests."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import norm

from pyxtdpthresh._types import FloatArray, IntArray, Lang
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    BLUE,
    MUTED,
    chart_style,
    finish,
    new_figure,
    resolve_lang,
)  # fmt: skip

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.fit import PointFit


def residual_quartiles(fit: PointFit) -> tuple[IntArray, FloatArray]:
    """Periods and the quartiles ``(P, 3)`` of the transformed residuals of each period."""
    stack, fitted = fit.stack, fit.search.fit
    resid = stack.dy - stack.regressors(fitted.gamma) @ fitted.theta
    periods = np.unique(stack.time)
    quartiles = np.array(
        [np.percentile(resid[stack.time == t], [25, 50, 75]) for t in periods]
    ).reshape(periods.size, 3)
    return periods, quartiles


def plot_residuals(fit: PointFit, *, lang: Lang | None = None) -> Figure:
    """Median and quartiles of the transformed residuals by period, and the AR(1)/AR(2) tests.

    Left: the residuals the moments are built on, by period, around zero.  Right: the
    Arellano-Bond statistics with the normal bounds of the fit's level; AR(1) is expected to
    reject in first differences, AR(2) not.
    """
    chosen = resolve_lang(lang)
    periods, quartiles = residual_quartiles(fit)
    serial = fit.serial
    stats = [("AR(1)", serial.ar1), ("AR(2)", serial.ar2)]
    bound = float(norm.ppf(0.5 + fit.spec.options.level / 200.0))
    with chart_style():
        fig, axes = new_figure(height=3.0, shape=(1, 2), gridspec_kw={"width_ratios": [2.2, 1]})
        left, right = axes
        left.fill_between(
            periods, quartiles[:, 0], quartiles[:, 2], color=BLUE, alpha=0.18, linewidth=0
        )
        left.plot(
            periods, quartiles[:, 1], color=BLUE, linewidth=1.2, marker="o", markersize=3.5,
            markeredgecolor="white", markeredgewidth=0.5,
        )  # fmt: skip
        left.axhline(0.0, color=MUTED, linewidth=0.7, linestyle=":")
        left.set_xlabel(label("period", chosen))
        left.set_ylabel(label("residuals", chosen))
        left.text(
            0.01, 0.97, label("residual_band", chosen), transform=left.transAxes, va="top",
            fontsize=7.5, color=MUTED,
        )  # fmt: skip
        left.grid(axis="x", visible=False)
        for k, (_, test) in enumerate(stats):
            if not math.isfinite(test.statistic):
                continue
            right.bar(k, test.statistic, color=BLUE, width=0.55)
            offset = 0.04 * bound if test.statistic >= 0 else -0.04 * bound
            right.text(
                k, test.statistic + offset, label("ar_p", chosen, p=test.p_value), ha="center",
                va="bottom" if test.statistic >= 0 else "top", fontsize=7.5, color=MUTED,
            )  # fmt: skip
        for edge in (-bound, bound):
            right.axhline(edge, color=MUTED, linewidth=0.7, linestyle=":")
        right.axhline(0.0, color=MUTED, linewidth=0.5)
        right.set_xticks(range(len(stats)))
        right.set_xticklabels([name for name, _ in stats])
        right.set_ylabel(label("ar_stat", chosen))
        right.grid(axis="x", visible=False)
        return finish(fig, chosen)
