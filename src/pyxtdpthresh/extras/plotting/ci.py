"""``plot("ci")``: statistic of the grid bootstrap against its critical value."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, Lang
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    BLUE,
    GREY,
    MUTED,
    ORANGE,
    chart_style,
    direct_label,
    finish,
    new_figure,
    resolve_lang,
)  # fmt: skip

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.bootstrap import ConfidenceSet
    from pyxtdpthresh.models.xtdpthresh.fit import PointFit

#: Columns of ``ConfidenceSet.table``.
GAMMA, STAT, CRIT, ACCEPT, STATUS = 0, 1, 2, 3, 5
#: Statuses that are a decision (valid draws, or ``D = 0``); the others are unresolved.
DECIDED = (1.0, 2.0)


def confidence_set_of(fit: PointFit, kind: str) -> ConfidenceSet:
    """Return the grid-bootstrap confidence set of ``fit`` (an error if it was not computed)."""
    if fit.bootstrap is None or fit.bootstrap.ci is None:
        raise DataError(message("plot_needs_ci", kind=kind), key="plot_needs_ci")
    return fit.bootstrap.ci


def plot_ci(fit: PointFit, *, lang: Lang | None = None) -> Figure:
    """Distance ``D`` of each candidate, its critical value and the accepted set shaded.

    The equivalent of the likelihood-ratio plot of Hansen (2000) for the grid bootstrap: a
    candidate belongs to the confidence set where ``D`` is under the critical value.  Candidates
    whose test could not be resolved are marked with a cross on the axis.
    """
    chosen = resolve_lang(lang)
    ci = confidence_set_of(fit, "ci")
    table = ci.table
    decided = np.isin(table[:, STATUS], DECIDED)
    accepted = decided & (table[:, ACCEPT] == 1)
    rejected = decided & ~accepted
    gap = np.isfinite(table[:, CRIT]) & decided
    estimate = fit.search.fit.gamma
    with chart_style():
        fig, ax = new_figure(height=3.2)
        for lo, hi in np.atleast_2d(ci.segments) if ci.segments.size else []:
            ax.axvspan(lo, hi, color=BLUE, alpha=0.13, linewidth=0)
        order = np.argsort(table[:, GAMMA])
        sorted_table = table[order]
        keep = np.isin(sorted_table[:, STATUS], DECIDED)
        ax.plot(sorted_table[keep, GAMMA], sorted_table[keep, STAT], color=BLUE, linewidth=1.1)
        ax.scatter(
            table[accepted, GAMMA], table[accepted, STAT], s=14, color=BLUE, edgecolor="white",
            linewidth=0.5, zorder=3,
        )  # fmt: skip
        ax.scatter(
            table[rejected, GAMMA], table[rejected, STAT], s=14, facecolor="white", edgecolor=BLUE,
            linewidth=0.8, zorder=3,
        )  # fmt: skip
        crit_keep = np.isfinite(sorted_table[:, CRIT]) & keep
        ax.plot(
            sorted_table[crit_keep, GAMMA], sorted_table[crit_keep, CRIT], color=MUTED,
            linewidth=0.9, linestyle=":",
        )  # fmt: skip
        ax.axvline(estimate, color=ORANGE, linewidth=0.8)
        unresolved = ~decided & (table[:, STATUS] >= 4)
        if unresolved.any():
            ax.scatter(
                table[unresolved, GAMMA], np.zeros(int(unresolved.sum())), marker="x", s=12,
                color=GREY, linewidth=0.7, clip_on=False, zorder=3,
            )  # fmt: skip
        _annotate(ax, fit, ci, chosen, gap)
        ax.set_xlabel(label("threshold", chosen, q=fit.spec.q))
        ax.set_ylabel(label("distance", chosen))
        ax.set_ylim(bottom=0)
        ax.grid(axis="x", visible=False)
        return finish(fig, chosen)


def _annotate(ax: Axes, fit: PointFit, ci: ConfidenceSet, lang: Lang, gap: BoolArray) -> None:
    """Direct labels: the curves, the confidence set and the estimate."""
    table = ci.table
    decided = np.isin(table[:, STATUS], DECIDED)
    top = float(np.nanmax(table[decided, STAT])) if decided.any() else 1.0
    level = fit.spec.options.level
    right = float(np.nanmax(table[:, GAMMA]))
    if gap.any():
        i = int(np.flatnonzero(gap)[np.argmax(table[gap, GAMMA])])
        direct_label(ax, right, table[i, CRIT], " " + label("ci_critical", lang), va="center")
    estimate = fit.search.fit.gamma
    direct_label(ax, estimate, top, rf" $\hat{{\gamma}}$ = {estimate:.3f}", color=ORANGE, va="top")
    if np.isfinite(ci.lo):
        text = label("ci_set", lang, level=level) + f"\n[{ci.lo:.3f}, {ci.hi:.3f}]"
        ax.text(
            0.995, 0.96, text, transform=ax.transAxes, fontsize=7.5, color=MUTED, va="top",
            ha="right",
        )  # fmt: skip
    ax.set_xlim(right=right + 0.16 * (right - float(np.nanmin(table[:, GAMMA]))))
