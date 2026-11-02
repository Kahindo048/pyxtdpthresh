"""Freeze the Stata reference results into ``tests/golden/golden_master.json``.

The frozen file lets the test suite run without Stata.  Run it after (re)generating the
Stata outputs with ``run_stata.ps1``.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from validation.compare import load_stata

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "golden_master.json"
OUT_DIR = Path(__file__).resolve().parent / "out"

META = {
    "stata": "Stata 17.0 MP (batch, PowerShell)",
    "xthenreg": "Seo, Kim and Kim (2019), Stata Journal 19(3), st0573",
    "xtdpthresh": "version 0.9.38 (29sep2026)",
}


def freeze(tags: list[str], out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> dict:
    """Write the golden master for ``tags`` and return it."""
    master = {
        "meta": {**META, "frozen_on": dt.date.today().isoformat()},
        "cases": {
            tag: {k: v.tolist() for k, v in load_stata(out_dir, tag).items()} for tag in tags
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master, indent=1), encoding="utf-8", newline="\n")
    return master


def load_golden(path: Path = GOLDEN) -> dict:
    """Read the frozen reference results."""
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    tags = sorted({p.name.split("_")[0] for p in OUT_DIR.glob("c*_b.csv")})
    master = freeze(tags)
    print(f"Frozen {len(master['cases'])} case(s): {', '.join(master['cases'])} -> {GOLDEN}")
