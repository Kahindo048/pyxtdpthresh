"""``plot("profile")``: the GMM criterion over the grid of thresholds."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import chi2

from pyxtdpthresh._types import FloatArray, Lang
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

#: A profile is flat when at least this share of the thresholds is within ``FLAT_GAP`` of the
#: minimum.
FLAT_SHARE = 0.5
#: Gap to the minimum, in units of the criterion: the 95 % point of a chi-square with one degree
#: of freedom, the cost of fixing one parameter.
FLAT_GAP = float(chi2.ppf(0.95, 1))


def flatness(values: FloatArray, *, gap: float = FLAT_GAP) -> tuple[float, bool]:
    """Share of the admitted thresholds within ``gap`` of the minimum, and whether it is flat.

    ``values`` is the criterion at each threshold (``nan`` where it is not defined).  The
    criterion is on the chi-square scale (``J = n g'Wg``), so ``gap`` is read as the loss of fit
    that one fixed parameter costs; a profile where half of the grid is that close to the
    minimum identifies the threshold poorly.
    """
    ok = values[np.isfinite(values)]
    if ok.size == 0:
        return float("nan"), False
    share = float(np.mean(ok <= np.min(ok) + gap))
    return share, share >= FLAT_SHARE


def plot_profile(fit: PointFit, *, lang: Lang | None = None) -> Figure:
    """Criterion ``J(gamma)`` over the initial grid with the estimate marked.

    A flat profile (see :func:`flatness`) adds a note under the curve.
    """
    chosen = resolve_lang(lang)
    gammas, values = fit.search.profile()
    ok = np.isfinite(values)
    estimate, objective = fit.search.fit.gamma, fit.search.fit.obj
    with chart_style():
        fig, ax = new_figure(height=3.2)
        ax.plot(
            gammas[ok], values[ok], color=BLUE, linewidth=1.2, marker="o", markersize=3.2,
            markeredgecolor="white", markeredgewidth=0.5,
        )  # fmt: skip
        ax.axvline(estimate, color=MUTED, linewidth=0.7, linestyle=":")
        ax.scatter([estimate], [objective], s=26, color=ORANGE, edgecolor="white", zorder=4)
        top = float(np.nanmax(values)) if ok.any() else objective
        direct_label(
            ax, estimate, top, rf" $\hat{{\gamma}}$ = {estimate:.3f}", color=ORANGE, va="top"
        )
        share, flat = flatness(values)
        if flat:
            text = label("profile_flat", chosen, share=100 * share, gap=FLAT_GAP)
            ax.text(0.01, 0.02, text, transform=ax.transAxes, fontsize=7.5, color=MUTED)
        ax.set_xlabel(label("threshold", chosen, q=fit.spec.q))
        ax.set_ylabel(label("criterion", chosen))
        ax.grid(axis="x", visible=False)
        return finish(fig, chosen)
