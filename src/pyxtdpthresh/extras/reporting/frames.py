"""Tables of a fit as data frames, and its reproducible record as JSON (layer 6)."""

from __future__ import annotations

import json
import math
import platform
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._version import __version__
from pyxtdpthresh.extras.plotting._data import upper_regime_flag
from pyxtdpthresh.extras.reporting.extract import BLOCKS, extract
from pyxtdpthresh.results.containers import XthenregFit

#: Columns of the coefficient frame.
COEFFICIENT_COLUMNS = ("estimate", "se", "z", "p", "ci_low", "ci_high")
#: Columns of the table of the inversion, in the order of ``e(ci_grid)``.
CI_COLUMNS = ("gamma", "statistic", "critical", "accepted", "n_valid", "status")


def to_dataframe(model: object, level: float = 95.0) -> pd.DataFrame:
    """Return the coefficients of a fit as a frame indexed by ``(block, variable)``.

    The blocks are ``lower``, ``change`` and ``upper`` (the slopes above the threshold with their
    own standard error), then ``threshold``: the estimate of the threshold with the interval the
    model reports for it (grid bootstrap for ``xtdpthresh``, asymptotic for ``xthenreg``), which
    has no standard error or p-value here.  ``level`` sets the normal interval of the slopes.
    """
    column = extract(model)
    z = float(norm.ppf(0.5 + level / 200.0))
    records: list[tuple[tuple[str, str], list[float]]] = []
    for block in BLOCKS:
        for (kind, variable), est in column.coefs.items():
            if kind != block:
                continue
            stat = est.b / est.se if est.se > 0 else math.nan
            p = 2.0 * float(norm.sf(abs(stat))) if math.isfinite(stat) else math.nan
            records.append(
                (
                    (block, variable),
                    [est.b, est.se, stat, p, est.b - z * est.se, est.b + z * est.se],
                )
            )
    gamma = column.stats.get("gamma")
    interval = column.stats.get("gamma_ci")
    if isinstance(gamma, float):
        low, high = interval if isinstance(interval, tuple) else (math.nan, math.nan)
        records.append((("threshold", "gamma"), [gamma, math.nan, math.nan, math.nan, low, high]))
    index = pd.MultiIndex.from_tuples([key for key, _ in records], names=["block", "variable"])
    frame = pd.DataFrame([row for _, row in records], index=index, columns=COEFFICIENT_COLUMNS)
    frame.attrs.update(level=level, kind=column.kind, dep_var=column.dep_var)
    return frame


def ci_table(fit: Any) -> pd.DataFrame:
    """Return the full inversion of the grid bootstrap: one row per candidate threshold.

    Columns: ``gamma``, ``statistic`` (the distance ``D``), ``critical`` (its bootstrap critical
    value), ``accepted`` (1 when the candidate is in the confidence set), ``n_valid`` (valid
    draws) and ``status`` (1 valid, 2 mechanical accept, 3 not admissible, 4 sample solve failed,
    5 too few valid draws, 6 no quantile).  It is ``e(ci_grid)`` of the Stata command.
    """
    boot = getattr(fit, "bootstrap", None)
    if boot is None or boot.ci is None:
        raise DataError(message("table_needs_bootstrap"), key="table_needs_bootstrap")
    frame = pd.DataFrame(boot.ci.table, columns=list(CI_COLUMNS))
    for name in ("accepted", "n_valid", "status"):
        frame[name] = frame[name].astype("Int64")
    return frame


def regime_table(fit: Any) -> pd.DataFrame:
    """Return the size of each regime and the mean of the variables in it.

    Rows ``lower`` and ``upper``; columns ``observations`` (equations), ``units`` (units with at
    least one equation in the regime), ``share`` (percent of the equations) and then the mean of
    the dependent variable, of the regressors and of the threshold variable over the equations
    of the regime, at the period of the equation.
    """
    stack = fit.stack
    upper, finite = upper_regime_flag(fit)
    columns: dict[str, np.ndarray] = {
        fit.spec.y: np.asarray(fit.data.y[stack.row], dtype=np.float64),
    }
    level = np.asarray(stack.level_x[stack.current_level], dtype=np.float64)
    for position, name in enumerate(stack.names):
        columns[name] = level[:, position]
    columns[fit.spec.q] = np.asarray(stack.level_q[stack.current_level], dtype=np.float64)
    total = int(finite.sum())
    rows = {}
    for regime, mask in (("lower", finite & ~upper), ("upper", upper)):
        row: dict[str, float] = {
            "observations": float(mask.sum()),
            "units": float(np.unique(stack.unit[mask]).size),
            "share": 100.0 * float(mask.sum()) / total if total else math.nan,
        }
        for name, values in columns.items():
            row[name] = float(np.nanmean(values[mask])) if mask.any() else math.nan
        rows[regime] = row
    frame = pd.DataFrame.from_dict(rows, orient="index")
    frame[["observations", "units"]] = frame[["observations", "units"]].astype("Int64")
    return frame


# ------------------------------------------------------------------------------------ JSON
def _clean(value: Any) -> Any:
    """Convert a value into what JSON can hold (missing and infinite numbers included)."""
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return _clean(value.tolist())
    if isinstance(value, np.generic):
        return _clean(value.item())
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return "inf" if value == math.inf else "-inf" if value == -math.inf else value
    return value


def _environment() -> dict[str, str]:
    """Versions that a run depends on."""
    import scipy

    return {
        "pyxtdpthresh": __version__,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "pandas": pd.__version__,
        "platform": sys.platform,
    }


def _point_fit_record(fit: Any) -> dict[str, Any]:
    """Specification, options, seed and results of an ``xtdpthresh`` fit."""
    spec = fit.spec
    record: dict[str, Any] = {
        "model": "xtdpthresh",
        "specification": {
            "y": spec.y,
            "q": spec.q,
            "x": [term.raw for term in spec.x],
            "id": fit.id,
            "time": fit.time,
        },
        "options": asdict(spec.options),
        "scalars": fit.scalars,
    }
    boot = fit.bootstrap
    if boot is not None and boot.ci is not None:
        record["ci_grid"] = {"columns": list(CI_COLUMNS), "rows": boot.ci.table.tolist()}
    return record


def _xthenreg_record(fit: XthenregFit) -> dict[str, Any]:
    """Options and results of an ``xthenreg`` fit."""
    return {
        "model": "xthenreg",
        "specification": {"y": fit.y_name, "q": fit.q_name, "names": list(fit.names)},
        "options": {
            "static": fit.static,
            "kink": fit.kink,
            "grid_num": fit.grid_num,
            "trim_rate": fit.trim_rate,
            "boot_reps": fit.boot_reps,
            "seed": fit.seed,
        },
        "scalars": {
            "gamma": fit.gamma,
            "N": fit.n_units,
            "T": fit.n_periods,
            "boots_p": fit.boots_p,
            "sup_wald": fit.sup_wald,
            "bandwidth": fit.bandwidth,
        },
        "cov": fit.cov.tolist(),
        "ci": fit.ci.tolist(),
    }


def to_json(model: object, path: str | Path | None = None, *, level: float = 95.0) -> str:
    """Return a reproducible record of a fit as JSON; also write it to ``path`` when given.

    It holds the versions of the packages, the specification and options (the seed is in the
    options and in the scalars as ``rseed``), the coefficients with their standard errors, the
    scalars of ``e()`` and, for ``xtdpthresh``, the inversion table of the confidence set.
    Missing numbers are ``null`` and infinite ones the strings ``"inf"`` and ``"-inf"``.
    """
    record = _xthenreg_record(model) if isinstance(model, XthenregFit) else _point_fit_record(model)
    frame = to_dataframe(model, level)
    record["coefficients"] = [
        {"block": block, "variable": variable, **row}
        for (block, variable), row in frame.to_dict(orient="index").items()
    ]
    record["environment"] = _environment()
    text = json.dumps(_clean(record), indent=2, ensure_ascii=False)
    if path is not None:
        Path(path).write_text(text + "\n", encoding="utf-8")
    return text
