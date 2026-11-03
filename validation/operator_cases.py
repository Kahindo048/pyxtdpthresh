"""Time-series operators against Stata (block E.1.2; files ``ts_*``).

Two checks come out of one Stata run:

* the canonical spelling Stata gives to each term (``syntax varlist(ts)``), including the
  expansion of ranges such as ``L(1/2).x``;
* the values of operated terms on a panel with calendar gaps (units 1 to 30 of the Hansen
  panel with the periods where ``mod(firm + 3*year, 7) == 0`` removed).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from validation.cases import OUT_DIR, STATA_DIR, load_invest

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "operators_golden.json"
LOG = STATA_DIR / "_run_operator_cases.log"
VALUES = OUT_DIR / "ts_values.csv"

SPELLINGS = [
    "l.cashflow",
    "l1.cashflow",
    "L2.cashflow",
    "ll.cashflow",
    "l2l.cashflow",
    "ld.cashflow",
    "l1d.cashflow",
    "d1.cashflow",
    "d.cashflow",
    "d2.cashflow",
    "f.cashflow",
    "f1.cashflow",
    "f2.cashflow",
    "s.cashflow",
    "s1.cashflow",
    "s12.cashflow",
    "L0.cashflow",
    "d0.cashflow",
    "l(1).cashflow",
    "l(2).cashflow",
    "l(0/2).cashflow",
    "l(1/2).cashflow",
    "l(1 3).cashflow",
    "ld2.cashflow",
    "L2D.cashflow",
    "dl.cashflow",
    "lf.cashflow",
    "fl.cashflow",
    "l0f.cashflow",
    "ls.cashflow",
    "ll2.cashflow",
    "L3L.cashflow",
    "d(1/2).cashflow",
    "LLL.cashflow",
    "FF.cashflow",
    "dd.cashflow",
    "ss.cashflow",
    "L(1/2)D.cashflow",
    "l01.cashflow",
    "L10.cashflow",
    "cashflow",
    "L.D2.cashflow",
    "S2D.cashflow",
    "DS2.cashflow",
    "ls2.cashflow",
    "fd.cashflow",
    "df.cashflow",
    "ldl.cashflow",
    "l(1/2)f.cashflow",
    "s2s3.cashflow",
    "F2L.cashflow",
    "D(1 2).cashflow",
]
VALUE_TERMS = [
    "L.cashflow",
    "L2.cashflow",
    "F.cashflow",
    "F2.cashflow",
    "D.cashflow",
    "D2.cashflow",
    "LD.cashflow",
    "DL.cashflow",
    "L2D.cashflow",
    "S2.cashflow",
    "S3.cashflow",
    "LS2.cashflow",
    "FD.cashflow",
    "DF.cashflow",
    "L3.cashflow",
    "L.D2.cashflow",
    "SS.cashflow",
    "S2D.cashflow",
    "LF.cashflow",
]


def render_do() -> str:
    """Do-file that prints the canonical spellings and exports the operated values."""
    lines = [
        "version 17",
        "set more off",
        "clear all",
        "capture program drop pyx_canon",
        "program define pyx_canon",
        "    syntax varlist(min=1 ts)",
        '    display "@@CANON `varlist\'"',
        "end",
        'use "../data/invest.dta", clear',
        "xtset firm year",
    ]
    for term in SPELLINGS:
        lines += [
            f'display "@@IN {term}"',
            f"capture noisily pyx_canon {term}",
            'display "@@RC " _rc',
        ]
    lines += [
        'use "../data/invest.dta", clear',
        "xtset firm year",
        "keep if firm <= 30",
        "drop if mod(firm + 3*year, 7) == 0",
        "sort firm year",
    ]
    for i, term in enumerate(VALUE_TERMS, start=1):
        lines.append(f"quietly gen double pyxv{i} = {term}")
    lines += [
        "keep firm year cashflow pyxv*",
        f'export delimited using "../out/{VALUES.name}", replace',
        "exit, clear",
    ]
    return "\n".join(lines) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/operator_cases.do``."""
    path = path or STATA_DIR / "operator_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


def parse_log(text: str) -> dict[str, dict[str, object]]:
    """Canonical spelling and return code of each input spelling."""
    out: dict[str, dict[str, object]] = {}
    current = None
    canon = ""
    for line in text.splitlines():
        if line.startswith("@@IN "):
            current, canon = line[5:].strip(), ""
        elif line.startswith("@@CANON") and current is not None:
            canon = line[7:].strip()
        elif line.startswith("@@RC ") and current is not None:
            out[current] = {"canonical": canon, "rc": int(line[5:].strip())}
            current = None
    return out


def panel_frame() -> pd.DataFrame:
    """The sample the Stata run used, as a data frame."""
    df = load_invest(max_year=None, derived=False)
    df = df[df["firm"] <= 30]
    df = df[(df["firm"] + 3 * df["year"]) % 7 != 0]
    return df.sort_values(["firm", "year"]).reset_index(drop=True)


def freeze(log: Path = LOG, path: Path = GOLDEN, values: Path = VALUES) -> Path:
    """Freeze the canonical spellings and the operated values."""
    table = pd.read_csv(values, na_values=["."])
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/operator_cases.py"},
        "canonical": parse_log(log.read_text(encoding="utf-8", errors="replace")),
        "terms": list(VALUE_TERMS),
        "values": {
            term: [None if np.isnan(v) else float(v) for v in table[f"pyxv{i}"]]
            for i, term in enumerate(VALUE_TERMS, start=1)
        },
        "keys": {"firm": table["firm"].tolist(), "year": table["year"].tolist()},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
