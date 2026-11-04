"""``plot("regimes")``: distribution of the threshold variable around the estimated threshold."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting._data import confidence_segments, equation_threshold, window
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
    BLUE,
    GREY,
    INK,
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


def plot_regimes(
    fit: PointFit, *, bins: int = 30, trim: float = 0.01, lang: Lang | None = None
) -> Figure:
    """Histogram of ``q`` over the equations, split at ``gamma`` with the confidence set shaded.

    The bars below the threshold are blue and those above orange, as in the other figures; the
    share of the equations in each regime is written on each side.  The histogram covers the
    central window of ``q`` (``trim`` cut from each tail, 1 % by default, ``0`` for the whole
    range) and says how many equations fall outside it; the shares count every equation.
    """
    chosen = resolve_lang(lang)
    _, _, q = equation_threshold(fit)
    q = q[np.isfinite(q)]
    gamma = fit.search.fit.gamma
    q_lo, q_hi = window(q, gamma, trim)
    width = (q_hi - q_lo) / bins
    shown = (q >= q_lo) & (q <= q_hi)
    parts = (
        ("regime_lower", BLUE, q[q <= gamma], q[shown & (q <= gamma)], q_lo, gamma, "right"),
        ("regime_upper", ORANGE, q[q > gamma], q[shown & (q > gamma)], gamma, q_hi, "left"),
    )
    with chart_style():
        fig, ax = new_figure(height=3.2)
        for lo, hi in confidence_segments(fit):
            ax.axvspan(lo, hi, color=GREY, alpha=0.16, linewidth=0)
        for _, colour, _, values, start, stop, _ in parts:
            n_bins = max(1, round((stop - start) / width)) if width > 0 else 1
            edges = np.linspace(start, stop, n_bins + 1)
            ax.hist(values, bins=edges, color=colour, alpha=0.85, edgecolor="white", linewidth=0.5)
        ax.axvline(gamma, color=INK, linewidth=0.9, linestyle="--")
        ax.set_ylim(0, ax.get_ylim()[1] * 1.12)
        for key, colour, values, _, _, _, align in parts:
            text = label(key, chosen, n=values.size, share=100.0 * values.size / q.size)
            shift = (-0.01 if align == "right" else 0.01) * (q_hi - q_lo)
            ax.text(
                gamma + shift, 0.96, text, transform=ax.get_xaxis_transform(), ha=align,
                va="top", fontsize=8, color=colour,
            )  # fmt: skip
        if not shown.all():
            text = label("outside", chosen, n=int(np.sum(~shown)))
            ax.text(
                0.99, 0.97, text, transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
                color=MUTED,
            )  # fmt: skip
        ax.set_xlim(q_lo, q_hi)
        ax.set_xlabel(fit.spec.q)
        ax.set_ylabel(label("observations", chosen))
        ax.grid(axis="x", visible=False)
        return finish(fig, chosen)
