"""``plot("power")``: rejection rate of the thresholds ``gamma + c`` by the confidence set."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting._mc import Experiments, level_of, named
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    AQUA,
    BLUE,
    GREY,
    MUTED,
    ORANGE,
    chart_style,
    finish,
    new_figure,
    resolve_lang,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure

#: Colours of the experiments, in order (the palette of the other figures).
COLOURS = (BLUE, ORANGE, AQUA, GREY, MUTED)


#: Smallest vertical distance between two names at the end of the lines (rejection-rate units).
LABEL_GAP = 0.05


def _spread(ends: list[tuple[float, float, str, str]]) -> list[tuple[float, float, str, str]]:
    """Move the names that would overlap upward so that each is ``LABEL_GAP`` above the last."""
    placed: list[tuple[float, float, str, str]] = []
    floor = -math.inf
    for x, y, name, colour in sorted(ends, key=lambda end: end[1]):
        floor = max(y, floor + LABEL_GAP)
        placed.append((x, floor, name, colour))
    return placed


def plot_power(results: Experiments, *, lang: Lang | None = None) -> Figure:
    """Rejection rate against the shift ``c`` of the tested threshold, one line per experiment.

    At ``c = 0`` the rate is the size of the test of the true threshold, which should sit at the
    nominal level (dotted); it grows with ``c`` as the confidence set excludes the shifted
    threshold.  Each line is named at its right end instead of in a legend.  Experiments without a
    threshold effect have no true threshold to shift and are left out.
    """
    chosen = resolve_lang(lang)
    runs = [(name, run) for name, run in named(results, chosen) if run.design.has_threshold]
    level = level_of([run for _, run in runs]) if runs else 95.0
    with chart_style():
        fig, ax = new_figure(height=3.2)
        ax.axhline(1.0 - level / 100.0, color=MUTED, linewidth=0.7, linestyle=":")
        ax.text(
            0.99, 1.0 - level / 100.0, label("mc_level", chosen, alpha=1.0 - level / 100.0),
            transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=7.5, color=MUTED,
        )  # fmt: skip
        right = 0.0
        ends: list[tuple[float, float, str, str]] = []
        for index, (name, run) in enumerate(runs):
            power = run.power()
            x = power.index.to_numpy(dtype=float)
            y = power["rejection"].to_numpy(dtype=float)
            colour = COLOURS[index % len(COLOURS)]
            ax.plot(x, y, color=colour, linewidth=1.2, marker="o", markersize=3.5, zorder=3)
            finite = np.isfinite(y)
            if finite.any():
                last = int(np.flatnonzero(finite)[-1])
                ends.append((float(x[last]), float(y[last]), name, colour))
            right = max(right, float(np.max(x)) if x.size else 0.0)
        for x_end, y_label, name, colour in _spread(ends):
            ax.text(x_end + 0.01, y_label, name, color=colour, fontsize=7.5, va="center", ha="left")
        ax.set_xlim(-0.02, right * 1.6 if right > 0 else 1.0)
        ax.set_ylim(-0.02, 1.02)
        ax.set_xlabel(label("mc_shift_x", chosen))
        ax.set_ylabel(label("mc_rejection_y", chosen))
        ax.grid(axis="x", visible=False)
        return finish(fig, chosen)
