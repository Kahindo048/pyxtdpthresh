"""Description of the validation cases and generation of the matching Stata do-files.

Each case is described once.  The same description drives the Stata run (through
``render_xthenreg_do``) and the Python run, so both sides always use the same data,
sample and options.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"
STATA_DIR = ROOT / "stata"


# --------------------------------------------------------------------------- data
def load_invest(max_year: int | None = 1980, derived: bool = True) -> pd.DataFrame:
    """Hansen (1999) investment panel, optionally restricted to ``year <= max_year``.

    The derived columns ``z1`` and ``z2`` are the external instruments used by the cases;
    they are defined exactly as in the generated do-files.
    """
    df = pd.read_stata(DATA_DIR / "invest.dta")
    df["firm"] = df["firm"].astype("int64")
    df["year"] = df["year"].astype("int64")
    if max_year is not None:
        df = df[df["year"] <= max_year].copy()
    if derived:
        df["z1"] = df["cashflow"] * df["tobin_q"] + df["debt"]
        df["z2"] = np.log(1.0 + df["tobin_q"])
    return df.reset_index(drop=True)


# --------------------------------------------------------------------------- cases
@dataclass(frozen=True)
class XthenregCase:
    """One ``xthenreg`` specification."""

    tag: str
    y: str
    q: str
    x: tuple[str, ...] = ()
    endogenous: tuple[str, ...] = ()
    exogenous: tuple[str, ...] = ()
    inst: tuple[str, ...] = ()
    kink: bool = False
    static: bool = False
    grid_num: int = 100
    trim_rate: float = 0.4
    h_0: float | None = None
    boost: int = 0
    seed: int | None = None
    max_year: int | None = 1980

    def stata_command(self) -> str:
        """The ``xthenreg`` command line, as typed in Stata."""
        parts = ["xthenreg", self.y, self.q, *self.x]
        opts: list[str] = []
        if self.endogenous:
            opts.append(f"endogenous({' '.join(self.endogenous)})")
        if self.exogenous:
            opts.append(f"exogenous({' '.join(self.exogenous)})")
        if self.inst:
            opts.append(f"inst({' '.join(self.inst)})")
        opts.append(f"grid_num({self.grid_num})")
        opts.append(f"trim_rate({self.trim_rate:g})")
        if self.h_0 is not None:
            opts.append(f"h_0({self.h_0:g})")
        if self.boost:
            opts.append(f"boost({self.boost})")
        if self.static:
            opts.append("static")
        if self.kink:
            opts.append("kink")
        return " ".join(parts) + ", " + " ".join(opts)


XTHENREG_CASES: tuple[XthenregCase, ...] = (
    XthenregCase("c1", "invest", "debt", endogenous=("cashflow", "tobin_q", "debt"), grid_num=50),
    XthenregCase(
        "c2", "invest", "debt", endogenous=("cashflow", "tobin_q", "debt"), grid_num=50, kink=True
    ),
    XthenregCase(
        "c3",
        "invest",
        "debt",
        x=("cashflow",),
        endogenous=("tobin_q",),
        exogenous=("debt",),
        grid_num=40,
        trim_rate=0.3,
        static=True,
    ),
    XthenregCase(
        "c4",
        "invest",
        "debt",
        x=("cashflow",),
        endogenous=("tobin_q", "debt"),
        inst=("z1", "z2"),
        grid_num=50,
    ),
    XthenregCase(
        "c5",
        "invest",
        "debt",
        x=("cashflow",),
        endogenous=("tobin_q",),
        grid_num=40,
        trim_rate=0.3,
        static=True,
        kink=True,
    ),
    XthenregCase(
        "c6",
        "invest",
        "debt",
        x=("cashflow",),
        endogenous=("tobin_q",),
        exogenous=("debt",),
        grid_num=60,
        trim_rate=0.2,
    ),
)

_MATA_EXPORT = """\
mata:
void pyx_export(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
    fh = fopen(fname, "w")
    for (i = 1; i <= rows(M); i++) {
        line = strofreal(M[i,1], "%21.15g")
        for (j = 2; j <= cols(M); j++) line = line + "," + strofreal(M[i,j], "%21.15g")
        fput(fh, line)
    }
    fclose(fh)
}
end
"""

_SAVE_XTHENREG = """\
program define pyx_save_xthenreg
    args tag
    mata: pyx_export("../out/`tag'_b.csv", st_matrix("e(b)")')
    mata: pyx_export("../out/`tag'_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/`tag'_CI.csv", st_matrix("e(CI)"))
    mata: pyx_export("../out/`tag'_scal.csv", (st_numscalar("e(N)") \\ st_numscalar("e(T)") \\ st_numscalar("e(boots_p)")))
end
"""


def render_xthenreg_do(cases: tuple[XthenregCase, ...] = XTHENREG_CASES) -> str:
    """Do-file that runs every case in Stata and exports ``b``, ``V``, ``CI`` and scalars."""
    lines = [
        "version 17",
        "set more off",
        "clear all",
        "capture log close",
        "",
        _MATA_EXPORT,
        _SAVE_XTHENREG,
    ]
    for c in cases:
        lines += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            f"keep if year <= {c.max_year}" if c.max_year is not None else "* all years",
            "gen double z1 = cashflow*tobin_q + debt",
            "gen double z2 = ln(1 + tobin_q)",
        ]
        if c.seed is not None:
            lines.append(f"set seed {c.seed}")
        lines += [c.stata_command(), f"pyx_save_xthenreg {c.tag}", ""]
    lines.append("exit, clear")
    return "\n".join(lines) + "\n"


def write_xthenreg_do(path: Path | None = None) -> Path:
    """Write the generated do-file (default ``validation/stata/xthenreg_cases.do``)."""
    path = path or STATA_DIR / "xthenreg_cases.do"
    path.write_text(render_xthenreg_do(), encoding="ascii", newline="\n")
    return path
