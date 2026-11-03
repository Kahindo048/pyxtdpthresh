"""Specification checks of ``xtdpthresh`` against Stata (block E.1; files ``spec_*``).

Each case is a dict of Python keyword arguments.  It is rendered as a Stata command, run
with ``capture noisily``, and the return code and the text of the error are frozen in
``tests/golden/spec_golden.json``.  The Python test then checks, for every case, that

* the same rule fires (``SpecificationError.key`` is the case's expected key and the frozen
  Stata text contains the fragment that identifies that rule in Stata), and
* the return code is Stata's, or that no error is raised when Stata accepted the command.

The texts themselves differ on purpose: the package words its messages for the Python call.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from validation.cases import STATA_DIR

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "spec_golden.json"
LOG = STATA_DIR / "_run_spec_cases.log"

#: Arguments that name variables; every other argument is an option.
VARIABLE_ARGS = ("y", "x", "q", "endogenous", "predetermined", "exogenous", "iv")
#: Defaults that keep the valid cases fast (no bootstrap, small grid).
BASE: dict[str, Any] = {
    "y": "invest",
    "x": ("cashflow",),
    "q": "debt",
    "bootstrap": False,
    "grid": 10,
}

#: Fragment of the Stata message that identifies each rule (None: only the code is compared).
FRAGMENTS: dict[str, str | None] = {
    "opt_type_int": None,
    "opt_type_number": None,
    "opt_vce": "option vce() must be robust or windmeijer",
    "opt_coef_ci_type": "option coefcitype() must be",
    "opt_coef_boot_gs": "coefboot(gs) is not implemented",
    "opt_coef_boot": "option coefboot() must be",
    "opt_grid_type": "option gridtype() must be",
    "opt_min_regime": "minregime() must be >= 0",
    "opt_bw_scale": "option bwscale() must be positive",
    "opt_refine": "option refine() must be an integer between 0 and 20",
    "opt_refine_kink": "refine() is supported for the jump specification only",
    "opt_search_retired": "searchmode(), searchmax(), and searchtol()",
    "opt_history": "option history() must be panel or sample",
    "opt_history_sample_ts": "history(sample) cannot retro-restrict",
    "opt_boot_type_exact": "boottype(exact) has been renamed",
    "opt_boot_type": "option boottype() must be wild or unit",
    "opt_boot_type_unit_method": "currently supports method(fd) only",
    "opt_boot_type_unit_kink": "does not support kink",
    "opt_grid_sample": "option gridsample() must be",
    "opt_lev_maxlag": "levmaxlag() was retired",
    "opt_iv_maxlag": "iv() sub-option maxlag() is not supported",
    "opt_method_system": "method(system) is no longer supported",
    "opt_method": "option method() must be fd or fod",
    "opt_grid": "grid() must be at least 10",
    "opt_grid_ci": "gridci() must be at least 10",
    "opt_gamma_test": "citest() requires the grid bootstrap",
    "opt_continuity_boot": "conttest requires the bootstrap tests",
    "opt_trim": "trim must be in [0.01, 0.45]",
    "opt_n_boot": "boot should be at least 10",
    "opt_seed": "rseed() must be an integer in",
    "opt_level": "level() must be between 10 and 99.99",
    "opt_maxlag_count": "too many elements",
    "opt_maxlag_range": "outside of allowed range",
    "opt_maxlag_int": "noninteger elements",
    "opt_maxlag_order": "requires min <= max",
    "opt_td_boot_type_unit": "boottype(unit) is not available with td",
    "opt_td_coef_boot": "coefboot(twostep) is not available with td",
    "term_invalid": None,
    "spec_depvar_operator": "dependent variable may not contain time-series operators",
    "spec_depvar_lag_exogenous": "is a lag of the dependent variable and cannot be strictly",
    "spec_depvar_current_exogenous": "contains the current or a future value of the dep",
    "spec_depvar_current_regressor": "it cannot be a regressor",
    "spec_depvar_current_iv": "it cannot be an instrument",
    "spec_overlap_endog_x": "endogenous() vars must not appear in indepvars",
    "spec_overlap_endog_exog": "endogenous() and exogenous() vars must not overlap",
    "spec_overlap_x_exog": "indepvars and exogenous() vars must not overlap",
    "spec_overlap_predet_x": "predetermined() vars must not appear in indepvars",
    "spec_overlap_predet_exog": "predetermined() and exogenous() vars must not overlap",
    "spec_overlap_predet_endog": "predetermined() and endogenous() vars must not overlap",
    "spec_iv_declared": "iv() may not contain variables declared",
    "spec_static_empty": "a static model requires at least one regressor",
    "spec_conttest_kink": "conttest is not allowed with kink",
    "spec_conttest_q": "as a contemporaneous regressor",
    "spec_duplicates": "duplicate variables in",
    "spec_depvar_in_rhs": "the dependent variable may not appear in",
    "spec_q_is_depvar": "qx() may not be the dependent variable",
    "spec_exogenous_lag_of_declared": "is declared strictly exogenous",
    "spec_iv_lag_needed": "is not a valid instrument under method",
    "spec_auto_lag_y": "added automatically in the dynamic model",
}


@dataclass(frozen=True)
class SpecCase:
    """One specification: Python arguments on top of :data:`BASE`, and the rule expected."""

    name: str
    args: dict[str, Any] = field(default_factory=dict)
    key: str | None = None  # None: the command is valid

    def full_args(self) -> dict[str, Any]:
        """The arguments of the call, base included."""
        return {**BASE, **self.args}


def _case(name: str, key: str | None = None, **args: Any) -> SpecCase:
    return SpecCase(name, args, key)


OPTION_CASES: tuple[SpecCase, ...] = (
    _case("ok_default"),
    _case("ok_fod", method="FOD"),
    _case("ok_maxlag_pair", maxlag=(2, 8)),
    _case("ok_maxlag_one", maxlag=3),
    _case("ok_vce_case", vce="Windmeijer"),
    _case("ok_level", level=90),
    _case("ok_bad_seed_without_bootstrap", seed=1.5),
    _case("ok_unit_without_bootstrap", boot_type="unit", method="fod"),
    _case("ok_bad_nboot_without_bootstrap", n_boot=3),
    _case("ok_bad_gridci_without_bootstrap", grid_ci=3),
    _case("ok_coef_boot_onestep", coef_boot="onestep", warn=False),
    _case("vce", "opt_vce", vce="bogus"),
    _case("coef_ci_type", "opt_coef_ci_type", coef_ci_type="bogus"),
    _case("coef_boot_gs", "opt_coef_boot_gs", coef_boot="gs"),
    _case("coef_boot", "opt_coef_boot", coef_boot="bogus"),
    _case("grid_type", "opt_grid_type", grid_type="bogus"),
    _case("min_regime", "opt_min_regime", min_regime=-1),
    _case("bw_scale_zero", "opt_bw_scale", bw_scale=0),
    _case("bw_scale_negative", "opt_bw_scale", bw_scale=-1),
    _case("refine_high", "opt_refine", refine=21),
    _case("refine_negative", "opt_refine", refine=-1),
    _case("refine_kink", "opt_refine_kink", refine=2, kink=True),
    _case("search_mode", "opt_search_retired", search_mode="fixed"),
    _case("search_max", "opt_search_retired", search_max=50),
    _case("search_tol", "opt_search_retired", search_tol=1e-5),
    _case("history", "opt_history", history="bogus"),
    _case("history_sample_lag", "opt_history_sample_ts", history="sample", x=("L.cashflow",)),
    _case("history_sample_ok", history="sample"),
    _case("boot_type_exact", "opt_boot_type_exact", boot_type="exact"),
    _case("boot_type", "opt_boot_type", boot_type="bogus"),
    _case("unit_fod", "opt_boot_type_unit_method", boot_type="unit", method="fod", bootstrap=True),
    _case("unit_kink", "opt_boot_type_unit_kink", boot_type="unit", kink=True, bootstrap=True),
    _case("grid_sample", "opt_grid_sample", grid_sample="bogus"),
    _case("lev_maxlag", "opt_lev_maxlag", lev_maxlag="2"),
    _case("iv_maxlag", "opt_iv_maxlag", iv=("z1",), iv_maxlag=2),
    _case("method_system", "opt_method_system", method="system"),
    _case("method", "opt_method", method="bogus"),
    _case("grid_small", "opt_grid", grid=9),
    _case("grid_ci_small", "opt_grid_ci", grid_ci=9, bootstrap=True),
    _case("gamma_test_noboot", "opt_gamma_test", gamma_test=0.2),
    _case("continuity_noboot", "opt_continuity_boot", continuity_test=True),
    _case(
        "continuity_notest",
        "opt_continuity_boot",
        continuity_test=True,
        bootstrap=True,
        linearity_test=False,
    ),  # fmt: skip
    _case("trim_high", "opt_trim", trim=0.5),
    _case("trim_low", "opt_trim", trim=0.005),
    _case("n_boot_small", "opt_n_boot", n_boot=9, bootstrap=True, grid_ci=10),
    _case("seed_fraction", "opt_seed", seed=1.5, bootstrap=True, n_boot=10, grid_ci=10),
    _case("seed_negative", "opt_seed", seed=-1, bootstrap=True, n_boot=10, grid_ci=10),
    _case("seed_large", "opt_seed", seed=2147483648, bootstrap=True, n_boot=10, grid_ci=10),
    _case("level_low", "opt_level", level=5),
    _case("level_high", "opt_level", level=100),
    _case("maxlag_zero", "opt_maxlag_range", maxlag=0),
    _case("maxlag_three", "opt_maxlag_count", maxlag=(1, 2, 3)),
    _case("maxlag_fraction", "opt_maxlag_int", maxlag=1.5),
    _case("maxlag_order", "opt_maxlag_order", maxlag=(3, 2)),
    _case("grid_fraction", "opt_type_int", grid=5.5),
    _case("min_regime_fraction", "opt_type_int", min_regime=1.5),
    _case("refine_fraction", "opt_type_int", refine=2.5),
    _case("trim_text", "opt_type_number", trim="abc"),
    _case("bw_scale_text", "opt_type_number", bw_scale="abc"),
    _case(
        "td_unit",
        "opt_td_boot_type_unit",
        time_effects=True,
        boot_type="unit",
        bootstrap=True,
        n_boot=10,
        grid_ci=10,
    ),  # fmt: skip
    _case(
        "td_twostep",
        "opt_td_coef_boot",
        time_effects=True,
        coef_boot="twostep",
        bootstrap=True,
        n_boot=10,
        grid_ci=10,
        warn=False,
    ),  # fmt: skip
    _case("td_twostep_noboot", time_effects=True, coef_boot="twostep", warn=False),
)

OPERATOR_CASES: tuple[SpecCase, ...] = (
    _case("ok_range", x=("L(1/2).cashflow",)),
    _case("ok_predetermined_lag2", predetermined=("L2.invest",)),
    _case("ok_endogenous_lag2", endogenous=("L2.invest",)),
    _case("ok_iv_lag2", iv=("L2.invest",)),
    _case("ok_dl", x=("DL.cashflow", "F.tobin_q")),
    _case("y_operator", "spec_depvar_operator", y="L.invest"),
    _case("y_difference", "spec_depvar_operator", y="D.invest"),
    _case("x_lag2_y", "spec_depvar_lag_exogenous", x=("L2.invest",)),
    _case("x_lag3_y", "spec_depvar_lag_exogenous", x=("cashflow", "L3.invest")),
    _case("exogenous_lag2_y", "spec_depvar_lag_exogenous", exogenous=("L2.invest",)),
    _case("x_ld_y", "spec_depvar_current_exogenous", x=("LD.invest",)),
    _case("x_lead_y", "spec_depvar_current_exogenous", x=("F.invest",)),
    _case("x_seasonal_y", "spec_depvar_current_exogenous", x=("S12.invest",)),
    _case("exogenous_diff_y", "spec_depvar_current_exogenous", exogenous=("D.invest",)),
    _case("endogenous_diff_y", "spec_depvar_current_regressor", endogenous=("D.invest",)),
    _case("endogenous_lead_y", "spec_depvar_current_regressor", endogenous=("F.invest",)),
    _case("predetermined_ld_y", "spec_depvar_current_regressor", predetermined=("LD.invest",)),
    _case("iv_diff_y", "spec_depvar_current_iv", iv=("D.invest",)),
    _case("iv_lead_y", "spec_depvar_current_iv", iv=("F2.invest",)),
    _case("bad_operator", "term_invalid", x=("Q.cashflow",)),
    _case("bad_name", "term_invalid", x=("2cashflow",)),
)

_BOOT = {"bootstrap": True, "n_boot": 10, "grid_ci": 10}

ROLE_CASES: tuple[SpecCase, ...] = (
    _case("ok_roles", x=("cashflow",), endogenous=("tobin_q",), predetermined=("L.debt",)),
    _case("ok_lag_not_overlapping", x=("cashflow",), endogenous=("L.cashflow",)),
    _case("ok_exogenous_earlier_lag", endogenous=("L2.tobin_q",), exogenous=("L.tobin_q",)),
    _case("ok_predetermined_lag_exogenous_now", predetermined=("L.cashflow",), x=("cashflow",)),
    _case("ok_iv_far_lag", endogenous=("tobin_q",), iv=("L2.tobin_q",)),
    _case("ok_iv_fod_lag", iv=("L.invest",), method="fod"),
    _case("ok_conttest", x=("cashflow", "debt"), continuity_test=True, **_BOOT),
    _case("overlap_endog_x", "spec_overlap_endog_x", x=("cashflow",), endogenous=("cashflow",)),
    _case(
        "overlap_endog_x_lag",
        "spec_overlap_endog_x",
        x=("L.cashflow",),
        endogenous=("L1.cashflow",),
    ),  # fmt: skip
    _case(
        "overlap_endog_x_l0", "spec_overlap_endog_x", x=("cashflow",), endogenous=("L0.cashflow",)
    ),  # fmt: skip
    _case(
        "overlap_endog_exog",
        "spec_overlap_endog_exog",
        endogenous=("tobin_q",),
        exogenous=("tobin_q",),
    ),  # fmt: skip
    _case("overlap_x_exog", "spec_overlap_x_exog", exogenous=("cashflow",)),
    _case("overlap_predet_x", "spec_overlap_predet_x", predetermined=("cashflow",)),
    _case(
        "overlap_predet_exog",
        "spec_overlap_predet_exog",
        predetermined=("tobin_q",),
        exogenous=("tobin_q",),
    ),  # fmt: skip
    _case(
        "overlap_predet_endog",
        "spec_overlap_predet_endog",
        predetermined=("tobin_q",),
        endogenous=("tobin_q",),
    ),  # fmt: skip
    _case("iv_declared_endog", "spec_iv_declared", endogenous=("z1",), iv=("z1",)),
    _case("iv_declared_predet", "spec_iv_declared", predetermined=("z1",), iv=("z1",)),
    _case("static_empty", "spec_static_empty", static=True, x=()),
    _case("conttest_kink", "spec_conttest_kink", continuity_test=True, kink=True, **_BOOT),
    _case("conttest_q_missing", "spec_conttest_q", continuity_test=True, **_BOOT),
    _case("dup_x", "spec_duplicates", x=("cashflow", "cashflow")),
    _case("dup_x_l0", "spec_duplicates", x=("cashflow", "L0.cashflow")),
    _case("dup_x_lag", "spec_duplicates", x=("L.cashflow", "l1.cashflow")),
    _case("dup_exogenous", "spec_duplicates", exogenous=("tobin_q", "tobin_q")),
    _case("dup_endogenous", "spec_duplicates", endogenous=("tobin_q", "tobin_q")),
    _case("dup_predetermined", "spec_duplicates", predetermined=("tobin_q", "tobin_q")),
    _case("dup_iv", "spec_duplicates", iv=("z1", "z1")),
    _case("y_in_x", "spec_depvar_in_rhs", x=("invest",)),
    _case("y_in_x_l0", "spec_depvar_in_rhs", x=("L0.invest",)),
    _case("y_endogenous", "spec_depvar_in_rhs", endogenous=("invest",)),
    _case("y_iv", "spec_depvar_in_rhs", iv=("invest",)),
    _case("q_is_y", "spec_q_is_depvar", q="invest"),
    _case(
        "exogenous_lag_of_endogenous",
        "spec_exogenous_lag_of_declared",
        endogenous=("tobin_q",),
        x=("L.tobin_q",),
    ),  # fmt: skip
    _case(
        "exogenous_same_date_as_predetermined",
        "spec_exogenous_lag_of_declared",
        predetermined=("cashflow",),
        exogenous=("L.cashflow",),
        x=(),
    ),  # fmt: skip
    _case(
        "exogenous_lag3_of_endogenous_lag2",
        "spec_exogenous_lag_of_declared",
        endogenous=("L2.tobin_q",),
        x=("L3.tobin_q",),
    ),  # fmt: skip
    _case(
        "exogenous_difference_of_endogenous",
        "spec_exogenous_lag_of_declared",
        endogenous=("tobin_q",),
        exogenous=("D.tobin_q",),
    ),  # fmt: skip
    _case("iv_lag_too_short", "spec_iv_lag_needed", endogenous=("tobin_q",), iv=("L.tobin_q",)),
    _case("iv_lag_depvar_fd", "spec_iv_lag_needed", iv=("L.invest",)),
    _case(
        "iv_lag_predetermined", "spec_iv_lag_needed", predetermined=("L.tobin_q",), iv=("tobin_q",)
    ),  # fmt: skip
)

AUTO_LAG_CASES: tuple[SpecCase, ...] = (
    _case("ok_static_predetermined_lag", static=True, predetermined=("L.invest",)),
    _case("ok_dynamic_lag2_exogenous_as_predetermined", predetermined=("L2.invest", "L3.invest")),
    _case("auto_lag_x", "spec_auto_lag_y", x=("L.invest",)),
    _case("auto_lag_x_l1", "spec_auto_lag_y", x=("l1.invest", "cashflow")),
    _case("auto_lag_fl2", "spec_auto_lag_y", x=("FL2.invest",)),
    _case("auto_lag_l2f", "spec_auto_lag_y", x=("L2F.invest",)),
    _case("auto_lag_endogenous", "spec_auto_lag_y", endogenous=("L.invest",)),
    _case("auto_lag_predetermined", "spec_auto_lag_y", predetermined=("L.invest",)),
    _case("auto_lag_exogenous", "spec_auto_lag_y", exogenous=("L.invest",)),
    _case("static_lag_exogenous", "spec_depvar_lag_exogenous", static=True, x=("L.invest",)),
    _case("auto_lag_ld_is_not_the_lag", "spec_depvar_current_exogenous", x=("LD.invest",)),
)

ALL_CASES: tuple[SpecCase, ...] = (
    *OPTION_CASES,
    *OPERATOR_CASES,
    *ROLE_CASES,
    *AUTO_LAG_CASES,
)

# --------------------------------------------------------------------------- Stata rendering
_FLAGS = {
    "kink": "kink",
    "static": "static",
    "time_effects": "td",
    "collapse": "collapse",
    "continuity_test": "conttest",
    "verbose": "verbose",
    "export_gmm": "exportgmm",
}
_LISTS = ("endogenous", "predetermined", "exogenous")
_NEGATED = {"bootstrap": "noboot", "linearity_test": "notest", "center": "nocenter",
            "warn": "nowarn"}  # fmt: skip
_VALUED = {
    "method": "method", "grid": "grid", "grid_type": "gridtype", "grid_sample": "gridsample",
    "min_regime": "minregime", "trim": "trim", "refine": "refine", "bw_scale": "bwscale",
    "n_boot": "boot", "boot_type": "boottype", "seed": "rseed", "grid_ci": "gridci",
    "gamma_test": "citest", "coef_boot": "coefboot", "coef_ci_type": "coefcitype",
    "vce": "vce", "history": "history", "level": "level", "search_mode": "searchmode",
    "search_max": "searchmax", "search_tol": "searchtol", "lev_maxlag": "levmaxlag",
    "maxlag": "maxlag",
}  # fmt: skip
_DEFAULT_ON = {"bootstrap", "linearity_test", "center", "warn"}


def _value(value: Any) -> str:
    if isinstance(value, (tuple, list)):
        return " ".join(str(v) for v in value)
    return str(value)


def stata_command(args: dict[str, Any]) -> str:
    """The Stata command equivalent to the Python arguments."""
    opts = [f"qx({args['q']})"]
    opts += [option for name, option in _FLAGS.items() if args.get(name)]
    opts += [option for name, option in _NEGATED.items() if name in args and not args[name]]
    opts += [
        f"{option}({_value(args[name])})"
        for name, option in _VALUED.items()
        if args.get(name) is not None
    ]
    opts += [f"{name}({_value(args[name])})" for name in _LISTS if args.get(name)]
    if args.get("iv"):
        sub = f", maxlag({args['iv_maxlag']})" if args.get("iv_maxlag") is not None else ""
        sub = sub or (", collapse" if args.get("iv_collapse") else "")
        opts.append(f"iv({_value(args['iv'])}{sub})")
    return f"xtdpthresh {args['y']} {_value(args.get('x', ()))}, {' '.join(opts)}"


def render_do(cases: tuple[SpecCase, ...] | None = None) -> str:
    """Do-file that runs every case with ``capture noisily`` and marks case and return code."""
    cases = ALL_CASES if cases is None else cases
    out = [
        "version 17",
        "set more off",
        "clear all",
        'use "../data/invest.dta", clear',
        "xtset firm year",
        "gen double z1 = cashflow*tobin_q + debt",
        "gen double z2 = ln(1 + tobin_q)",
    ]
    for c in cases:
        out += [
            f'display "@@CASE {c.name}"',
            f"capture noisily {stata_command(c.full_args())}",
            'display "@@RC " _rc',
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/spec_cases.do``."""
    path = path or STATA_DIR / "spec_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


# --------------------------------------------------------------------------- freeze
_ECHO = re.compile(r"^(\. |> |\s*\d+\.\s)")


def parse_log(text: str) -> dict[str, dict[str, Any]]:
    """Return code and error text of each case in a log produced by :func:`render_do`."""
    cases: dict[str, dict[str, Any]] = {}
    name = None
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("@@CASE "):
            name, lines = line[7:].strip(), []
        elif line.startswith("@@RC ") and name is not None:
            cases[name] = {"rc": int(line[5:].strip()), "text": " ".join(lines)[:600]}
            name = None
        elif name is not None and line.strip() and not _ECHO.match(line):
            lines.append(line.strip())
    return cases


def freeze(log: Path = LOG, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/spec_golden.json``."""
    master = {
        "meta": {
            "stata": "Stata 17.0 MP",
            "xtdpthresh": "0.9.38",
            "source": "validation/spec_cases.py",
        },
        "cases": parse_log(log.read_text(encoding="utf-8", errors="replace")),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master, indent=1), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
