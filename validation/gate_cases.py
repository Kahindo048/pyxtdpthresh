"""Validation gate of ``xthenreg`` (block D.5): variants, T = 15 and the real bootstrap command.

Every case is run in Stata with the real ``xthenreg`` command (``render_xthenreg_do``) and
frozen in ``tests/golden/gate_golden.json``.  The groups are

* ``gv``: ``grid_num`` in (40, 50, 60, 100) crossed with ``trim_rate`` in (0.2, 0.3, 0.4);
* ``gk``: the same sweep for the kink, dynamic and static;
* ``gt``: the full panel (T = 15), with jump, kink, static and external instruments;
* ``gb``: the bootstrap p-value of the command itself (``boost(100)`` after ``set seed``).
"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from validation.cases import OUT_DIR, STATA_DIR, XthenregCase, render_xthenreg_do
from validation.compare import load_stata

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "gate_golden.json"
GRIDS = (40, 50, 60, 100)
TRIMS = (0.2, 0.3, 0.4)
BOOT = 100
SEED = 2024

_BASE = {"y": "invest", "q": "debt", "x": ("cashflow",), "endogenous": ("tobin_q",)}


def gate_cases() -> tuple[XthenregCase, ...]:
    """All the cases of the gate."""
    out: list[XthenregCase] = []
    for i, (g, t) in enumerate(product(GRIDS, TRIMS), start=1):
        out.append(XthenregCase(f"gv{i:02d}", **_BASE, grid_num=g, trim_rate=t))
    out += [
        XthenregCase("gk1", **_BASE, kink=True, grid_num=100, trim_rate=0.2),
        XthenregCase("gk2", **_BASE, kink=True, static=True, grid_num=60, trim_rate=0.3),
        XthenregCase("gk3", **_BASE, kink=True, grid_num=40, trim_rate=0.4),
    ]
    full = {"max_year": None, "grid_num": 50}
    endo3 = ("cashflow", "tobin_q", "debt")
    out += [
        XthenregCase("gt1", "invest", "debt", endogenous=endo3, **full),
        XthenregCase("gt2", "invest", "debt", endogenous=endo3, kink=True, **full),
        XthenregCase("gt3", **_BASE, static=True, **full),
        XthenregCase(
            "gt4",
            "invest",
            "debt",
            x=("cashflow",),
            endogenous=("tobin_q", "debt"),
            inst=("z1", "z2"),
            **full,
        ),  # fmt: skip
    ]
    boot = {"y": "invest", "grid_num": 20, "boost": BOOT, "seed": SEED, "max_year": 1980}
    out += [
        XthenregCase("gb1", q="cashflow", endogenous=("debt",), static=True, **boot),
        XthenregCase("gb2", q="cashflow", endogenous=("debt",), **boot),
        XthenregCase(
            "gb3", q="tobin_q", endogenous=("cashflow", "tobin_q"), static=True, kink=True, **boot
        ),
        XthenregCase("gb4", q="debt", endogenous=("debt",), static=True, kink=True, **boot),
        XthenregCase("gb5", q="debt", endogenous=("debt",), kink=True, **boot),
    ]
    return tuple(out)


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/gate_cases.do``."""
    path = path or STATA_DIR / "gate_cases.do"
    path.write_text(render_xthenreg_do(gate_cases()), encoding="ascii", newline="\n")
    return path


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/gate_golden.json``."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/gate_cases.py"},
        "cases": {
            c.tag: {k: v.tolist() for k, v in load_stata(out_dir, c.tag).items()}
            for c in gate_cases()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
