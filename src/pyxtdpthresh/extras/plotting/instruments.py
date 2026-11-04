"""``plot("instruments")``: instrument columns available in each period, against N."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import IntArray, Lang
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    BLUE,
    MUTED,
    ORANGE,
    chart_style,
    direct_label,
    finish,
    new_figure,
    resolve_lang,
)  # fmt: skip

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.fit import PointFit


def instruments_by_period(fit: PointFit) -> tuple[IntArray, IntArray]:
    """Periods of the equations and, for each, the instrument columns that are not all zero."""
    stack = fit.stack
    csr = stack.z.csr
    periods = np.unique(stack.time)
    counts = np.empty(periods.size, dtype=np.int64)
    for i, period in enumerate(periods):
        block = csr[np.flatnonzero(stack.time == period)]
        counts[i] = int(np.sum(np.asarray((block != 0).sum(axis=0)).ravel() > 0))
    return periods, counts


def plot_instruments(fit: PointFit, *, lang: Lang | None = None) -> Figure:
    """Instrument columns used by the equations of each period, with the number of units.

    The instrument count is the usual warning sign of weak Hansen tests: when it approaches or
    exceeds the number of units the over-identification test loses its power.
    """
    chosen = resolve_lang(lang)
    periods, counts = instruments_by_period(fit)
    n_units = fit.n_units
    with chart_style():
        fig, ax = new_figure(height=3.0)
        ax.bar(periods, counts, color=BLUE, width=0.7)
        for period, count in zip(periods, counts, strict=True):
            direct_label(ax, float(period), float(count), str(count), ha="center")
        ax.axhline(n_units, color=ORANGE, linewidth=0.9, linestyle="--")
        direct_label(
            ax, float(np.min(periods)), n_units, label("instruments_n", chosen, n=n_units),
            color=ORANGE, va="bottom",
        )  # fmt: skip
        total = f"{fit.n_instruments}"
        ax.text(
            0.99, 0.96, f"{label('instruments', chosen)}: {total}", transform=ax.transAxes,
            ha="right", va="top", fontsize=8, color=MUTED,
        )  # fmt: skip
        ax.set_ylim(0, max(float(np.max(counts)), float(n_units)) * 1.15)
        ax.set_xlabel(label("period", chosen))
        ax.set_ylabel(label("instruments", chosen))
        ax.grid(axis="x", visible=False)
        return finish(fig, chosen)
