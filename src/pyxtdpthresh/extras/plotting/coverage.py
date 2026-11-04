"""``plot("coverage")``: coverage of the true threshold and of the true slopes."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting._mc import Experiments, level_of, named
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

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from pyxtdpthresh.extras.simulation.montecarlo import MonteCarloResult

#: Half-width of the Monte Carlo error bars, in standard errors.
BAR = 1.96
#: Vertical offset between the two markers of a row of the threshold panel.
OFFSET = 0.16


def plot_coverage(results: Experiments, *, lang: Lang | None = None) -> Figure:
    """One row per experiment: coverage of the threshold (left) and of the slopes (right).

    The threshold panel shows the coverage of the confidence set read as its accepted segments
    (blue, the strict reading) and as its hull (orange) with ``+/-1.96`` Monte Carlo standard
    errors; the nominal level is dotted.  The slope panel shows the coverage of each slope as a
    grey dot and their mean in blue.
    """
    chosen = resolve_lang(lang)
    runs = named(results, chosen)
    level = level_of([run for _, run in runs])
    with chart_style():
        fig, (left, right) = new_figure(
            height=max(2.6, 0.42 * len(runs) + 1.5), shape=(1, 2), sharey=True,
            gridspec_kw={"width_ratios": [3, 2]},
        )  # fmt: skip
        values: list[float] = []
        for row, (_, run) in enumerate(runs):
            values += _threshold_row(left, row, run, chosen)
            values += _slope_row(right, row, run)
        for ax in (left, right):
            ax.axvline(level / 100.0, color=MUTED, linewidth=0.7, linestyle=":")
            ax.set_xlim(_lower(values, level), 1.02)
            ax.grid(axis="y", visible=False)
        left.set_yticks(range(len(runs)))
        left.set_yticklabels([name for name, _ in runs], fontsize=7.5)
        left.set_ylim(len(runs) - 0.5, -0.5)
        left.set_title(label("mc_threshold", chosen), loc="left")
        right.set_title(label("mc_slopes", chosen), loc="left")
        fig.supxlabel(label("mc_coverage_x", chosen, level=level), fontsize=9)
        _direct_labels(left, right, chosen, level)
        return finish(fig, chosen)


def _lower(values: list[float], level: float) -> float:
    """Left limit of the coverage axes: below every value drawn and the nominal level."""
    finite = [v for v in values if math.isfinite(v)]
    floor = min([*finite, level / 100.0 - 0.05])
    return max(0.0, math.floor((floor - 0.02) * 20.0) / 20.0)


def _threshold_row(ax: Axes, row: int, run: MonteCarloResult, lang: Lang) -> list[float]:
    """Draw the two coverages of the threshold of one experiment; return the values drawn."""
    table = run.threshold_coverage()
    drawn: list[float] = []
    for use, colour, shift in (("segments", BLUE, -OFFSET), ("hull", ORANGE, OFFSET)):
        share, error = float(table.loc[use, "coverage"]), float(table.loc[use, "mcse"])
        if not math.isfinite(share):
            ax.text(
                0.02, row, label("mc_no_coverage", lang), transform=ax.get_yaxis_transform(),
                va="center", fontsize=7.5, color=MUTED,
            )  # fmt: skip
            return drawn
        ax.errorbar(
            share, row + shift, xerr=BAR * error, fmt="o", markersize=4, color=colour,
            markeredgecolor="white", markeredgewidth=0.5, elinewidth=0.8, capsize=0, zorder=3,
        )  # fmt: skip
        drawn += [share - BAR * error]
    return drawn


def _slope_row(ax: Axes, row: int, run: MonteCarloResult) -> list[float]:
    """Draw the coverage of each slope of one experiment (grey) and their mean (blue)."""
    table = run.estimates()
    names = [name for name in table.index if name != "gamma"]
    shares = table.loc[names, "coverage"].to_numpy(dtype=float) if names else np.empty(0)
    shares = shares[np.isfinite(shares)]
    if shares.size == 0:
        return []
    ax.scatter(shares, np.full(shares.size, float(row)), s=10, color=GREY, alpha=0.8, zorder=2)
    ax.scatter(
        [float(np.mean(shares))], [float(row)], s=20, color=BLUE, edgecolor="white",
        linewidth=0.5, zorder=3,
    )  # fmt: skip
    return [float(np.min(shares))]


def _direct_labels(left: Axes, right: Axes, lang: Lang, level: float) -> None:
    for ax, text, colour, x in (
        (left, label("mc_segments", lang), BLUE, 0.02),
        (left, label("mc_hull", lang), ORANGE, 0.2),
        (right, label("mc_slope_mean", lang), BLUE, 0.02),
    ):
        ax.text(x, 0.01, text, transform=ax.transAxes, fontsize=7.5, color=colour, va="bottom")
    left.text(
        0.99, 0.01, label("mc_nominal", lang, level=level), transform=left.transAxes,
        fontsize=7.5, color=MUTED, ha="right", va="bottom",
    )  # fmt: skip
