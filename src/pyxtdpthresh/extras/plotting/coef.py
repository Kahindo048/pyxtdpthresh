"""``plot("coef")``: forest plot of the slopes of both regimes and of their change."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import norm

from pyxtdpthresh._types import Lang
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
)

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from pyxtdpthresh.models.xtdpthresh.fit import PointFit

#: Block, colour and offset of the three estimates of a variable on a shared axis.
_SLOTS = (("lower", BLUE, -0.26), ("upper", AQUA, 0.0), ("change", ORANGE, 0.26))
#: Ratio between the widest and the narrowest variable above which scales are freed.
SCALE_RATIO = 5.0

Estimates = dict[str, dict[str, tuple[float, float]]]


def estimates_by_variable(fit: PointFit) -> Estimates:
    """Estimate and standard error of ``lower``, ``upper`` and ``change``, by variable name."""
    theta, cov = fit.search.fit.theta, fit.cov
    se = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    out: Estimates = {}
    for position, name in enumerate(fit.names):
        block, _, variable = name.partition(":")
        out.setdefault(variable, {})[block] = (float(theta[position]), float(se[position]))
    upper = fit.upper
    if upper is not None:
        upper_se = np.sqrt(np.clip(np.diag(upper.cov), 0.0, None))
        for position, name in enumerate(upper.names):
            variable = name.partition(":")[2]
            out.setdefault(variable, {})["upper"] = (
                float(upper.b[position]),
                float(upper_se[position]),
            )
    return out


def _extent(blocks: dict[str, tuple[float, float]], z: float) -> float:
    """Largest distance from zero reached by an interval of the variable."""
    return max(abs(b) + z * se for b, se in blocks.values())


def _interval(ax: Axes, y: float, estimate: tuple[float, float], colour: str, z: float) -> None:
    """Draw one point with its interval at height ``y``."""
    b, se = estimate
    ax.plot([b - z * se, b + z * se], [y, y], color=colour, linewidth=1.0)
    ax.scatter([b], [y], s=16, color=colour, edgecolor="white", linewidth=0.5, zorder=3)


def plot_coef(
    fit: PointFit,
    *,
    variables: Sequence[str] | None = None,
    free_scale: bool | None = None,
    lang: Lang | None = None,
) -> Figure:
    """Estimates and confidence intervals of the lower slope, upper slope and change.

    ``variables`` keeps (and orders) some of the regressors, for example to leave out the time
    effects.  Intervals use the normal quantile of the fit's ``level``.  When the regressors
    are on very different scales a single axis hides the small ones, so each variable then gets
    its own panel and scale; ``free_scale`` forces (``True``) or forbids (``False``) that, and
    the default decides from the ratio of the widest to the narrowest interval.
    """
    chosen = resolve_lang(lang)
    blocks = estimates_by_variable(fit)
    names = [v for v in (variables if variables is not None else blocks) if v in blocks]
    z = float(norm.ppf(0.5 + fit.spec.options.level / 200.0))
    level = fit.spec.options.level
    extents = [_extent(blocks[v], z) for v in names]
    if free_scale is None:
        free_scale = len(names) > 1 and max(extents) > SCALE_RATIO * max(min(extents), 1e-300)
    with chart_style():
        if free_scale:
            fig = _facets(blocks, names, z, level, chosen)
        else:
            fig = _single_axis(blocks, names, z, level, chosen)
        return finish(fig, chosen)


def _single_axis(blocks: Estimates, names: list[str], z: float, level: float, lang: Lang) -> Figure:
    """All the variables on one axis, grouped by variable, with a colour legend."""
    fig, ax = new_figure(height=max(2.6, 0.55 * len(names) + 1.1))
    for row, variable in enumerate(names):
        for block, colour, offset in _SLOTS:
            if block in blocks[variable]:
                _interval(ax, row + offset, blocks[variable][block], colour, z)
    ax.axvline(0.0, color=MUTED, linewidth=0.7, linestyle=":")
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_ylim(len(names) - 0.5, -0.5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel(label("coef_x", lang, level=level))
    handles = [
        ax.scatter([], [], s=16, color=colour, edgecolor="white", linewidth=0.5)
        for _, colour, _ in _SLOTS
    ]
    fig.legend(
        handles,
        [label(key, lang) for key, _, _ in _SLOTS],
        loc="outside upper center",
        ncol=3,
        fontsize=8,
    )
    return fig


def _facets(blocks: Estimates, names: list[str], z: float, level: float, lang: Lang) -> Figure:
    """One panel per variable, each on its own scale, the three estimates one under the other."""
    fig, axes = new_figure(height=max(2.4, 0.95 * len(names) + 0.7), shape=(len(names), 1))
    for ax, variable in zip(np.atleast_1d(axes), names, strict=True):
        present = [slot for slot in _SLOTS if slot[0] in blocks[variable]]
        for row, (block, colour, _) in enumerate(present):
            _interval(ax, row, blocks[variable][block], colour, z)
        ax.axvline(0.0, color=MUTED, linewidth=0.7, linestyle=":")
        ax.set_yticks(range(len(present)))
        ax.set_yticklabels([label(slot[0], lang) for slot in present], fontsize=7.5)
        ax.set_ylim(len(present) - 0.5, -0.5)
        ax.set_title(variable, loc="left", fontsize=9)
        ax.grid(axis="y", visible=False)
    fig.supxlabel(label("coef_x", lang, level=level), fontsize=9)
    return fig
