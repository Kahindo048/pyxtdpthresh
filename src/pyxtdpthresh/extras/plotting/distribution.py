"""``plot("distribution")``: distribution of the estimated threshold over the replications."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting._mc import Experiments, named
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    BLUE,
    MUTED,
    ORANGE,
    chart_style,
    finish,
    new_figure,
    resolve_lang,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure

#: Quantiles drawn: the 5-95 % range (thin), the quartiles (thick) and the median (dot).
RANGE, QUARTILES = (0.05, 0.95), (0.25, 0.75)


def plot_distribution(results: Experiments, *, lang: Lang | None = None) -> Figure:
    """One row per experiment: the 5-95 % range, the quartiles and the median of ``gamma-hat``.

    The true threshold of each experiment is the orange tick of its row.  A threshold estimated
    far from it, or a range that does not shrink with the sample size, shows bias or weak
    identification that coverage alone hides.  Experiments without a threshold effect are named
    and left blank.
    """
    chosen = resolve_lang(lang)
    runs = named(results, chosen)
    with chart_style():
        fig, ax = new_figure(height=max(2.6, 0.34 * len(runs) + 1.4))
        for row, (_, run) in enumerate(runs):
            if not run.design.has_threshold:
                ax.text(
                    0.01, row, label("mc_no_threshold", chosen), transform=ax.get_yaxis_transform(),
                    va="center", fontsize=7.5, color=MUTED,
                )  # fmt: skip
                continue
            gamma = run.ok["gamma"].dropna().to_numpy(dtype=float)
            if gamma.size == 0:
                continue
            low, high = np.quantile(gamma, RANGE)
            q1, q3 = np.quantile(gamma, QUARTILES)
            ax.plot([low, high], [row, row], color=BLUE, linewidth=0.7)
            ax.plot([q1, q3], [row, row], color=BLUE, linewidth=2.6, solid_capstyle="butt")
            ax.scatter(
                [np.median(gamma)], [row], s=16, color=BLUE, edgecolor="white", linewidth=0.5,
                zorder=3,
            )  # fmt: skip
            ax.plot(
                [run.design.gamma] * 2, [row - 0.3, row + 0.3], color=ORANGE, linewidth=1.4,
                zorder=4,
            )  # fmt: skip
        ax.set_yticks(range(len(runs)))
        ax.set_yticklabels([name for name, _ in runs], fontsize=7.5)
        ax.set_ylim(len(runs) - 0.5, -0.5)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel(label("mc_estimate_x", chosen))
        ax.text(
            0.99, 0.01, label("mc_range", chosen) + "; " + label("mc_truth", chosen),
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=MUTED,
        )  # fmt: skip
        return finish(fig, chosen)
