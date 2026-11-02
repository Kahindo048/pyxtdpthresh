"""Validation of the Stata-compatible random number generator (block C.5; files ``rn_*``).

Stata (``set seed s``) is asked for long series of ``uniform()`` and ``invnormal(uniform())``
values, printed with 17 significant digits (enough to identify a double exactly), plus the
order in which a matrix is filled and the behaviour of consecutive calls.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from validation.cases import OUT_DIR, STATA_DIR
from validation.compare import read_matrix

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "rng_golden.json"
TAG = "rn"
SEEDS = (0, 1, 123, 12345, 2147483647)
N_DRAWS = 2000

_MATA = """\
mata:
void pyx_export17(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
    if (fileexists(fname)) unlink(fname)
    fh = fopen(fname, "w")
    for (i = 1; i <= rows(M); i++) {
        line = strtrim(strofreal(M[i,1], "%25.17g"))
        for (j = 2; j <= cols(M); j++) line = line + "," + strtrim(strofreal(M[i,j], "%25.17g"))
        fput(fh, line)
    }
    fclose(fh)
}

void dump(real scalar seed, real scalar n)
{
    string scalar tag
    real matrix u, u2
    tag = "../out/__TAG___s" + strofreal(seed, "%12.0f")
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_uniform.csv", uniform(n, 1))
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_normal.csv", invnormal(uniform(n, 1)))
    // matrix fill order: 3 x 4, then 5 more draws to show the stream continues
    stata("set seed " + strofreal(seed, "%12.0f"))
    u = uniform(3, 4)
    pyx_export17(tag + "_matrix.csv", u)
    pyx_export17(tag + "_after.csv", uniform(5, 1))
    // a row vector, as in invnormal(uniform(1, N)) of xthenreg
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_row.csv", uniform(1, 7))
    // runiform() and uniform() share one stream
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_runiform.csv", runiform(6, 1))
    // two successive normal blocks, as in a bootstrap loop
    stata("set seed " + strofreal(seed, "%12.0f"))
    pyx_export17(tag + "_boot1.csv", invnormal(uniform(1, 50)))
    pyx_export17(tag + "_boot2.csv", invnormal(uniform(1, 50)))
}
end
"""


def render_do() -> str:
    """Do-file that dumps the generator output for every seed."""
    body = ["version 17", "set more off", "clear all", "", _MATA.replace("__TAG__", TAG), "mata:"]
    body += [f"dump({seed}, {N_DRAWS})" for seed in SEEDS]
    body += ["end", "exit, clear"]
    return "\n".join(body) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/rng_cases.do``."""
    path = path or STATA_DIR / "rng_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


KINDS = ("uniform", "normal", "matrix", "after", "row", "runiform", "boot1", "boot2")


def stata_results(out_dir: Path = OUT_DIR) -> dict[int, dict[str, np.ndarray]]:
    """Exports of the Stata run, grouped by seed."""
    return {
        seed: {k: read_matrix(out_dir / f"{TAG}_s{seed}_{k}.csv") for k in KINDS} for seed in SEEDS
    }


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze the Stata draws into ``tests/golden/rng_golden.json`` (17 digits kept)."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/rng_cases.py"},
        "stata": {
            str(s): {k: v.tolist() for k, v in o.items()} for s, o in stata_results(out_dir).items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
