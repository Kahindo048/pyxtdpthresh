"""Variances and diagnostics of ``xtdpthresh`` against Stata (block G).

The real command is run, without the bootstraps, on the Hansen panel (100 firms, 1973-1981, and
the 565 firms, 1973-1987) for the jump and the kink model, ``vce(robust)`` and
``vce(windmeijer)``, ``bwscale()``, ``nocenter``, forward deviations, time effects and unbalanced
panels.  Stata exports ``e(b)``, ``e(V)``, ``e(V_cond)``, ``e(b_upper)``, ``e(V_upper)`` and the
scalars of the variance (``joint_vce``, ``gamma_bw``, ``q_nvals_bw``, ``vce_applied``,
``wind_same_threshold``), of the Hansen test and of the AR tests with their pieces.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix
from validation.estimation_cases import BASE_ARGS, DERIVED_STATA, MAX_FIRM, MAX_YEAR, pack
from validation.point_cases import HELP
from validation.point_cases import frame as full_frame
from validation.sample_cases import DATA
from validation.search_cases import _E_NAME, _MATA_SC, SearchCase
from validation.spec_cases import parse_log, stata_command
from validation.transform_cases import DATA2, EXTRA_STATA, TransformCase
from validation.transform_cases import frame as small_frame

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "variance_golden.json"
LOG = STATA_DIR / "_run_variance_cases.log"
QDISC_STATA = "gen double qdisc = floor(debt/0.25 + 0.5)*0.25"
FOD = {"method": "fod"}
TD = {"time_effects": True}
WIND = {"vce": "windmeijer"}
_E = {"endogenous": ("tobin_q",)}


@dataclass(frozen=True)
class VarCase:
    """One run: a panel, a distortion of the data and the call (Python arguments)."""

    name: str
    panel: str = "small"
    data: str = "d0"
    args: dict[str, Any] = field(default_factory=dict)

    def full_args(self) -> dict[str, Any]:
        """Arguments of the call: the base of the panel, then the case."""
        if self.panel == "full":
            base = {k: v for k, v in BASE_ARGS.items() if k != "grid"}
            return {**base, "export_gmm": False, **self.args}
        return {**BASE_ARGS, "grid": 30, "export_gmm": False, **self.args}


def _small(name: str, data: str = "d0", **a: Any) -> VarCase:
    return VarCase(name, "small", data, a)


def _full(name: str, data: str = "d0", **a: Any) -> VarCase:
    return VarCase(name, "full", data, {**HELP, **a})


CASES: tuple[VarCase, ...] = (
    _small("fd_jump", **_E),
    _small("fd_jump_wind", **WIND, **_E),
    _small("fd_kink", kink=True, **_E),
    _small("fd_kink_wind", kink=True, **WIND, **_E),
    _small("fd_kink_q_regressor", kink=True, x=("cashflow", "debt"), **_E),
    _small("fd_jump_q_regressor", x=("cashflow", "debt"), **_E),
    _small("fd_bw_small", bw_scale=0.8, **_E),
    _small("fd_bw_large", bw_scale=3.0, **_E),
    _small("fd_nocenter", center=False, **_E),
    _small("fd_nocenter_wind", center=False, **WIND, **_E),
    _small("fd_exog_only"),
    _small("fd_exog_only_wind", **WIND),
    _small("fd_predet", predetermined=("tobin_q",)),
    _small("fd_static", static=True, x=("cashflow", "L.tobin_q")),
    _small("fd_collapse_wind", collapse=True, **WIND, **_E),
    _small("fd_refine_wind", refine=2, grid=15, **WIND, **_E),
    _small("fd_iv_wind", iv=("z1", "z2"), **WIND, **_E),
    _small("fd_td", **TD, **_E),
    _small("fd_td_wind", **TD, **WIND, **_E),
    _small("fd_gaps", "d1", **_E),
    _small("fd_gaps_wind", "d1", **WIND, **_E),
    _small("fd_short_wind", "d3", **WIND, **_E),
    _small("fd_alternate_wind", "d4", **WIND, **_E),
    _small("fd_discrete_q", q="qdisc", **_E),
    _small("fod_jump", **FOD, **_E),
    _small("fod_jump_wind", **FOD, **WIND, **_E),
    _small("fod_kink", **FOD, kink=True, **_E),
    _small("fod_kink_wind", **FOD, kink=True, **WIND, **_E),
    _small("fod_td", **FOD, **TD, **_E),
    _small("fod_td_wind", **FOD, **TD, **WIND, **_E),
    _small("fod_gaps_wind", "d1", **FOD, **WIND, **_E),
    _small("fod_short", "d3", **FOD, **_E),
    _small("fod_alternate_wind", "d4", **FOD, **WIND, **_E),
    _small("fod_nocenter_wind", **FOD, center=False, **WIND, **_E),
    _small("fod_bw_small", **FOD, bw_scale=0.8, **_E),
    _full("full_help"),
    _full("full_help_wind", **WIND),
    _full("full_help_kink", kink=True),
    _full("full_help_kink_wind", kink=True, **WIND),
    _full("full_help_fod", **FOD),
    _full("full_help_fod_wind", **FOD, **WIND),
    _full("full_maxlag_2_10_wind", maxlag=(2, 10), **WIND),
    _full("full_unbalanced_gaps_wind", "d1", **WIND),
    _full("full_unbalanced_short", "d3"),
    _full("full_unbalanced_alternate_wind", "d4", **WIND),
)

SCALARS = (
    "gamma", "obj", "twostep", "n", "n_units", "n_clust", "n_switch", "hansen", "hansen_df",
    "hansen_p", "ar1", "ar1_p", "ar2", "ar2_p", "ar_joint", "ar1_cond", "ar2_cond", "ar1_b0",
    "ar1_T1", "ar1_TT", "ar2_b0", "ar2_T1", "ar2_TT", "joint_vce", "gamma_bw", "q_nvals_bw",
    "vce_applied", "wind_same_threshold",
)  # fmt: skip
_NAMES = {
    **_E_NAME,
    "n_units": "N_units",
    "n_clust": "N_clust",
    "n_switch": "N_switch",
    "ar1_T1": "ar1_T1",
}
MATRICES = (("b", "e(b)"), ("v", "e(V)"), ("vcond", "e(V_cond)"), ("bup", "e(b_upper)"),
            ("vup", "e(V_upper)"))  # fmt: skip


def frame(case: VarCase) -> pd.DataFrame:
    """The panel of the case after its distortion, as Stata has it."""
    if case.panel == "full":
        return full_frame(SearchCase(case.name, case.data, {}, None))
    df = small_frame(TransformCase(case.name, case.data))
    return df.assign(qdisc=np.floor(df["debt"] / 0.25 + 0.5) * 0.25)


def render_do(cases: tuple[VarCase, ...] | None = None) -> str:
    """Do-file that runs every case and exports what Python must reproduce."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC]
    for c in cases:
        tag = f"../out/vc_{c.name}"
        scalars = ", ".join(f'pyx_sc("e({_NAMES.get(n, n)})")' for n in SCALARS)
        if c.panel == "full":
            prep = ["egen double peer_q = mean(tobin_q), by(year)", *DATA[c.data][0]]
        else:
            prep = [
                f"keep if firm <= {MAX_FIRM} & year <= {MAX_YEAR}",
                *DERIVED_STATA,
                *EXTRA_STATA,
                QDISC_STATA,
                *DATA2[c.data][0],
            ]
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            *prep,
            f'display "@@CASE {c.name}"',
            f"capture noisily {stata_command(c.full_args())}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", ({scalars}))',
            *[
                f'    mata: pyx_export("{tag}_{key}.csv", st_matrix("{name}"))'
                for key, name in MATRICES
            ],
            "}",
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/variance_cases.do``."""
    path = path or STATA_DIR / "variance_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/variance_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            tag = out_dir / f"vc_{c.name}"
            values = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(SCALARS, (float(v) for v in values), strict=True))
            for key, _ in MATRICES:
                entry[key] = pack(read_matrix(Path(f"{tag}_{key}.csv")))
        cases[c.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
