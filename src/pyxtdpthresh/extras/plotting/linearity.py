"""``plot("linearity")``: bootstrap distribution of the linearity test."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.plotting.style import (
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


def plot_linearity(fit: PointFit, *, lang: Lang | None = None) -> Figure:
    """Histogram of the bootstrap distances ``D*`` with the observed ``D`` and the p-value."""
    chosen = resolve_lang(lang)
    test = fit.bootstrap.linearity if fit.bootstrap is not None else None
    if test is None:
        raise DataError(message("plot_needs_linearity"), key="plot_needs_linearity")
    if not math.isfinite(test.statistic) or test.draws.size == 0:
        raise DataError(message("plot_linearity_undefined"), key="plot_linearity_undefined")
    draws = test.draws
    with chart_style():
        fig, ax = new_figure(height=3.0)
        upper = max(float(np.max(draws)), test.statistic)
        bins = np.linspace(0.0, upper * 1.02, min(40, max(10, draws.size // 5)) + 1)
        ax.hist(draws, bins=bins, color=BLUE, alpha=0.85, edgecolor="white", linewidth=0.5)
        ax.axvline(test.statistic, color=ORANGE, linewidth=1.2)
        text = label("lin_obs", chosen, d=test.statistic)
        text += "\n" + (
            label("lin_p", chosen, p=test.p_value)
            if math.isfinite(test.p_value)
            else label("lin_p_missing", chosen)
        )
        side_right = test.statistic < 0.7 * upper
        ax.text(
            test.statistic + (0.01 if side_right else -0.01) * upper, 0.95, text,
            transform=ax.get_xaxis_transform(), ha="left" if side_right else "right",
            va="top", fontsize=8, color=ORANGE,
        )  # fmt: skip
        ax.set_xlim(0, upper * 1.02)
        ax.set_xlabel(label("lin_x", chosen))
        ax.set_ylabel(label("lin_y", chosen))
        ax.grid(axis="x", visible=False)
        ax.spines["left"].set_color(MUTED)
        return finish(fig, chosen)
