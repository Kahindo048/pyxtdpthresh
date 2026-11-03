"""Options of ``xtdpthresh`` and their checks.

The checks run in the order of the Stata command, so that the first failing rule is the same
in both programs.  Arguments use Python names (``grid_ci``, ``min_regime``, ``bootstrap=False``
for ``noboot``...); every failure raises :class:`~pyxtdpthresh._errors.SpecificationError` with
the key of the rule and the return code Stata gives it.
"""

from __future__ import annotations

import math
import numbers
import warnings
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from pyxtdpthresh._errors import PyxdpthreshWarning, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import BootType, GridType, Method

#: Largest seed Stata's ``set seed`` accepts.
MAX_SEED = 2**31 - 1


@dataclass(frozen=True)
class XtdpthreshOptions:
    """Validated options of one ``xtdpthresh`` call (defaults are those of the Stata command).

    Attributes
    ----------
    kink, static, time_effects, collapse, iv_collapse
        Model variants and instrument options (``iv_collapse`` collapses only the external
        instruments; ``collapse`` implies it).
    maxlag
        ``(lo, hi)`` lags used by the GMM-style instruments; ``hi`` is infinite when unrestricted.
    method
        ``"fd"`` or ``"fod"``.
    grid, grid_type, grid_sample, min_regime, trim, refine, bw_scale
        Threshold search.
    bootstrap, n_boot, boot_type, seed, grid_ci, gamma_test, linearity_test, continuity_test
        Bootstrap tests and the confidence set of the threshold.
    coef_boot, coef_ci_type, vce, center, history, level
        Coefficient inference and sample history.
    warn, verbose, export_gmm
        Messages and extra output.
    """

    kink: bool = False
    static: bool = False
    time_effects: bool = False
    collapse: bool = False
    iv_collapse: bool = False
    maxlag: tuple[int, float] = (1, math.inf)
    method: Method = "fd"
    grid: int = 100
    grid_type: GridType = "uniform"
    grid_sample: str = "effective"
    min_regime: int = 0
    trim: float = 0.10
    refine: int = 0
    bw_scale: float = 1.5
    bootstrap: bool = True
    n_boot: int = 299
    boot_type: BootType = "wild"
    seed: int | None = None
    grid_ci: int = 100
    gamma_test: float | None = None
    linearity_test: bool = True
    continuity_test: bool = False
    coef_boot: str = "none"
    coef_ci_type: str = "symmetric"
    vce: str = "robust"
    center: bool = True
    history: str = "panel"
    level: float = 95.0
    warn: bool = True
    verbose: bool = False
    export_gmm: bool = False


def _fail(key: str, code: int = 198, **fields: Any) -> SpecificationError:
    return SpecificationError(message(key, **fields), stata_code=code, key=key)


def _integer(name: str, value: Any) -> int:
    """``value`` as an int; Stata's ``integer`` option type rejects fractions (rc 198)."""
    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        number = float(value)
        if math.isfinite(number) and number == int(number):
            return int(number)
    raise _fail("opt_type_int", name=name, value=value)


def _number(name: str, value: Any) -> float:
    """``value`` as a float; Stata's ``real`` option type rejects non-numbers (rc 198)."""
    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        return float(value)
    raise _fail("opt_type_number", name=name, value=value)


def _text(value: Any, default: str) -> str:
    """Lower-case, trimmed text; an empty value takes ``default`` (``lower(trim())``)."""
    text = str(value).strip().lower()
    return text or default


def _parse_maxlag(value: Any) -> tuple[int, float]:
    """``maxlag`` as ``(lo, hi)``: an integer, a pair, or ``None`` for no limit."""
    # Stata: maxlag(numlist max=2 min=1 integer >0) (xtdpthresh.ado:69, 439-455)
    if value is None:
        return 1, math.inf
    items = [value] if isinstance(value, numbers.Real) else list(value)
    if not 1 <= len(items) <= 2:
        raise _fail("opt_maxlag_count", 123, value=value)
    parsed = []
    for item in items:
        if not isinstance(item, numbers.Real) or isinstance(item, bool):
            raise _fail("opt_maxlag_int", 126, value=value)
        number = float(item)
        if not math.isfinite(number) or number != int(number):
            raise _fail("opt_maxlag_int", 126, value=value)
        if number <= 0:
            raise _fail("opt_maxlag_range", 125, value=value)
        parsed.append(int(number))
    lo, hi = (1, parsed[0]) if len(parsed) == 1 else (parsed[0], parsed[1])
    return lo, float(hi)


def _seed(value: Any) -> int:
    """``seed`` as an int in ``[0, 2**31 - 1]``."""
    # Stata: confirm integer number, then the range (xtdpthresh.ado:417-430)
    if isinstance(value, numbers.Real) and not isinstance(value, bool):
        number = float(value)
        if math.isfinite(number) and number == int(number) and 0 <= int(number) <= MAX_SEED:
            return int(number)
    raise _fail("opt_seed", value=value)


def _choice(a: dict[str, Any], name: str, allowed: tuple[str, ...], default: str, key: str) -> str:
    """Case-insensitive choice among ``allowed``."""
    value = _text(a[name], default)
    if value not in allowed:
        raise _fail(key, value=a[name])
    return value


# ------------------------------------------------------------------ ordered stages
def _stage_typed(a: dict[str, Any], v: dict[str, Any]) -> None:
    """Typing and ranges the Stata ``syntax`` line enforces (return codes 198, 123, 125, 126)."""
    v["grid"], v["grid_ci"] = _integer("grid", a["grid"]), _integer("grid_ci", a["grid_ci"])
    v["min_regime"] = _integer("min_regime", a["min_regime"])
    v["refine"] = _integer("refine", a["refine"])
    v["n_boot"] = _integer("n_boot", a["n_boot"])
    v["search_max"] = _integer("search_max", a["search_max"])
    v["trim"], v["bw_scale"] = _number("trim", a["trim"]), _number("bw_scale", a["bw_scale"])
    v["search_tol"] = _number("search_tol", a["search_tol"])
    v["level"] = _number("level", a["level"])
    v["maxlag"] = _parse_maxlag(a["maxlag"])
    if not 10 <= v["level"] <= 99.99:
        raise _fail("opt_level", value=a["level"])
    gamma = a["gamma_test"]
    v["gamma_test"] = None if gamma is None else _number("gamma_test", gamma)


def _stage_inference(a: dict[str, Any], v: dict[str, Any]) -> None:
    """``vce``, ``coef_ci_type`` and ``coef_boot``."""
    v["vce"] = _choice(a, "vce", ("robust", "windmeijer"), "robust", "opt_vce")
    v["coef_ci_type"] = _choice(
        a, "coef_ci_type", ("symmetric", "percentile"), "symmetric", "opt_coef_ci_type"
    )
    if _text(a["coef_boot"], "none") == "gs":
        raise _fail("opt_coef_boot_gs")
    v["coef_boot"] = _choice(
        a, "coef_boot", ("twostep", "onestep", "none"), "none", "opt_coef_boot"
    )
    if v["coef_boot"] in ("twostep", "onestep") and a["warn"]:
        text = message("note_coef_boot", value=v["coef_boot"])
        warnings.warn(text, PyxdpthreshWarning, stacklevel=4)


def _stage_search(a: dict[str, Any], v: dict[str, Any]) -> None:
    """Threshold-search options and the retired ``search_*`` arguments."""
    v["grid_type"] = _choice(a, "grid_type", ("uniform", "quantile"), "uniform", "opt_grid_type")
    if v["min_regime"] < 0:
        raise _fail("opt_min_regime", value=a["min_regime"])
    if not v["bw_scale"] > 0:
        raise _fail("opt_bw_scale", value=a["bw_scale"])
    if not 0 <= v["refine"] <= 20:
        raise _fail("opt_refine", value=a["refine"])
    if v["refine"] > 0 and a["kink"]:
        raise _fail("opt_refine_kink")
    if a["search_mode"] not in (None, "") or v["search_max"] != -1 or v["search_tol"] != 1e-8:
        raise _fail("opt_search_retired")


def _stage_history(a: dict[str, Any], v: dict[str, Any], terms: Sequence[str]) -> None:
    """``history`` and its incompatibility with operated terms."""
    v["history"] = _choice(a, "history", ("panel", "sample"), "panel", "opt_history")
    operated = [t for t in terms if "." in t]
    if v["history"] == "sample" and operated:
        raise _fail("opt_history_sample_ts", terms=", ".join(operated))


def _stage_boot_type(a: dict[str, Any], v: dict[str, Any]) -> None:
    """``boot_type`` (and what the unit bootstrap does not support), ``grid_sample``, retired."""
    if _text(a["boot_type"], "wild") == "exact":
        raise _fail("opt_boot_type_exact")
    v["boot_type"] = _choice(a, "boot_type", ("wild", "unit"), "wild", "opt_boot_type")
    if a["bootstrap"] and v["boot_type"] == "unit":
        if _text(a["method"], "fd") != "fd":
            raise _fail("opt_boot_type_unit_method")
        if a["kink"]:
            raise _fail("opt_boot_type_unit_kink")
    v["grid_sample"] = _choice(
        a, "grid_sample", ("effective", "observed"), "effective", "opt_grid_sample"
    )
    if a["lev_maxlag"] not in (None, ""):
        raise _fail("opt_lev_maxlag")
    if a["iv_maxlag"] is not None:
        raise _fail("opt_iv_maxlag")


def _stage_counts(a: dict[str, Any], v: dict[str, Any]) -> None:
    """Check ``method``, the minimum counts, ``trim``, ``seed`` and the ``maxlag`` order."""
    if _text(a["method"], "fd") == "system":
        raise _fail("opt_method_system")
    v["method"] = _choice(a, "method", ("fd", "fod"), "fd", "opt_method")
    boot = bool(a["bootstrap"])
    if v["grid"] < 10:
        raise _fail("opt_grid", value=a["grid"])
    if boot and v["grid_ci"] < 10:
        raise _fail("opt_grid_ci", value=a["grid_ci"])
    if v["gamma_test"] is not None and not boot:
        raise _fail("opt_gamma_test")
    if a["continuity_test"] and not (boot and a["linearity_test"]):
        raise _fail("opt_continuity_boot")
    if not 0.01 <= v["trim"] <= 0.45:
        raise _fail("opt_trim", value=a["trim"])
    if boot and v["n_boot"] < 10:
        raise _fail("opt_n_boot", value=a["n_boot"])
    v["seed"] = _seed(a["seed"]) if a["seed"] is not None and boot else None
    if v["maxlag"][0] > v["maxlag"][1]:
        raise _fail("opt_maxlag_order", value=a["maxlag"])


def make_options(
    *,
    kink: bool = False,
    static: bool = False,
    time_effects: bool = False,
    collapse: bool = False,
    iv_collapse: bool = False,
    maxlag: Any = None,
    method: str = "fd",
    grid: Any = 100,
    grid_type: str = "uniform",
    grid_sample: str = "effective",
    min_regime: Any = 0,
    trim: Any = 0.10,
    refine: Any = 0,
    bw_scale: Any = 1.5,
    bootstrap: bool = True,
    n_boot: Any = 299,
    boot_type: str = "wild",
    seed: Any = None,
    grid_ci: Any = 100,
    gamma_test: Any = None,
    linearity_test: bool = True,
    continuity_test: bool = False,
    coef_boot: str = "none",
    coef_ci_type: str = "symmetric",
    vce: str = "robust",
    center: bool = True,
    history: str = "panel",
    level: Any = 95,
    warn: bool = True,
    verbose: bool = False,
    export_gmm: bool = False,
    search_mode: Any = None,
    search_max: Any = -1,
    search_tol: Any = 1e-8,
    lev_maxlag: Any = None,
    iv_maxlag: Any = None,
    terms: Sequence[str] = (),
) -> XtdpthreshOptions:
    """Check the options in the order of the Stata command and return them normalised.

    Parameters
    ----------
    terms
        Every variable term the call names (regressors, ``endogenous``, ``predetermined``,
        ``exogenous``, ``iv``); ``history="sample"`` is refused when one is a lag or difference.
    search_mode, search_max, search_tol, lev_maxlag, iv_maxlag
        Retired arguments, kept so that using them gives an explicit error.

    Raises
    ------
    SpecificationError
        On the first rule that fails; ``key`` names the rule and ``stata_code`` is Stata's
        return code.
    """
    # Stata: xtdpthresh.ado:58-460 (syntax line, then the option checks)
    given = {k: val for k, val in locals().items() if k != "terms"}
    out: dict[str, Any] = {}
    _stage_typed(given, out)
    _stage_inference(given, out)
    _stage_search(given, out)
    _stage_history(given, out, terms)
    _stage_boot_type(given, out)
    _stage_counts(given, out)
    return XtdpthreshOptions(
        kink=bool(kink),
        static=bool(static),
        time_effects=bool(time_effects),
        collapse=bool(collapse),
        iv_collapse=bool(iv_collapse or collapse),
        maxlag=out["maxlag"],
        method=out["method"],
        grid=out["grid"],
        grid_type=out["grid_type"],
        grid_sample=out["grid_sample"],
        min_regime=out["min_regime"],
        trim=out["trim"],
        refine=out["refine"],
        bw_scale=out["bw_scale"],
        bootstrap=bool(bootstrap),
        n_boot=out["n_boot"],
        boot_type=out["boot_type"],
        seed=out["seed"],
        grid_ci=out["grid_ci"],
        gamma_test=out["gamma_test"],
        linearity_test=bool(linearity_test),
        continuity_test=bool(continuity_test),
        coef_boot=out["coef_boot"],
        coef_ci_type=out["coef_ci_type"],
        vce=out["vce"],
        center=bool(center),
        history=out["history"],
        level=out["level"],
        warn=bool(warn),
        verbose=bool(verbose),
        export_gmm=bool(export_gmm),
    )


def check_time_effects(options: XtdpthreshOptions) -> None:
    """Refuse the combinations of ``time_effects`` that the bootstrap cannot replay."""
    # Stata: xtdpthresh.ado:1015-1026 (checked after the variable lists)
    if options.bootstrap and options.time_effects and options.boot_type == "unit":
        raise _fail("opt_td_boot_type_unit")
    if options.bootstrap and options.time_effects and options.coef_boot == "twostep":
        raise _fail("opt_td_coef_boot")
