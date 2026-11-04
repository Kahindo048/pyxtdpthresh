"""Extraction of what a table needs from a fitted model (layer 6).

A table does not know the model classes: it reads :class:`ModelColumn` objects, and one extractor
per result type, registered with :func:`register`, builds that object.  Adding a model is adding
an extractor, not touching the table.  Slopes are indexed by ``(block, variable)`` where the block
is ``lower``, ``change`` or ``upper``, so models with different variables line up on their union.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

import numpy as np

from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh.results.containers import XthenregFit

#: Blocks of slopes, in the order they are shown.
BLOCKS = ("lower", "change", "upper")
#: Value of a statistic that a model has no counterpart for.
Statistic = float | str | tuple[float, float] | None
T = TypeVar("T")


@dataclass(frozen=True)
class Estimate:
    """A coefficient and its standard error."""

    b: float
    se: float


@dataclass(frozen=True)
class ModelColumn:
    """What one model contributes to a table.

    Attributes
    ----------
    kind
        ``"xthenreg"`` or ``"xtdpthresh"``.
    dep_var
        Name of the dependent variable.
    coefs
        Estimates by ``(block, variable)``.
    stats
        Diagnostics by key (``n_obs``, ``n_units``, ``n_instruments``, ``hansen_p``, ``ar1_p``,
        ``ar2_p``, ``linearity_p``, ``gamma``, ``gamma_ci``, ``method``, ``shape``,
        ``estimator``); a missing key or a ``None`` value is shown as ``-``.
    gamma_ci_kind
        How the interval of the threshold was built: ``bootstrap`` or ``asymptotic``.
    q
        Name of the threshold variable (empty when unknown).
    """

    kind: str
    dep_var: str
    coefs: dict[tuple[str, str], Estimate]
    stats: dict[str, Statistic] = field(default_factory=dict)
    gamma_ci_kind: str = ""
    q: str = ""


_REGISTRY: dict[type, Callable[[Any], ModelColumn]] = {}


def register(
    result_type: type[T],
) -> Callable[[Callable[[T], ModelColumn]], Callable[[T], ModelColumn]]:
    """Register the function that extracts a :class:`ModelColumn` from ``result_type``."""

    def decorator(function: Callable[[T], ModelColumn]) -> Callable[[T], ModelColumn]:
        _REGISTRY[result_type] = function
        return function

    return decorator


def extract(model: object) -> ModelColumn:
    """Return the :class:`ModelColumn` of a fitted model (a registered result type).

    A public result (``XtdpthreshResult``, ``XthenregResult``) is read through its ``fit``.
    """
    if getattr(model, "is_public_result", False):
        model = model.fit  # type: ignore[attr-defined]
    for result_type, function in _REGISTRY.items():
        if isinstance(model, result_type):
            return function(model)
    raise SpecificationError(
        message("table_unknown_model", kind=type(model).__name__), key="table_unknown_model"
    )


def _se(cov: np.ndarray) -> np.ndarray:
    """Return the standard errors of a covariance matrix (``nan`` where a variance is negative)."""
    diag = np.diag(cov)
    return np.where(diag >= 0, np.sqrt(np.clip(diag, 0.0, None)), np.nan)


def _nan_to_none(value: float) -> float | None:
    return None if value is None or not math.isfinite(value) else float(value)


# ---------------------------------------------------------------------------------- xtdpthresh
def _from_point_fit(fit: Any) -> ModelColumn:
    """Extract an ``xtdpthresh`` fit (:class:`~pyxtdpthresh.models.xtdpthresh.fit.PointFit`)."""
    theta, se = fit.search.fit.theta, _se(fit.cov)
    coefs: dict[tuple[str, str], Estimate] = {}
    for position, name in enumerate(fit.names):
        block, _, variable = name.partition(":")
        coefs[(block, variable)] = Estimate(float(theta[position]), float(se[position]))
    upper = fit.upper
    if upper is not None:
        upper_se = _se(upper.cov)
        for position, name in enumerate(upper.names):
            coefs[("upper", name.partition(":")[2])] = Estimate(
                float(upper.b[position]), float(upper_se[position])
            )
    boot = fit.bootstrap
    ci = boot.ci if boot is not None else None
    interval = (float(ci.lo), float(ci.hi)) if ci is not None and math.isfinite(ci.lo) else None
    test = boot.linearity if boot is not None else None
    options = fit.spec.options
    stats: dict[str, Statistic] = {
        "n_obs": float(fit.n_obs),
        "n_units": float(fit.n_units),
        "n_instruments": float(fit.n_instruments),
        "hansen_p": _nan_to_none(fit.hansen.p_value),
        "ar1_p": _nan_to_none(fit.serial.ar1.p_value),
        "ar2_p": _nan_to_none(fit.serial.ar2.p_value),
        "linearity_p": _nan_to_none(test.p_value) if test is not None else None,
        "gamma": float(fit.search.fit.gamma),
        "gamma_ci": interval,
        "method": options.method.upper(),
        "shape": "kink" if fit.stack.kink else "jump",
        "estimator": "two_step" if fit.search.fit.twostep else "one_step",
    }
    return ModelColumn("xtdpthresh", fit.spec.y, coefs, stats, "bootstrap", fit.spec.q)


# ------------------------------------------------------------------------------------ xthenreg
def _variable(label: str, y_name: str) -> str:
    """Variable named by a Stata coefficient label (``Lag_y`` is the lag of the dependent)."""
    return f"L.{y_name or 'y'}" if label == "Lag_y" else label


def _combine(coef: np.ndarray, cov: np.ndarray, first: int, second: int) -> Estimate:
    """Estimate and standard error of ``coef[first] + coef[second]``."""
    variance = cov[first, first] + cov[second, second] + 2.0 * cov[first, second]
    se = math.sqrt(variance) if variance >= 0 else math.nan
    return Estimate(float(coef[first] + coef[second]), se)


def _from_xthenreg(fit: XthenregFit) -> ModelColumn:
    """Extract an ``xthenreg`` fit (:class:`~pyxtdpthresh.results.containers.XthenregFit`)."""
    labels = fit.names or tuple(f"b{i}" for i in range(fit.coef.size))
    se = _se(fit.cov)
    coefs: dict[tuple[str, str], Estimate] = {}
    position: dict[tuple[str, str], int] = {}
    for index, name in enumerate(labels[:-1]):  # the last entry is the threshold r
        if name == "cons_d":
            key = ("change", "_cons")
        elif name == "kink_slope":
            key = ("change", fit.q_name or "kink_slope")
        else:
            stem, _, suffix = name.rpartition("_")
            key = ("lower" if suffix == "b" else "change", _variable(stem, fit.y_name))
        coefs[key] = Estimate(float(fit.coef[index]), float(se[index]))
        position[key] = index
    for (block, variable), index in position.items():
        partner = position.get(("change", variable))
        if block == "lower" and partner is not None:
            coefs[("upper", variable)] = _combine(fit.coef, fit.cov, index, partner)
    low, high = fit.ci[-1]
    stats: dict[str, Statistic] = {
        "n_units": float(fit.n_units),
        "n_instruments": float(fit.n_moments),
        "linearity_p": fit.boots_p if fit.boots_p >= 0 else None,
        "gamma": float(fit.gamma),
        "gamma_ci": (float(low), float(high)),
        "method": "FD",
        "shape": "kink" if fit.kink else "jump",
    }
    return ModelColumn("xthenreg", fit.y_name, coefs, stats, "asymptotic", fit.q_name)


def register_defaults() -> None:
    """Register the extractors of the package's result types."""
    from pyxtdpthresh.models.xtdpthresh.fit import PointFit

    _REGISTRY[PointFit] = _from_point_fit
    _REGISTRY[XthenregFit] = _from_xthenreg


register_defaults()
