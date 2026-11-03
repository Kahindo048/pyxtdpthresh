"""Forward orthogonal deviations, unbalanced panels, time effects and history against Stata (F).

The real command is run with ``exportgmm`` on the Hansen panel (100 firms, 1973-1981) for
``method(fod)``, ``td`` in first differences and in forward deviations, unbalanced panels and
``history(sample)``.  Stata exports the instrument matrix ``Z`` of the final stack, the
regressors ``X`` at the estimated threshold, the weight ``A`` paired with the estimate, the
counters of removed instrument columns, the estimate and the search bookkeeping.  Python must
reproduce all of them; invalid requests are compared by return code and message.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR, load_invest
from validation.compare import read_matrix
from validation.estimation_cases import BASE_ARGS, DERIVED_STATA, MAX_FIRM, MAX_YEAR, pack
from validation.sample_cases import DATA
from validation.search_cases import _E_NAME, _MATA_SC
from validation.spec_cases import parse_log, stata_command

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "transform_golden.json"
LOG = STATA_DIR / "_run_transform_cases.log"
EXTRA_STATA = ["gen double ageish = firm + year"]
#: Periods observed for very few units: single-equation periods (first differences) and
#: transformed dummies the projection saturates (forward deviations).
DATA2 = {
    **DATA,
    "s1": (
        ["drop if year == 1981 & firm > 1"],
        lambda df: df[~((df["year"] == 1981) & (df["firm"] > 1))],
    ),
    "s2": (
        ["drop if year == 1975 & firm > 3", "drop if year == 1979 & firm > 40"],
        lambda df: df[
            ~((df["year"] == 1975) & (df["firm"] > 3)) & ~((df["year"] == 1979) & (df["firm"] > 40))
        ],
    ),
}
FRAGMENTS = {
    "xd_td_gone": "removed by the unit and time effects",
    "xd_const_time": "td removes it",
}


@dataclass(frozen=True)
class TransformCase:
    """One run: a distortion of the data, an optional ``if`` and the call."""

    name: str
    data: str = "d0"
    args: dict[str, Any] = field(default_factory=dict)
    where: str | None = None
    key: str | None = None

    def full_args(self) -> dict[str, Any]:
        """Arguments of the call: the base, then the case."""
        return {**BASE_ARGS, "grid": 30, **self.args}


def _case(
    name: str, data: str = "d0", where: str | None = None, key: str | None = None, **a: Any
) -> TransformCase:
    return TransformCase(name, data, a, where, key)


_E = {"endogenous": ("tobin_q",)}
FOD = {"method": "fod"}
TD = {"time_effects": True}
CASES: tuple[TransformCase, ...] = (
    _case("fod_endog", **FOD, **_E),
    _case("fod_exog_only", **FOD),
    _case("fod_predet", **FOD, predetermined=("tobin_q",)),
    _case("fod_static", **FOD, static=True, x=("cashflow", "L.tobin_q")),
    _case("fod_collapse", **FOD, collapse=True, **_E),
    _case("fod_maxlag", **FOD, maxlag=(2, 5), **_E),
    _case("fod_iv", **FOD, iv=("z1", "z2"), **_E),
    _case("fod_kink", **FOD, kink=True, **_E),
    _case("fod_refine", **FOD, refine=2, grid=15, **_E),
    _case("fod_nocenter", **FOD, center=False, **_E),
    _case("fod_gaps", "d1", **FOD, **_E),
    _case("fod_missing_x", "d2", **FOD, **_E),
    _case("fod_short_units", "d3", **FOD, **_E),
    _case("fod_alternate_years", "d4", **FOD, **_E),
    _case("fod_missing_endog", "d5", **FOD, **_E),
    _case("fd_td_endog", **TD, **_E),
    _case("fd_td_exog_only", **TD),
    _case("fd_td_collapse", **TD, collapse=True, **_E),
    _case("fd_td_kink", **TD, kink=True, **_E),
    _case("fd_td_gaps", "d1", **TD, **_E),
    _case("fd_td_short_units", "d3", **TD, **_E),
    _case("fd_td_alternate_years", "d4", **TD, **_E),
    _case("fod_td_endog", **FOD, **TD, **_E),
    _case("fod_td_exog_only", **FOD, **TD),
    _case("fod_td_collapse", **FOD, **TD, collapse=True, **_E),
    _case("fod_td_static", **FOD, **TD, static=True, x=("cashflow", "L.tobin_q")),
    _case("fod_td_gaps", "d1", **FOD, **TD, **_E),
    _case("fod_td_short_units", "d3", **FOD, **TD, **_E),
    _case("fod_td_alternate_years", "d4", **FOD, **TD, **_E),
    _case("fd_history_panel", where="year >= 1976", **_E),
    _case("fd_history_sample", where="year >= 1976", history="sample", **_E),
    _case("fod_history_panel", where="year >= 1976", **FOD, **_E),
    _case("fod_history_sample", where="year >= 1976", history="sample", **FOD, **_E),
    _case("fd_iv_with_gaps", "d1", iv=("z1",), **_E),
    _case("fod_iv_with_gaps", "d1", iv=("z1",), **FOD, **_E),
    _case("fd_td_single_period", "s1", **TD, **_E),
    _case("fd_td_sparse_periods", "s2", **TD, **_E),
    _case("fod_td_single_period", "s1", **FOD, **TD, **_E),
    _case("fod_td_sparse_periods", "s2", **FOD, **TD, **_E),
    _case("fod_sparse_periods", "s2", **FOD, **_E),
    _case("fd_td_macro", x=("cashflow", "macro"), key="xd_const_time", **TD, **_E),
    _case("fod_td_macro", x=("cashflow", "macro"), key="xd_const_time", **FOD, **TD, **_E),
    _case("fd_td_gone", x=("cashflow", "ageish"), key="xd_td_gone", **TD, **_E),
    _case("fod_td_gone", x=("cashflow", "ageish"), key="xd_td_gone", **FOD, **TD, **_E),
    _case("fd_age_without_td", x=("cashflow", "ageish"), **_E),
)

_SCALARS = (
    "n_iv", "n_common", "n_dep", "n_dep_near", "dep_res", "w1_fallback", "gamma", "obj",
    "twostep", "n", "grid_admitted", "q_lo", "q_hi", "kink_refined", "stage1_gamma",
    "refine_iterations", "refine_added", "grid_effective",
)  # fmt: skip
_NAMES = {
    **_E_NAME,
    "n_iv": "N_iv",
    "n_common": "N_iv_common",
    "n_dep": "N_iv_dep",
    "n_dep_near": "N_iv_dep_near",
    "w1_fallback": "W1_fallback",
    "n": "N",
}


def frame(case: TransformCase) -> pd.DataFrame:
    """The panel after the distortion, as Stata has it."""
    df = load_invest(max_year=None, derived=True)
    df = df[(df["firm"] <= MAX_FIRM) & (df["year"] <= MAX_YEAR)].reset_index(drop=True)
    by_firm = df.groupby("firm")["invest"]
    df = df.assign(
        macro=np.log(df["year"] - 1960.0),
        ysum=by_firm.shift(2) + by_firm.shift(3),
        ageish=(df["firm"] + df["year"]).astype(float),
    )
    return DATA2[case.data][1](df).reset_index(drop=True)


def render_do(cases: tuple[TransformCase, ...] | None = None) -> str:
    """Do-file that runs every case with ``exportgmm`` and exports what Python must reproduce."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC]
    for c in cases:
        tag = f"../out/tc_{c.name}"
        scalars = ", ".join(f'pyx_sc("e({_NAMES.get(n, n)})")' for n in _SCALARS)
        command = stata_command({**c.full_args(), "export_gmm": True})
        if c.where:
            command = command.replace(", qx(", f" if {c.where}, qx(", 1)
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            f"keep if firm <= {MAX_FIRM} & year <= {MAX_YEAR}",
            *DERIVED_STATA,
            *EXTRA_STATA,
            *DATA2[c.data][0],
            f'display "@@CASE {c.name}"',
            f"capture noisily {command}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", ({scalars}))',
            f'    mata: pyx_export("{tag}_b.csv", st_matrix("e(b)"))',
            f'    mata: pyx_export("{tag}_vc.csv", st_matrix("e(V_cond)"))',
            f'    mata: pyx_export("{tag}_z.csv", xdpt_best_Z_f)',
            f'    mata: pyx_export("{tag}_x.csv", xdpt_best_X_f)',
            f'    mata: pyx_export("{tag}_a.csv", xdpt_best_A)',
            "}",
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/transform_cases.do``."""
    path = path or STATA_DIR / "transform_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/transform_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            tag = out_dir / f"tc_{c.name}"
            values = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(_SCALARS, (float(v) for v in values), strict=True))
            for key, suffix in (("b", "b"), ("vcond", "vc"), ("z", "z"), ("x", "x"), ("a", "a")):
                entry[key] = pack(read_matrix(Path(f"{tag}_{suffix}.csv")))
        cases[c.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
