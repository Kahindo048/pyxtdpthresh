"""Automatic graphs of a fit (matplotlib is imported when a figure is drawn).

``plot(fit, "profile")`` and the other kinds listed in :data:`PLOT_KINDS` return a
``matplotlib.figure.Figure`` drawn in the common style of :mod:`.style`; with ``path`` the
figure is also written as PNG, PDF or SVG.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import Lang

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from pyxtdpthresh.extras.robustness.sensitivity import RobustnessResult
    from pyxtdpthresh.extras.simulation.montecarlo import MonteCarloResult
    from pyxtdpthresh.models.xtdpthresh.fit import PointFit

#: Kinds of graph and what each shows.
PLOT_KINDS: dict[str, str] = {
    "profile": "GMM criterion over the grid of thresholds",
    "ci": "grid-bootstrap statistic against its critical value, accepted set shaded",
    "linearity": "bootstrap distribution of the linearity test",
    "coef": "slopes of both regimes and their change, with intervals",
    "regimes": "distribution of the threshold variable and the share in each regime",
    "effect": "effect of one regressor according to the regime (var=...)",
    "switch": "share of the upper regime by period and units that change regime",
    "instruments": "instrument columns by period against the number of units",
    "residuals": "transformed residuals by period and the AR(1) and AR(2) tests",
    "robustness": "threshold and confidence set of each setting (a RobustnessResult)",
    "coverage": "coverage of the true threshold and slopes (Monte Carlo experiments)",
    "power": "rejection rate of the shifted thresholds (Monte Carlo experiments)",
    "distribution": "distribution of the estimated threshold (Monte Carlo experiments)",
}
#: The kinds that draw Monte Carlo experiments (one ``MonteCarloResult`` or several).
MONTE_CARLO_KINDS: tuple[str, ...] = ("coverage", "power", "distribution")
#: The kinds that draw one fit (every kind but those of a robustness analysis or of experiments).
FIT_KINDS: tuple[str, ...] = tuple(
    k for k in PLOT_KINDS if k != "robustness" and k not in MONTE_CARLO_KINDS
)


def _draw(kind: str) -> Callable[..., Figure]:
    """Return the drawing function of ``kind`` (its module is imported when first used)."""
    from importlib import import_module

    module = import_module(f"pyxtdpthresh.extras.plotting.{kind}")
    return getattr(module, f"plot_{kind}")


def _expected(kind: str) -> str:
    """Name of the kind of object the graph ``kind`` draws."""
    if kind == "robustness":
        return "RobustnessResult"
    return "MonteCarloResult" if kind in MONTE_CARLO_KINDS else "fit"


def _kind_of(result: object) -> str:
    """Name of the kind of object ``result`` is, as :func:`_expected` names them."""
    from collections.abc import Mapping, Sequence

    from pyxtdpthresh.extras.robustness.sensitivity import RobustnessResult
    from pyxtdpthresh.extras.simulation.montecarlo import MonteCarloResult

    if isinstance(result, RobustnessResult):
        return "RobustnessResult"
    if isinstance(result, MonteCarloResult):
        return "MonteCarloResult"
    if isinstance(result, Mapping):
        items = list(result.values())
    elif isinstance(result, Sequence) and not isinstance(result, str):
        items = list(result)
    else:
        return "fit"
    return (
        "MonteCarloResult"
        if items and all(isinstance(i, MonteCarloResult) for i in items)
        else "fit"
    )


def plot(
    fit: PointFit | RobustnessResult | MonteCarloResult | Sequence[MonteCarloResult],
    kind: str,
    *,
    lang: Lang | None = None,
    path: str | Path | None = None,
    **options: Any,
) -> Figure:
    """Draw the graph ``kind`` of ``fit``.

    Parameters
    ----------
    fit
        Result of an ``xtdpthresh`` estimation (a ``RobustnessResult`` for ``"robustness"``; one
        ``MonteCarloResult``, a list of them or a ``{name: result}`` mapping for the kinds
        ``"coverage"``, ``"power"`` and ``"distribution"``).
    kind
        One of :data:`PLOT_KINDS`.
    lang : {"en", "fr"}, optional
        Language of the texts of the figure (default: the global ``lang`` option).
    path
        File to write (``.png``, ``.pdf`` or ``.svg``).
    **options
        Options of the graph (``var`` for ``"effect"``, ``variables`` for ``"coef"``, ``bins`` for
        ``"regimes"``).

    Returns
    -------
    matplotlib.figure.Figure
        The figure; with ``path`` it has also been written to the file.

    Raises
    ------
    SpecificationError
        The kind is unknown, does not fit the object given (``plot_wrong_result``), or is asked
        of an ``xthenreg`` result (``plot_xthenreg``).

    Examples
    --------
    >>> import pyxtdpthresh as pyx
    >>> df = pyx.load_dataset("invest")
    >>> df = df[~df["firm"].isin([137, 391, 407, 488, 538])]
    >>> res = pyx.xtdpthresh(df, "invest", q="debt", endogenous=["cashflow", "tobin_q", "debt"],
    ...                      maxlag=(3, 8), collapse=True, id="firm", time="year", bootstrap=False)
    >>> fig = pyx.plot(res, "profile")
    >>> type(fig).__name__
    'Figure'
    """
    if kind not in PLOT_KINDS:
        raise SpecificationError(
            message("plot_unknown_kind", kind=kind, options=", ".join(PLOT_KINDS)),
            key="plot_unknown_kind",
        )
    if getattr(fit, "is_public_result", False):  # XtdpthreshResult / XthenregResult wrappers
        fit = fit.fit  # type: ignore[union-attr]
    if _kind_of(fit) != _expected(kind):
        raise SpecificationError(
            message("plot_wrong_result", kind=kind, expected=_expected(kind)),
            key="plot_wrong_result",
        )
    from pyxtdpthresh.results.containers import XthenregFit

    if kind in FIT_KINDS and isinstance(fit, XthenregFit):
        raise SpecificationError(message("plot_xthenreg", kind=kind), key="plot_xthenreg")
    fig = _draw(kind)(fit, lang=lang, **options)
    if path is not None:
        from pyxtdpthresh.extras.plotting.style import save_figure

        save_figure(fig, path)
    return fig
