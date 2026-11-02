"""Validation of the xthenreg data and instruments (block D.1; files ``dz_*``).

The Stata side runs the **verbatim** first step of ``maincode_0719`` (sample, reshaping,
``moment_mat``, ``Z_mat``, ``inst()``) and exports ``N``, ``T``, ``y_mat``, ``q_mat``, the
regressor blocks, ``moment_mat`` and ``Z_mat``; the whole Mata source of ``xthenreg.ado`` is
compiled in the do-file so that every helper is the original one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from validation.cases import (
    _MATA_EXPORT,
    OUT_DIR,
    STATA_DIR,
    XthenregCase,
    load_invest,
)
from validation.compare import read_matrix

ADO = Path.home() / "ado" / "plus" / "x" / "xthenreg.ado"
GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "design_golden.json"
TAG = "dz"


@dataclass(frozen=True)
class DesignCase(XthenregCase):
    """An ``xthenreg`` specification plus data manipulations that test the sample logic."""

    drop_by_missing: bool = False  # cashflow missing for firms divisible by 10 in 1976
    min_year: int | None = None  # an ``if year >= min_year`` clause


def design_cases() -> tuple[DesignCase, ...]:
    """The six reference cases, plus missing values, an ``if`` clause and T = 15."""
    from validation.cases import XTHENREG_CASES

    base = tuple(DesignCase(**c.__dict__) for c in XTHENREG_CASES)
    common = {"y": "invest", "q": "debt", "x": ("cashflow",), "endogenous": ("tobin_q",)}
    extra = (
        DesignCase(tag="m1", drop_by_missing=True, **common),
        DesignCase(tag="m2", drop_by_missing=True, static=True, **common),
        DesignCase(tag="w1", min_year=1975, **common),
        DesignCase(tag="w2", min_year=1976, inst=("z1",), static=True, **common),
        DesignCase(tag="f1", max_year=None, **common),
        DesignCase(
            tag="f2", max_year=None, exogenous=("debt",), inst=("z1", "z2"), **{**common, "x": ()}
        ),
    )
    return base + extra


def _stata_source() -> tuple[str, str]:
    """Verbatim Mata source of the file, and the verbatim step-1 body of ``maincode_0719``."""
    lines = ADO.read_text(encoding="utf-8", errors="replace").splitlines()
    mata_start = next(i for i, ln in enumerate(lines) if ln.strip() == "mata:") + 1
    mata_end = max(i for i, ln in enumerate(lines) if ln.strip() == "end")
    first = next(i for i, ln in enumerate(lines) if "pan_var = st_global" in ln)
    last = next(i for i, ln in enumerate(lines) if "(End) ####//" in ln and i > first)
    return "\n".join(lines[mata_start:mata_end]), "\n".join(lines[first : last + 1])


_DUMP = """\
mata:
void dump_design(string scalar tag, string scalar vname, real scalar k_endo,
                 real scalar k_exo, real scalar grid_num, real scalar trim_rate,
                 real scalar flag_static, real scalar flag_inst, string scalar inst_list,
                 string scalar touse)
{
__BODY__
    pyx_export("../out/" + tag + "_scal.csv", (N \\ T \\ N_ori \\ rows(Z_mat) \\ cols(moment_mat)))
    pyx_export("../out/" + tag + "_y.csv", y_mat)
    pyx_export("../out/" + tag + "_q.csv", q_mat)
    pyx_export("../out/" + tag + "_x.csv", x_mat)
    pyx_export("../out/" + tag + "_moment.csv", moment_mat)
    pyx_export("../out/" + tag + "_Z.csv", Z_mat)
}
end
"""


def sample_condition(case: DesignCase) -> str:
    """Stata expression selecting the rows (marksample on y, q, x and the ``if`` clause)."""
    missing_check = " & ".join(f"!missing({v})" for v in (case.y, case.q, *case.x))
    clause = f" & year >= {case.min_year}" if case.min_year is not None else ""
    return missing_check + clause


def render_do(cases: tuple[DesignCase, ...] | None = None) -> str:
    """Do-file that builds the design of every case in Stata and exports it."""
    cases = design_cases() if cases is None else cases
    source, body = _stata_source()
    body_lines = "\n".join("    " + ln for ln in body.splitlines())
    out = ["version 17", "set more off", "clear all", "", _MATA_EXPORT]
    out += ["mata:", source, "end", "", _DUMP.replace("__BODY__", body_lines)]
    for c in cases:
        out += [
            'use "../data/invest.dta", clear',
            "xtset firm year",
            f"keep if year <= {c.max_year}" if c.max_year is not None else "* all years",
            "gen double z1 = cashflow*tobin_q + debt",
            "gen double z2 = ln(1 + tobin_q)",
        ]
        if c.drop_by_missing:
            out.append("replace cashflow = . if mod(firm, 10) == 0 & year == 1976")
        var_all = " ".join([c.y, c.q, *c.x, *c.endogenous, *c.exogenous])
        out += [
            "quietly xtset",
            f"gen byte touse = {sample_condition(c)}",
            f'mata: dump_design("{TAG}_{c.tag}", "{var_all}", {len(c.endogenous)}, '
            f"{len(c.exogenous)}, {c.grid_num}, {c.trim_rate:g}, {int(c.static)}, "
            f'{int(bool(c.inst))}, "{" ".join(c.inst) if c.inst else "."}", "touse")',
            "",
        ]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/design_cases.do``."""
    path = path or STATA_DIR / "design_cases.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def case_frame(case: DesignCase):  # noqa: ANN201
    """The same data manipulations as the do-file, with pandas."""
    df = load_invest(max_year=case.max_year)
    if case.drop_by_missing:
        df.loc[(np.mod(df["firm"], 10) == 0) & (df["year"] == 1976), "cashflow"] = np.nan
    return df


KINDS = ("scal", "y", "q", "x", "moment", "Z")


def python_results(case: DesignCase) -> dict[str, np.ndarray]:
    """Same objects as the Stata export, computed with the package."""
    from pyxtdpthresh.models.xthenreg.design import build_instruments, prepare_data

    df = case_frame(case)
    where = df["year"] >= case.min_year if case.min_year is not None else None
    data = prepare_data(
        df, case.y, case.q, case.x, case.endogenous, case.exogenous, case.inst,
        id="firm", time="year", where=where,
    )  # fmt: skip
    inst = build_instruments(data, static=case.static)
    n, t = data.n_units, data.n_periods
    x_stack = np.vstack([data.x[b] for b in range(data.k_1)])
    x_stack = np.where(np.isnan(x_stack), 1.0, x_stack)  # Mata's placeholder in column 1
    return {
        "scal": np.array(
            [n, t, n + data.n_units_ignored, inst.n_moments, inst.moment_counts.shape[1]], float
        ),
        "y": data.y,
        "q": data.q,
        "x": x_stack,
        "moment": inst.moment_counts.astype(float),
        "Z": inst.literal(),
    }


def stata_results(out_dir: Path = OUT_DIR) -> dict[str, dict[str, np.ndarray]]:
    """Exports of the Stata run, grouped by case."""
    return {
        c.tag: {k: read_matrix(out_dir / f"{TAG}_{c.tag}_{k}.csv") for k in KINDS}
        for c in design_cases()
    }


def fingerprint(a: np.ndarray) -> dict[str, list[float]]:
    """Compact, order-sensitive summary of a matrix: row sums, column sums, bilinear checksum.

    The full ``Z_mat`` of every case would weigh megabytes in the repository; these three
    summaries change if any entry, or the order of rows or columns, changes.
    """
    a = np.atleast_2d(np.asarray(a, dtype=float))
    left = np.cos(np.arange(1, a.shape[0] + 1))
    right = np.sin(np.arange(1, a.shape[1] + 1))
    return {
        "rows": a.sum(axis=1).tolist(),
        "cols": a.sum(axis=0).tolist(),
        "bilinear": [float(left @ a @ right)],
    }


FINGERPRINTED = ("y", "q", "x", "Z")


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze the Stata results into ``tests/golden/design_golden.json``."""
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/design_cases.py"},
        "stata": {
            t: {k: (fingerprint(v) if k in FINGERPRINTED else v.tolist()) for k, v in o.items()}
            for t, o in stata_results(out_dir).items()
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
