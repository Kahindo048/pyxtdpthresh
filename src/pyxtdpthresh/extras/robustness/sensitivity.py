"""Automatic sensitivity of the threshold to the settings of the estimation (layer 6).

``robustness(frame, y, x, q=..., settings=...)`` re-estimates the model on a set of settings (grid
size, trimming, instrument lags, collapsing, first differences or forward deviations, jump or
kink) and gathers what moves: the threshold with its confidence set, the slopes, the linearity
p-value and the diagnostics.  Settings are varied **one at a time** around the reference by
default (each run differs from the reference by one option); ``product=True`` runs every
combination.  Nothing here estimates in a new way: each run is a call to the validated
estimator, and every run shares one bootstrap seed so that the settings, not the draws, explain
the differences.
"""

from __future__ import annotations

import itertools
import math
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import PyxdpthreshError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BoolArray, FloatArray, Lang
from pyxtdpthresh.extras.reporting.extract import extract
from pyxtdpthresh.models.xtdpthresh.fit import PointFit, fit_point
from pyxtdpthresh.models.xtdpthresh.options import XtdpthreshOptions

#: Label of the run that every other setting is compared with.
REFERENCE = "reference"
#: Settings tried when the caller gives none: each is one option and the values to try.
DEFAULT_SETTINGS: dict[str, Sequence[Any]] = {
    "grid": (50, 100, 200),
    "trim": (0.05, 0.10, 0.15),
    "collapse": (True, False),
    "method": ("fd", "fod"),
    "kink": (False, True),
}
#: Columns of the diagnostics of the table, with the scalar each one reads.
_SCALARS = {
    "n_obs": "N",
    "n_units": "N_units",
    "n_instruments": "N_iv",
    "hansen_p": "hansen_p",
    "ar2_p": "ar2_p",
    "pval_lin": "pval_lin",
}


@dataclass(frozen=True)
class SettingRun:
    """One estimation of the analysis.

    Attributes
    ----------
    label
        Name of the run (``reference``, ``trim=0.05``, ``collapse=False, method=fod``).
    changes
        Options this run changes with respect to the reference.
    fit
        The fit, or ``None`` when the estimation failed.
    error, key
        Message and key of the error of a failed run (empty otherwise).
    """

    label: str
    changes: Mapping[str, Any]
    fit: PointFit | None
    error: str = ""
    key: str | None = None


def _label(changes: Mapping[str, Any]) -> str:
    return ", ".join(f"{k}={v}" for k, v in changes.items()) or REFERENCE


def _validated(settings: Mapping[str, Sequence[Any]]) -> dict[str, Sequence[Any]]:
    """Check the setting names against the options of the estimator."""
    known = {f.name for f in fields(XtdpthreshOptions)}
    for name, values in settings.items():
        if name not in known:
            raise SpecificationError(
                message("robust_unknown_setting", name=name, options=", ".join(sorted(known))),
                key="robust_unknown_setting",
            )
        if isinstance(values, str) or not isinstance(values, Sequence) or len(values) == 0:
            raise SpecificationError(
                message("robust_empty_setting", name=name), key="robust_empty_setting"
            )
    return dict(settings)


def _plan(
    settings: Mapping[str, Sequence[Any]], base: Mapping[str, Any], *, product: bool
) -> list[dict[str, Any]]:
    """Return the changes of each run (without the reference), dropping repeats of the base."""
    defaults = {f.name: f.default for f in fields(XtdpthreshOptions)}
    current = {name: base.get(name, defaults[name]) for name in settings}
    if product:
        names = list(settings)
        runs = [
            dict(zip(names, combo, strict=True)) for combo in itertools.product(*settings.values())
        ]
    else:
        runs = [{name: value} for name, values in settings.items() for value in values]
    kept: list[dict[str, Any]] = []
    for changes in runs:
        if all(current[name] == value for name, value in changes.items()):
            continue  # that is the reference itself
        if changes not in kept:
            kept.append(changes)
    return kept


def _fit(frame: pd.DataFrame, y: str, x: Any, arguments: Mapping[str, Any]) -> PointFit:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(frame, y, x, **arguments)


def _run(
    frame: pd.DataFrame, y: str, x: Any, base: Mapping[str, Any], changes: Mapping[str, Any]
) -> SettingRun:
    """Estimate one variation; a failure is recorded, not raised."""
    try:
        return SettingRun(_label(changes), changes, _fit(frame, y, x, {**base, **changes}))
    except PyxdpthreshError as error:
        return SettingRun(_label(changes), changes, None, str(error), error.key)


def robustness(
    frame: pd.DataFrame,
    y: str,
    x: Sequence[str] | str = (),
    *,
    q: str,
    id: str | None = None,
    time: str | None = None,
    settings: Mapping[str, Sequence[Any]] | None = None,
    product: bool = False,
    **options: Any,
) -> RobustnessResult:
    """Re-estimate ``xtdpthresh`` over a set of settings and compare the threshold.

    Parameters
    ----------
    frame, y, x, q, id, time
        Data and variables, as for the estimator.
    settings
        Options to vary, each with the values to try: ``{"grid": [50, 100], "collapse": [True,
        False]}``.  The default varies the grid, the trimming, ``collapse``, ``method`` and
        ``kink``.  A value equal to the one of the reference is skipped.
    product
        Run every combination of the values instead of one option at a time.
    **options
        Options of the reference estimation (``collapse=True``, ``maxlag=(2, 4)``...).  The
        bootstraps are on, since the confidence set and the linearity test are what is compared;
        ``seed`` fixes their draws (a seed is drawn and recorded when omitted).

    Returns
    -------
    RobustnessResult
        The runs, the comparison table, the slopes, the stability index and the graph.

    Raises
    ------
    SpecificationError
        If a setting is not an option of the estimator or has no values.
    PyxdpthreshError
        If the reference estimation itself fails (a failed variation is only recorded).
    """
    chosen = _validated(DEFAULT_SETTINGS if settings is None else settings)
    seed = options.pop("seed", None)
    if seed is None:
        seed = int(np.random.default_rng().integers(1, 2**31 - 1))
    base = {"q": q, "id": id, "time": time, "seed": seed, "bootstrap": True, **options}
    runs = [SettingRun(REFERENCE, {}, _fit(frame, y, x, base))]
    runs += [_run(frame, y, x, base, changes) for changes in _plan(chosen, base, product=product)]
    return RobustnessResult(tuple(runs), seed)


@dataclass(frozen=True)
class RobustnessResult:
    """Outcome of :func:`robustness`: the runs and what they say about the threshold.

    Attributes
    ----------
    runs
        Every run, the reference first.
    seed
        Bootstrap seed shared by all the runs.
    """

    runs: tuple[SettingRun, ...]
    seed: int

    @property
    def reference(self) -> PointFit:
        """The reference fit."""
        assert self.runs[0].fit is not None
        return self.runs[0].fit

    @property
    def fits(self) -> dict[str, PointFit]:
        """The successful fits by label, the reference first."""
        return {run.label: run.fit for run in self.runs if run.fit is not None}

    # ----------------------------------------------------------------------------- the table
    @cached_property
    def table(self) -> pd.DataFrame:
        """One row per run: threshold, its confidence set, slopes, tests and diagnostics.

        ``gamma_lo`` and ``gamma_hi`` are the hull of the confidence set and ``ci_nseg`` its number
        of segments; ``in_reference_ci`` tells whether the threshold of the run is inside the
        confidence set of the reference.  The lower and upper slopes follow as ``lower:x`` and
        ``upper:x``.  A failed run has ``status`` ``failed`` and its message in ``error``.
        """
        reference = self.runs[0].fit
        assert reference is not None
        rows = []
        for run in self.runs:
            row: dict[str, Any] = {
                "setting": run.label,
                "status": "ok" if run.fit is not None else "failed",
                "error": run.error,
            }
            if run.fit is not None:
                row.update(self._row(run.fit, reference))
            rows.append(row)
        frame = pd.DataFrame(rows).set_index("setting")
        frame["in_reference_ci"] = frame["in_reference_ci"].astype("boolean")
        return frame

    @staticmethod
    def _row(fit: PointFit, reference: PointFit) -> dict[str, Any]:
        scalars = fit.scalars
        column = extract(fit)
        row: dict[str, Any] = {
            "shape": "kink" if fit.stack.kink else "jump",
            "method": fit.spec.options.method,
            "gamma": scalars["gamma"],
            "gamma_lo": scalars["gamma_lo"],
            "gamma_hi": scalars["gamma_hi"],
            "ci_nseg": scalars["ci_nseg"],
            "in_reference_ci": _inside(scalars["gamma"], reference),
        }
        row.update({name: scalars[key] for name, key in _SCALARS.items()})
        for (block, variable), estimate in column.coefs.items():
            if block in ("lower", "upper"):
                row[f"{block}:{variable}"] = estimate.b
        return row

    def to_dataframe(self) -> pd.DataFrame:
        """Return the comparison table (see :attr:`table`)."""
        return self.table.copy()

    def coefficients(self) -> pd.DataFrame:
        """Return every slope of every successful run, with its standard error.

        Indexed by ``(setting, block, variable)`` with ``estimate`` and ``se``; the blocks are
        ``lower``, ``change`` and ``upper``.
        """
        records = []
        for label, fit in self.fits.items():
            for (block, variable), estimate in extract(fit).coefs.items():
                records.append((label, block, variable, estimate.b, estimate.se))
        frame = pd.DataFrame(records, columns=["setting", "block", "variable", "estimate", "se"])
        return frame.set_index(["setting", "block", "variable"])

    # ------------------------------------------------------------------------ stability index
    def stability(self, use: str = "segments") -> float:
        """Return the share of the other runs whose threshold stays in the reference interval.

        The reference interval is the confidence set of the reference: the union of its accepted
        segments (``use="segments"``, the default) or their hull (``use="hull"``).  Failed runs
        are not counted; the result is ``nan`` when the reference has no complete confidence set
        or there is no other successful run.
        """
        if use not in ("segments", "hull"):
            raise SpecificationError(
                message("robust_stability_use", value=use), key="robust_stability_use"
            )
        reference = self.reference
        others = [f for label, f in self.fits.items() if label != REFERENCE]
        if not others:
            return math.nan
        inside = [_inside(f.search.fit.gamma, reference, use) for f in others]
        if any(v is None for v in inside):
            return math.nan
        return sum(bool(v) for v in inside) / len(inside)

    # ------------------------------------------------------------------------------ outputs
    def plot(self, lang: Lang | None = None, path: str | Path | None = None) -> Any:
        """Draw the thresholds of the runs with their confidence sets; return the figure."""
        from pyxtdpthresh.extras.plotting import plot

        return plot(self, "robustness", lang=lang, path=path)

    def stargazer(self, **options: Any) -> Any:
        """Return a :class:`~pyxtdpthresh.extras.reporting.ThresholdStargazer` of the fits."""
        from pyxtdpthresh.extras.reporting import ThresholdStargazer

        fits = self.fits
        options.setdefault("model_names", list(fits))
        return ThresholdStargazer(list(fits.values()), **options)


def accepted_segments(fit: PointFit) -> FloatArray | None:
    """Return the accepted segments ``(S, 2)`` of the confidence set (``None`` if incomplete)."""
    boot = fit.bootstrap
    ci = boot.ci if boot is not None else None
    if ci is None or ci.n_unresolved > 0 or not math.isfinite(ci.lo):
        return None
    return np.atleast_2d(np.asarray(ci.segments, dtype=np.float64))[:, :2]


def _inside(gamma: float, reference: PointFit, use: str = "segments") -> bool | None:
    """Whether ``gamma`` is in the confidence set of ``reference`` (``None`` if it has none)."""
    segments = accepted_segments(reference)
    if segments is None or not math.isfinite(gamma):
        return None
    if use == "hull":
        return bool(np.min(segments[:, 0]) <= gamma <= np.max(segments[:, 1]))
    held: BoolArray = (segments[:, 0] <= gamma) & (gamma <= segments[:, 1])
    return bool(held.any())
