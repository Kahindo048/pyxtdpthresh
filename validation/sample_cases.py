"""Estimation sample and first-difference equations of ``xtdpthresh`` against Stata (E.2).

The real command is run (point estimate only, ``noboot``) on the Hansen panel after a
deterministic distortion (calendar gaps, missing values, one-observation units, alternating
years...).  Stata exports the counts it reports (``e(N)``, ``e(N_stack)``, ``e(N_units)``) and
``e(sample)``, the exact set of rows that formed an equation, and Python must reproduce them.
Invalid samples are compared by return code and by the Stata message that identifies the rule.
Every specification has an exogenous regressor, so no equation is dropped for lack of an
instrument and the equations are exactly the first-difference candidates.
"""

from __future__ import annotations

import base64
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR, load_invest
from validation.compare import read_matrix
from validation.spec_cases import parse_log, stata_command

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "sample_golden.json"
LOG = STATA_DIR / "_run_sample_cases.log"
BASE_ARGS: dict[str, Any] = {
    "y": "invest",
    "x": ("cashflow",),
    "q": "debt",
    "bootstrap": False,
    "grid": 10,
}

#: Stata lines and pandas function of each distortion of the Hansen panel.
DATA: dict[str, tuple[list[str], Callable[[pd.DataFrame], pd.DataFrame]]] = {
    "d0": ([], lambda df: df),
    "d1": (
        ["drop if mod(firm + 3*year, 11) == 0"],
        lambda df: df[(df["firm"] + 3 * df["year"]) % 11 != 0],
    ),
    "d2": (
        ["replace cashflow = . if mod(firm*year, 13) == 0"],
        lambda df: df.assign(cashflow=df["cashflow"].where((df["firm"] * df["year"]) % 13 != 0)),
    ),
    "d3": (
        ["drop if firm <= 10 & year > 1973", "drop if firm >= 11 & firm <= 20 & year > 1974"],
        lambda df: df[
            ~((df["firm"] <= 10) & (df["year"] > 1973))
            & ~((df["firm"] >= 11) & (df["firm"] <= 20) & (df["year"] > 1974))
        ],
    ),
    "d4": (
        ["drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0"],
        lambda df: df[~((df["firm"] >= 11) & (df["firm"] <= 40) & (df["year"] % 2 == 0))],
    ),
    "d5": (
        ["replace tobin_q = . if firm <= 50 & year == 1975"],
        lambda df: df.assign(
            tobin_q=df["tobin_q"].where(~((df["firm"] <= 50) & (df["year"] == 1975)))
        ),
    ),
    "d6": (
        ["drop if firm > 3 & year != 1980"],
        lambda df: df[~((df["firm"] > 3) & (df["year"] != 1980))],
    ),
}
DERIVED = [
    "gen double cu = firm",
    "gen double ct = year",
    "gen double qm = .",
    "gen double qone = 1",
]


@dataclass(frozen=True)
class SampleCase:
    """One run: a distortion of the data and the call (Python arguments)."""

    name: str
    data: str = "d0"
    args: dict[str, Any] = field(default_factory=dict)
    where: str | None = None
    key: str | None = None  # rule expected from the Python side when the sample is invalid

    def full_args(self) -> dict[str, Any]:
        """The arguments of the call, base included."""
        return {**BASE_ARGS, **self.args}


_SPECS: dict[str, dict[str, Any]] = {
    "dyn": {"endogenous": ("tobin_q",)},
    "dynw": {"endogenous": ("tobin_q",)},
    "dyns": {"endogenous": ("tobin_q",), "history": "sample"},
    "ops": {"x": ("cashflow", "L.tobin_q"), "static": True},
}
_WHERE = {"dyn": None, "dynw": "year >= 1976", "dyns": "year >= 1976", "ops": "year >= 1976"}


def sample_cases() -> tuple[SampleCase, ...]:
    """Distorted panels under four specifications, plus invalid samples."""
    cases = [
        SampleCase(f"{data}_{spec}", data, dict(_SPECS[spec]), _WHERE[spec])
        for data in DATA
        for spec in _SPECS
        if data != "d6"  # d6 keeps three units: it is the invalid case e_few_after_drop
    ]
    cases += [
        SampleCase("e_const_unit", args={"x": ("cu",)}, key="xd_const_unit"),
        SampleCase("e_const_time", args={"x": ("ct",), "time_effects": True}, key="xd_const_time"),
        SampleCase("e_q_const_unit", args={"q": "cu"}, key="xd_q_const_unit"),
        SampleCase("e_q_const_time", args={"q": "ct", "time_effects": True}, key="xd_q_const_time"),
        SampleCase("e_few_units", where="firm <= 4", key="xd_few_units"),
        SampleCase("e_q_missing", args={"q": "qm"}, key="no_usable_obs"),
        SampleCase("e_x_missing", args={"x": ("qm",)}, key="no_usable_obs"),
        SampleCase("e_few_after_drop", "d6", key="xd_few_units"),
        SampleCase("ok_time_effects", args={"time_effects": True}),
    ]
    return tuple(cases)


FRAGMENTS = {
    "xd_const_unit": "of the estimation sample",
    "xd_const_time": "td removes it",
    "xd_q_const_unit": "the regime indicator is removed by the",
    "xd_q_const_time": "td removes the regime indicator",
    "xd_few_units": "need >= 5 units",
    "no_usable_obs": "no usable complete-case observations",
}


def frame(case: SampleCase) -> pd.DataFrame:
    """The Hansen panel after the distortion and with the derived columns, as Stata has it."""
    df = load_invest(max_year=None, derived=False)
    df = DATA[case.data][1](df).reset_index(drop=True)
    return df.assign(cu=df["firm"].astype(float), ct=df["year"].astype(float), qm=np.nan, qone=1.0)


def render_do(cases: tuple[SampleCase, ...] | None = None) -> str:
    """Do-file that runs every case and exports counts and ``e(sample)``."""
    cases = sample_cases() if cases is None else cases
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT]
    for c in cases:
        cond = f" if {c.where}" if c.where else ""
        command = stata_command(c.full_args()).replace(", qx(", f"{cond}, qx(", 1)
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            *DATA[c.data][0],
            *DERIVED,
            f'display "@@CASE {c.name}"',
            f"capture noisily {command}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("../out/sc_{c.name}.csv", (st_numscalar("e(N)"), '
            'st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))',
            "    quietly gen byte pyxes = e(sample)",
            f'    mata: pyx_export("../out/sc_{c.name}_es.csv", st_data(., "pyxes"))',
            "    drop pyxes",
            "}",
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/sample_cases.do``."""
    path = path or STATA_DIR / "sample_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def _pack(mask: np.ndarray) -> str:
    return base64.b64encode(np.packbits(mask.astype(bool)).tobytes()).decode()


def unpack(text: str, n: int) -> np.ndarray:
    """Inverse of the packing used in the golden file."""
    bits = np.unpackbits(np.frombuffer(base64.b64decode(text), dtype=np.uint8))
    return bits[:n].astype(bool)


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/sample_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for c in sample_cases():
        entry: dict[str, Any] = dict(parsed[c.name])
        if entry["rc"] == 0:
            counts = read_matrix(out_dir / f"sc_{c.name}.csv").ravel()
            sample = read_matrix(out_dir / f"sc_{c.name}_es.csv").ravel()
            entry.update(
                n=int(counts[0]), n_stack=int(counts[1]), n_units=int(counts[2]),
                size=int(sample.size), sample=_pack(sample == 1),
            )  # fmt: skip
        cases[c.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
