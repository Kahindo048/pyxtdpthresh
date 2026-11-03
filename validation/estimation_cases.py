"""Instruments and fixed-threshold GMM of ``xtdpthresh`` against Stata (E.3 and E.4).

The real command is run with ``exportgmm`` on the Hansen panel (100 firms, 1973-1981).  Stata
exports the instrument matrix of the final stack ``Z``, the regressors at the estimated threshold
``X``, the weight matrix paired with the reported estimate ``A``, the counters of removed
instrument columns, ``e(b)``, ``e(obj)`` and the conditional variance ``e(V_cond)``.  Python
rebuilds the instruments from the data and must reproduce ``Z`` and ``X`` entry by entry; then,
given Stata's own ``A``, it must reproduce ``e(b)``, ``e(obj)`` and ``e(V_cond)``.  Finally, when
its own second-step weight at the estimated threshold equals ``A``, the whole two-step chain is
checked as well.
"""

from __future__ import annotations

import base64
import json
import zlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR, load_invest
from validation.compare import read_matrix
from validation.sample_cases import DATA
from validation.spec_cases import parse_log, stata_command

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "estimation_golden.json"
LOG = STATA_DIR / "_run_estimation_cases.log"
MAX_FIRM, MAX_YEAR = 100, 1981
BASE_ARGS: dict[str, Any] = {
    "y": "invest",
    "x": ("cashflow",),
    "q": "debt",
    "bootstrap": False,
    "grid": 10,
    "export_gmm": True,
}

#: Stata lines that create the derived variables, and their pandas counterpart.
DERIVED_STATA = [
    "gen double z1 = cashflow*tobin_q + debt",
    "gen double z2 = ln(1 + tobin_q)",
    "gen double macro = ln(year - 1960)",
    "gen double ysum = L2.invest + L3.invest",
]


@dataclass(frozen=True)
class EstCase:
    """One run: a distortion of the data and the call (Python arguments)."""

    name: str
    data: str = "d0"
    args: dict[str, Any] = field(default_factory=dict)

    def full_args(self) -> dict[str, Any]:
        """The arguments of the call, base included."""
        return {**BASE_ARGS, **self.args}


def _case(name: str, data: str = "d0", **args: Any) -> EstCase:
    return EstCase(name, data, args)


CASES: tuple[EstCase, ...] = (
    _case("endog", endogenous=("tobin_q",)),
    _case("exog_only"),
    _case("predet", predetermined=("tobin_q",)),
    _case("endog_predet", x=(), endogenous=("tobin_q",), predetermined=("cashflow",)),
    _case("exogenous_option", x=(), exogenous=("cashflow", "tobin_q")),
    _case("static", static=True, x=("cashflow", "L.tobin_q")),
    _case("static_endog", static=True, endogenous=("tobin_q",)),
    _case("collapse", collapse=True, endogenous=("tobin_q",)),
    _case("maxlag_collapse", maxlag=(3, 6), collapse=True, endogenous=("tobin_q",)),
    _case("maxlag_2_5", maxlag=(2, 5), endogenous=("tobin_q",)),
    _case("maxlag_1_2", maxlag=(1, 2), endogenous=("tobin_q",), predetermined=("cashflow",), x=()),
    _case("maxlag_4_4", maxlag=(4, 4), endogenous=("tobin_q",)),
    _case("iv_one", iv=("z1",)),
    _case("iv_two_collapse", iv=("z1", "z2"), iv_collapse=True, endogenous=("tobin_q",)),
    _case("iv_two", iv=("z1", "z2"), collapse=False, endogenous=("tobin_q",)),
    _case("iv_with_collapse", iv=("z1",), collapse=True),
    _case("kink", kink=True, endogenous=("tobin_q",)),
    _case("nocenter", center=False, endogenous=("tobin_q",)),
    _case("unbalanced_gaps", "d1", endogenous=("tobin_q",)),
    _case("unbalanced_missing_x", "d2", endogenous=("tobin_q",)),
    _case("unbalanced_short_units", "d3", endogenous=("tobin_q",)),
    _case("unbalanced_alternate_years", "d4", endogenous=("tobin_q",)),
    _case("unbalanced_missing_endog", "d5", endogenous=("tobin_q",)),
    _case("common_variable", x=("cashflow", "macro")),
    _case("common_variable_collapse", x=("cashflow", "macro"), collapse=True),
    _case("duplicate_endog_lag", endogenous=("tobin_q", "L.tobin_q")),
    _case("duplicate_predetermined_ylag", predetermined=("L2.invest", "L3.invest")),
    _case("dependent_iv", iv=("ysum",), endogenous=("tobin_q",)),
)

FRAGMENTS: dict[str, str] = {}


def _derived(df: pd.DataFrame) -> pd.DataFrame:
    """Derived columns, as the Stata lines in :data:`DERIVED_STATA` build them."""
    by_firm = df.groupby("firm")["invest"]
    return df.assign(
        macro=np.log(df["year"] - 1960.0),
        ysum=by_firm.shift(2) + by_firm.shift(3),
    )


def frame(case: EstCase) -> pd.DataFrame:
    """The panel after the distortion, as Stata has it."""
    df = load_invest(max_year=None, derived=True)
    df = df[(df["firm"] <= MAX_FIRM) & (df["year"] <= MAX_YEAR)].reset_index(drop=True)
    df = _derived(df)
    distort: Callable[[pd.DataFrame], pd.DataFrame] = DATA[case.data][1]
    return distort(df).reset_index(drop=True)


def render_do(cases: tuple[EstCase, ...] | None = None) -> str:
    """Do-file that runs every case with ``exportgmm`` and exports what Python must reproduce."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT]
    for c in cases:
        tag = f"../out/ec_{c.name}"
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            f"keep if firm <= {MAX_FIRM} & year <= {MAX_YEAR}",
            *DERIVED_STATA,
            *DATA[c.data][0],
            f'display "@@CASE {c.name}"',
            f"capture noisily {stata_command(c.full_args())}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", (st_numscalar("e(N_iv)"), '
            'st_numscalar("e(N_iv_common)"), st_numscalar("e(N_iv_dep)"), '
            'st_numscalar("e(N_iv_dep_near)"), st_numscalar("e(iv_dep_res)"), '
            'st_numscalar("e(W1_fallback)"), st_numscalar("e(gamma)"), st_numscalar("e(obj)"), '
            'st_numscalar("e(estimator_twostep)"), st_numscalar("e(N)")))',
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
    """Write ``validation/stata/estimation_cases.do``."""
    path = path or STATA_DIR / "estimation_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def pack(array: np.ndarray) -> dict[str, Any]:
    """Array as zlib-compressed little-endian doubles, for the golden file."""
    flat = np.ascontiguousarray(array, dtype="<f8")
    return {
        "shape": list(flat.shape),
        "data": base64.b64encode(zlib.compress(flat.tobytes())).decode(),
    }


def unpack(entry: dict[str, Any]) -> np.ndarray:
    """Inverse of :func:`pack`."""
    raw = zlib.decompress(base64.b64decode(entry["data"]))
    return np.frombuffer(raw, dtype="<f8").reshape(entry["shape"]).copy()


_SCALARS = (
    "n_iv", "n_common", "n_dep", "n_dep_near", "dep_res", "w1_fallback", "gamma", "obj",
    "twostep", "n",
)  # fmt: skip


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/estimation_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            tag = out_dir / f"ec_{c.name}"
            scalars = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(_SCALARS, (float(v) for v in scalars), strict=True))
            for key, suffix in (("b", "b"), ("vcond", "vc"), ("z", "z"), ("x", "x"), ("a", "a")):
                entry[key] = pack(read_matrix(Path(f"{tag}_{suffix}.csv")))
        cases[c.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
