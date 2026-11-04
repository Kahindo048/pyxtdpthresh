"""``plot("switch")``: how the units move between the regimes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from matplotlib.ticker import MaxNLocator

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting._data import equation_threshold, upper_regime_flag
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    AQUA,
    BLUE,
    MUTED,
    ORANGE,
    chart_style,
    finish,
    new_figure,
    resolve_lang,
)  # fmt: skip

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.fit import PointFit


def regime_paths(fit: PointFit) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Periods, share of equations in the upper regime by period, and the unit counts.

    The counts are the units always in the lower regime, always in the upper regime, and those
    that move between the two across their equations.
    """
    unit, time, _ = equation_threshold(fit)
    upper, finite = upper_regime_flag(fit)
    periods = np.unique(time[finite])
    share = np.array([upper[finite & (time == t)].mean() for t in periods])
    n_units = int(np.max(unit)) + 1 if unit.size else 0
    has_upper = np.bincount(unit[finite & upper], minlength=n_units) > 0
    has_lower = np.bincount(unit[finite & ~upper], minlength=n_units) > 0
    counts = np.array(
        [
            int(np.sum(has_lower & ~has_upper)),
            int(np.sum(has_upper & ~has_lower)),
            int(np.sum(has_lower & has_upper)),
        ]
    )
    return periods, share, counts


def plot_switch(fit: PointFit, *, lang: Lang | None = None) -> Figure:
    """Share of the equations in the upper regime by period, and units that change regime."""
    chosen = resolve_lang(lang)
    periods, share, counts = regime_paths(fit)
    with chart_style():
        fig, axes = new_figure(height=3.0, shape=(1, 2), gridspec_kw={"width_ratios": [2.2, 1]})
        line, bars = axes
        line.plot(
            periods, 100 * share, color=BLUE, linewidth=1.2, marker="o", markersize=3.5,
            markeredgecolor="white", markeredgewidth=0.5,
        )  # fmt: skip
        line.set_ylim(0, 100)
        line.set_xlabel(label("period", chosen))
        line.set_ylabel(label("switch_share", chosen))
        line.xaxis.set_major_locator(MaxNLocator(integer=True))
        line.grid(axis="x", visible=False)
        names = [label(k, chosen) for k in ("always_lower", "always_upper", "switching")]
        colours = [BLUE, ORANGE, AQUA]
        y = np.arange(3)
        bars.barh(y, counts, color=colours, height=0.6)
        for row, count in enumerate(counts):
            bars.text(count, row, f" {count}", va="center", fontsize=8, color=MUTED)
        bars.set_yticks(y)
        bars.set_yticklabels(names)
        bars.invert_yaxis()
        bars.set_xlim(0, max(float(np.max(counts)), 1.0) * 1.2)
        bars.set_xlabel(label("units", chosen))
        bars.grid(axis="y", visible=False)
        return finish(fig, chosen)
