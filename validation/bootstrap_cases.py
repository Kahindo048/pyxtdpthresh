"""Bootstraps of ``xtdpthresh`` against Stata (block H): confidence set, linearity, tests.

The real command is run with ``rseed()``: every component restarts the generator at
``rseed + offset``, and Python reproduces Stata's Mersenne Twister, so both programs use the very
same Mammen weights.  Stata exports the bounds of the confidence set, the inversion table
``e(ci_grid)``, the segments, the p-values and the bookkeeping scalars.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix
from validation.estimation_cases import DERIVED_STATA, MAX_FIRM, MAX_YEAR, pack
from validation.point_cases import HELP
from validation.sample_cases import DATA
from validation.search_cases import _E_NAME, _MATA_SC
from validation.spec_cases import parse_log, stata_command
from validation.transform_cases import DATA2, EXTRA_STATA
from validation.variance_cases import QDISC_STATA, VarCase
from validation.variance_cases import frame as variance_frame

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "bootstrap_golden.json"
LOG = STATA_DIR / "_run_bootstrap_cases.log"
SEED = 20260611
BOOT = 99
FOD = {"method": "fod"}
TD = {"time_effects": True}
_E = {"endogenous": ("tobin_q",)}
XQ = ("cashflow", "debt")
ON = {"bootstrap": True, "n_boot": BOOT, "grid_ci": 40, "seed": SEED}


def _small(name: str, data: str = "d0", **a: Any) -> VarCase:
    return VarCase(name, "small", data, {**ON, **a})


def _full(name: str, data: str = "d0", **a: Any) -> VarCase:
    return VarCase(name, "full", data, {**HELP, **ON, "grid_ci": 40, **a})


CASES: tuple[VarCase, ...] = (
    _small("fd_jump", **_E),
    _small("fd_kink", kink=True, **_E),
    _small("fod_jump", **FOD, **_E),
    _small("fod_kink", **FOD, kink=True, **_E),
    _small("fd_td", **TD, **_E),
    _small("fod_td", **FOD, **TD, **_E),
    _small("fd_static", static=True, x=("cashflow", "L.tobin_q")),
    _small("fd_exog_only"),
    _small("fd_collapse", collapse=True, **_E),
    _small("fd_iv", iv=("z1", "z2"), **_E),
    _small("fd_gaps", "d1", **_E),
    _small("fd_short", "d3", **_E),
    _small("fd_one_step", "d4", **_E),
    _small("fod_one_step", "d4", **FOD, **_E),
    _small("fd_refine", refine=2, grid=15, **_E),
    _small("fd_quantile_grid", grid_type="quantile", **_E),
    _small("fd_level_90", level=90, **_E),
    _small("fd_no_linearity_test", linearity_test=False, **_E),
    _small("fd_small_boot", n_boot=19, **_E),
    _small("cont_fd", continuity_test=True, x=XQ, **_E),
    _small("cont_fod", continuity_test=True, x=XQ, **FOD, **_E),
    _small("cont_fd_td", continuity_test=True, x=XQ, **TD, **_E),
    _small(
        "cont_fd_static", continuity_test=True, static=True, x=("cashflow", "L.tobin_q", "debt")
    ),
    _small("cont_fd_one_step", "d4", continuity_test=True, x=XQ, **_E),
    _small("cont_fd_gaps", "d1", continuity_test=True, x=XQ, **_E),
    _small("cont_fd_collapse", continuity_test=True, collapse=True, x=XQ, **_E),
    _small("cont_without_q", continuity_test=True, **_E),
    _small("citest_inside", gamma_test=0.2, **_E),
    _small("citest_outside", gamma_test=0.45, **_E),
    _small("citest_kink", gamma_test=0.2, kink=True, **_E),
    _small("citest_fod", gamma_test=0.2, **FOD, **_E),
    _small("citest_one_step", "d4", gamma_test=0.2, **_E),
    _small("citest_with_tests", gamma_test=0.3, continuity_test=True, x=XQ, **_E),
    _small("citest_unseeded_subset", gamma_test=0.0, **_E),
    _small("coef_twostep", coef_boot="twostep", **_E),
    _small("coef_onestep", coef_boot="onestep", **_E),
    _small("coef_twostep_percentile", coef_boot="twostep", coef_ci_type="percentile", **_E),
    _small("coef_onestep_percentile", coef_boot="onestep", coef_ci_type="percentile", **_E),
    _small("coef_twostep_kink", coef_boot="twostep", kink=True, **_E),
    _small("coef_twostep_fod", coef_boot="twostep", **FOD, **_E),
    _small("coef_onestep_td", coef_boot="onestep", **TD, **_E),
    _small("coef_twostep_one_step_fit", "d4", coef_boot="twostep", **_E),
    _small("coef_twostep_refine", coef_boot="twostep", refine=2, grid=15, **_E),
    _small("coef_twostep_collapse", coef_boot="twostep", collapse=True, **_E),
    _small("coef_twostep_td", coef_boot="twostep", **TD, **_E),
    _small("unit_fd", boot_type="unit", **_E),
    _small("unit_gaps", "d1", boot_type="unit", **_E),
    _small("unit_collapse", boot_type="unit", collapse=True, **_E),
    _small("unit_nocenter", boot_type="unit", center=False, **_E),
    _small("unit_static", boot_type="unit", static=True, x=("cashflow", "L.tobin_q")),
    _small("unit_exog_only", boot_type="unit"),
    _small("unit_citest", boot_type="unit", gamma_test=0.2, **_E),
    _small("unit_quantile_grid", boot_type="unit", grid_type="quantile", **_E),
    _small("unit_kink", boot_type="unit", kink=True, **_E),
    _small("unit_fod", boot_type="unit", **FOD, **_E),
    _small("unit_td", boot_type="unit", **TD, **_E),
    _small("unit_one_step", "d4", boot_type="unit", **_E),
    _full("full_help"),
    _full("full_help_kink", kink=True),
    _full("full_help_fod", **FOD),
    _full("full_cont", continuity_test=True),
    _full("full_citest", gamma_test=0.25),
)

SCALARS = (
    "gamma", "twostep", "gamma_lo", "gamma_hi", "ci_empty", "ci_nseg", "ci_incomplete",
    "ci_unresolved", "boundary_warn", "pval_lin", "boot_linearity_valid", "rseed", "pval_cont",
    "boot_continuity_valid", "citest_gamma", "citest_D", "citest_crit", "citest_accept",
    "citest_draws", "citest_status", "citest_p", "boot_coef_B", "boot_coef_attempted",
    "boot_coef_failed", "boot_coef_twostep", "boot_grid_stage1", "boot_grid_stage2",
)  # fmt: skip
_NAMES = {**_E_NAME}
MATRICES = (
    ("grid", "e(ci_grid)"),
    ("segments", "e(ci_segments)"),
    ("bootci", "e(b_bootci)"),
)


def frame(case: VarCase) -> pd.DataFrame:
    """Panel of the case (same as the variance cases)."""
    return variance_frame(case)


def render_do(cases: tuple[VarCase, ...] | None = None) -> str:
    """Do-file that runs every case and exports the bootstrap results."""
    cases = CASES if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC]
    for c in cases:
        tag = f"../out/bc_{c.name}"
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
    """Write ``validation/stata/bootstrap_cases.do``."""
    path = path or STATA_DIR / "bootstrap_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/bootstrap_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in CASES:
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            tag = out_dir / f"bc_{c.name}"
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
