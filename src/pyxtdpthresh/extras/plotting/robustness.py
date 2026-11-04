"""``plot("robustness")``: the threshold of each setting with its confidence set."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    BLUE,
    GREY,
    MUTED,
    ORANGE,
    chart_style,
    finish,
    new_figure,
    resolve_lang,
)
from pyxtdpthresh.extras.robustness.sensitivity import (
    REFERENCE,
    RobustnessResult,
    accepted_segments,
)

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.fit import PointFit


def plot_robustness(result: RobustnessResult, *, lang: Lang | None = None) -> Figure:
    """One line per setting: ``gamma`` with the hull of its confidence set, the reference first.

    The reference is orange and the other settings blue, as in the other figures.  The accepted
    segments of each run are drawn thick and their hull thin; the confidence set of the reference
    is shaded behind every row and its threshold dotted, so that a setting that leaves the shaded
    area is easy to see.  The stability index is written in the corner.
    """
    chosen = resolve_lang(lang)
    runs = result.runs
    with chart_style():
        fig, ax = new_figure(height=max(2.6, 0.32 * len(runs) + 1.2))
        reference = result.reference
        segments = accepted_segments(reference)
        for low, high in segments if segments is not None else []:
            ax.axvspan(low, high, color=GREY, alpha=0.16, linewidth=0)
        ax.axvline(reference.search.fit.gamma, color=MUTED, linewidth=0.7, linestyle=":")
        for row, run in enumerate(runs):
            colour = ORANGE if run.label == REFERENCE else BLUE
            if run.fit is None:
                ax.text(
                    0.01, row, label("robust_failed", chosen), transform=ax.get_yaxis_transform(),
                    va="center", fontsize=7.5, color=MUTED,
                )  # fmt: skip
                continue
            gamma = run.fit.search.fit.gamma
            _intervals(ax, row, run.fit, colour)
            ax.scatter(
                [gamma], [row], s=16, color=colour, edgecolor="white", linewidth=0.5, zorder=3
            )
        names = [label("reference", chosen) if r.label == REFERENCE else r.label for r in runs]
        ax.set_yticks(range(len(runs)))
        ax.set_yticklabels(names, fontsize=7.5)
        ax.set_ylim(len(runs) - 0.5, -0.5)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel(label("threshold", chosen, q=reference.spec.q))
        index = result.stability()
        if math.isfinite(index):
            ax.text(
                0.99, 0.98, label("robust_stability", chosen, value=index),
                transform=ax.transAxes, ha="right", va="top", fontsize=8, color=MUTED,
            )  # fmt: skip
        return finish(fig, chosen)


def _intervals(ax: Axes, row: int, fit: PointFit, colour: str) -> None:
    """Hull (thin) and accepted segments (thick) of the confidence set of ``fit``."""
    segments = accepted_segments(fit)
    if segments is None:
        return
    hull = [float(np.min(segments[:, 0])), float(np.max(segments[:, 1]))]
    ax.plot(hull, [row, row], color=colour, linewidth=0.7)
    for low, high in segments:
        ax.plot([low, high], [row, row], color=colour, linewidth=2.0, solid_capstyle="butt")
