"""``plot("effect")``: effect of a regressor as a function of the threshold variable."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import norm

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting._data import confidence_segments, equation_threshold, window
from pyxtdpthresh.extras.plotting.coef import estimates_by_variable
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
)  # fmt: skip

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.fit import PointFit


def regressors_with_slope(fit: PointFit) -> list[str]:
    """Names of the regressors that have a slope (the intercept shift has none)."""
    return [v for v, blocks in estimates_by_variable(fit).items() if "lower" in blocks]


def plot_effect(
    fit: PointFit, *, var: str | None = None, trim: float = 0.01, lang: Lang | None = None
) -> Figure:
    """Effect of ``var`` on the dependent variable according to the regime of ``q``.

    Jump model: a staircase, the lower slope up to the threshold and the upper slope above it,
    each with its confidence band.  Kink model: the slope of the threshold variable changes at
    ``gamma``, so the contribution ``b (q - gamma) + delta (q - gamma)+`` is drawn as a broken
    line (zero at the threshold) with its delta-method band; any other regressor has a constant
    slope.  The horizontal range is the central window of ``q`` (``trim`` cut from each tail,
    ``0`` for the whole range).
    """
    chosen = resolve_lang(lang)
    options = regressors_with_slope(fit)
    if var is None:
        raise SpecificationError(
            message("plot_no_variable", options=", ".join(options)), key="plot_no_variable"
        )
    if var not in options:
        raise SpecificationError(
            message("plot_unknown_variable", name=var, options=", ".join(options)),
            key="plot_unknown_variable",
        )
    z = float(norm.ppf(0.5 + fit.spec.options.level / 200.0))
    _, _, q = equation_threshold(fit)
    span = window(q, fit.search.fit.gamma, trim)
    with chart_style():
        fig, ax = new_figure(height=3.2)
        for lo, hi in confidence_segments(fit):
            ax.axvspan(lo, hi, color=GREY, alpha=0.16, linewidth=0)
        if fit.stack.kink and var == fit.spec.q:
            _kink_line(ax, fit, var, span, z)
            ylabel = label("contribution", chosen, var=var)
        else:
            _steps(ax, fit, var, span, z)
            ylabel = label("effect", chosen, var=var)
        ax.axvline(fit.search.fit.gamma, color=MUTED, linewidth=0.7, linestyle=":")
        ax.axhline(0.0, color=MUTED, linewidth=0.5)
        ax.set_xlim(*span)
        ax.set_xlabel(fit.spec.q)
        ax.set_ylabel(ylabel)
        ax.grid(axis="x", visible=False)
        return finish(fig, chosen)


def _steps(ax: Axes, fit: PointFit, var: str, span: tuple[float, float], z: float) -> None:
    """Staircase of the slope of ``var`` below and above the threshold (constant under kink)."""
    blocks = estimates_by_variable(fit)[var]
    gamma = fit.search.fit.gamma
    if fit.stack.kink:
        pieces = [("lower", BLUE, span[0], span[1])]
    else:
        pieces = [("lower", BLUE, span[0], gamma), ("upper", ORANGE, gamma, span[1])]
    for block, colour, start, stop in pieces:
        if block not in blocks:
            continue
        b, se = blocks[block]
        ax.fill_between(
            [start, stop], b - z * se, b + z * se, color=colour, alpha=0.15, linewidth=0
        )
        ax.hlines(b, start, stop, color=colour, linewidth=1.8)


def _kink_line(ax: Axes, fit: PointFit, var: str, span: tuple[float, float], z: float) -> None:
    """Broken line of the contribution of the threshold variable with its delta-method band."""
    theta, cov = fit.search.fit.theta, fit.cov
    slope = fit.names.index(f"lower:{var}")
    last = theta.size - 1
    gamma = fit.search.fit.gamma
    grid = np.unique(np.concatenate([np.linspace(span[0], span[1], 200), [gamma]]))
    below, above = grid - gamma, np.maximum(grid - gamma, 0.0)
    value = theta[slope] * below + theta[last] * above
    sub = cov[np.ix_([slope, last], [slope, last])]
    gradient = np.column_stack([below, above])
    se = np.sqrt(np.clip(np.einsum("gi,ij,gj->g", gradient, sub, gradient), 0.0, None))
    ax.fill_between(grid, value - z * se, value + z * se, color=BLUE, alpha=0.15, linewidth=0)
    ax.plot(grid, value, color=BLUE, linewidth=1.8)
