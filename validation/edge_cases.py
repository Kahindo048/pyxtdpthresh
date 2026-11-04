"""Edge cases of ``xtdpthresh`` against Stata (K.1.4): the cases a user is most likely to get wrong.

The same hostile panels go through the real command in Stata and through the package: minimal
panels, a threshold variable that is constant, almost constant, binary or takes few values, an
empty admissible regime, dependent regressors and instruments, more instruments than units, and a
constant or null outcome.  Stata gives a return code (0 for success) and, on success, the
estimates; the package must give the same code (``stata_code`` of its error) and the same numbers.

    python -m validation.edge_cases            # write the data and the do-file
    python -m validation.edge_cases --freeze   # freeze the Stata log into the golden files
"""

from __future__ import annotations

import gzip
import io
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pyxtdpthresh import simulate_panel
from validation.cases import STATA_DIR
from validation.spec_cases import stata_command

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "validation" / "data" / "edge"
GOLDEN = ROOT / "tests" / "golden" / "edge_golden.json"
PANELS = ROOT / "tests" / "golden" / "edge_panels.csv.gz"
LOG = STATA_DIR / "_run_edge_cases.log"
SEED = 7
SCALARS = ("gamma", "N", "N_units", "N_iv", "estimator_twostep", "gamma_lo", "gamma_hi")
_BOOT = {"n_boot": 99, "grid_ci": 20, "seed": SEED}
_OFF = {"bootstrap": False}


def tiny(n: int, t: int, seed: int = 2) -> pd.DataFrame:
    """A normal-noise panel of ``n`` units and ``t`` periods."""
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "id": np.repeat(np.arange(1, n + 1), t),
            "t": np.tile(np.arange(1, t + 1), n),
            "y": rng.normal(size=n * t),
            "q": rng.normal(size=n * t),
        }
    )


def base() -> pd.DataFrame:
    """The reference simulated panel (60 units, 6 periods)."""
    return simulate_panel("gong_seo", 60, 6, seed=1)


def with_columns(frame: pd.DataFrame, **columns: Any) -> pd.DataFrame:
    """Return a copy of ``frame`` with columns replaced or added."""
    out = frame.copy()
    for name, values in columns.items():
        out[name] = values(out) if callable(values) else values
    return out


@dataclass(frozen=True)
class EdgeCase:
    """One panel and one call."""

    name: str
    frame: pd.DataFrame = field(repr=False)
    x: tuple[str, ...] = ()
    options: dict[str, Any] = field(default_factory=dict)

    def arguments(self) -> dict[str, Any]:
        """The arguments of the call, in the names of the package."""
        return {"y": "y", "x": self.x, "q": "q", **self.options}


def cases() -> tuple[EdgeCase, ...]:
    """Every case, deterministic."""
    b, rng = base(), np.random.default_rng(0)
    x1 = rng.normal(size=len(b))
    median = b["q"].median()
    quartiles = np.quantile(b["q"], [0.25, 0.5, 0.75])
    return (
        EdgeCase("min_n1_t5", tiny(1, 5), options=_OFF),
        EdgeCase("min_n2_t4", tiny(2, 4), options=_OFF),
        EdgeCase("min_n3_t3", tiny(3, 3), options=_OFF),
        EdgeCase("min_n4_t4", tiny(4, 4), options=_OFF),
        EdgeCase("min_n5_t2", tiny(5, 2), options=_OFF),
        EdgeCase("min_n20_t3", tiny(20, 3), options=_OFF),
        EdgeCase("minregime_huge", b, options={**_OFF, "min_regime": 10_000}),
        EdgeCase("trim_049", b, options={**_OFF, "trim": 0.49}),
        EdgeCase("q_constant", with_columns(b, q=1.0), options=_OFF),
        EdgeCase(
            "q_rare_ones",
            with_columns(b, q=lambda d: (np.arange(len(d)) % 50 == 0) * 1.0),
            options=_OFF,
        ),  # fmt: skip
        EdgeCase("q_binary", with_columns(b, q=lambda d: (d["q"] > median) * 1.0), options=_OFF),
        EdgeCase(
            "q_four_values",
            with_columns(b, q=lambda d: np.digitize(d["q"], quartiles) * 1.0),
            options=_BOOT,
        ),  # fmt: skip
        EdgeCase("x_duplicate", with_columns(b, x1=x1, x2=2 * x1), ("x1", "x2"), _OFF),
        EdgeCase("iv_equals_x", with_columns(b, x1=x1, z=x1), ("x1",), {**_OFF, "iv": ("z",)}),
        EdgeCase("x_constant", with_columns(b, c=3.0), ("c",), _OFF),
        EdgeCase("units_fewer_than_iv", simulate_panel("gong_seo", 8, 8, seed=3), options=_OFF),
        EdgeCase(
            "units_fewer_than_iv_boot", simulate_panel("gong_seo", 8, 8, seed=3), options=_BOOT
        ),
        EdgeCase("y_zero", with_columns(b, y=0.0), options=_OFF),
        EdgeCase("y_constant", with_columns(b, y=float(b["y"].iloc[0])), options=_OFF),
    )


def stata_line(case: EdgeCase) -> str:
    """The Stata command of one case."""
    return stata_command({**case.arguments(), "x": case.x})


def render_do() -> str:
    """Do-file that runs every case with ``capture`` and prints its return code and scalars."""
    out = ["version 17", "set more off", "clear all"]
    for case in cases():
        out += [
            f'display "@@CASE {case.name}"',
            f'import delimited using "../data/edge/{case.name}.csv", clear',
            "xtset id t",
            f"capture noisily {stata_line(case)}",
            'display "@@RC " _rc',
        ]
        out += [
            f'if _rc == 0 display "@@S {name} " %21.15g e({name})' for name in SCALARS
        ]  # one short line per scalar: Stata wraps long lines in the middle of a number
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_data() -> None:
    """Write the panels as CSV for Stata and as one compressed file for the tests."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    for case in cases():
        case.frame.to_csv(DATA_DIR / f"{case.name}.csv", index=False)
        parts.append(case.frame.assign(case=case.name))
    buffer = io.StringIO()
    pd.concat(parts, ignore_index=True).to_csv(buffer, index=False)
    PANELS.write_bytes(gzip.compress(buffer.getvalue().encode("utf-8"), mtime=0))


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/edge_cases.do`` (and the data it reads)."""
    write_data()
    path = path or STATA_DIR / "edge_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


def parse_log(text: str) -> dict[str, dict[str, Any]]:
    """Return ``{case: {"rc": int, "scalars": {...}}}`` from the Stata log."""
    results: dict[str, dict[str, Any]] = {}
    name = ""
    for line in text.splitlines():
        if line.startswith("@@CASE "):
            name = line[7:].strip()
            results[name] = {"rc": None, "scalars": {}}
        elif line.startswith("@@RC ") and name:
            results[name]["rc"] = int(line[5:].strip())
        elif line.startswith("@@S ") and name:
            _, key, value = line.split(None, 2)
            results[name]["scalars"][key] = None if value.strip() == "." else float(value)
    return results


def freeze(log: Path = LOG, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/edge_golden.json``."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/edge_cases.py"},
        "cases": parse_log(log.read_text(encoding="utf-8", errors="replace")),
    }
    path.write_text(json.dumps(master, indent=1), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    print(freeze() if "--freeze" in sys.argv else write_do())
