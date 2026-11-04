"""The examples of the help file of ``xtdpthresh``, run in Stata 17 and in Python, side by side (K.3.1).

Each example is the command printed in ``xtdpthresh.sthlp`` (section Examples), with the default
options of Stata: ``boot(299)``, ``gridci(100)``, ``grid(100)``.  The do-file runs them as written
on the panel of Hansen (1999) with the five extreme firms dropped, exports what ``e()`` holds and
the values ``predict`` returns, and :func:`freeze` stores it.  :func:`compare` runs the package on
the same data and returns one :class:`Row` per object; the golden test requires every row to agree
and :func:`report` writes the side-by-side tables (``docs/help_examples.md``).
"""

from __future__ import annotations

import gzip
import json
import math
import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from validation.cases import _MATA_EXPORT, DATA_DIR, OUT_DIR, STATA_DIR
from validation.compare import ATOL, RTOL, read_matrix
from validation.estimation_cases import pack, unpack
from validation.search_cases import _MATA_SC
from validation.spec_cases import parse_log, stata_command

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "help_examples_golden.json"
SAMPLE = ROOT / "tests" / "golden" / "help_examples_sample.csv.gz"
REPORT = ROOT / "docs" / "help_examples.md"
LOG = STATA_DIR / "_run_help_examples.log"
EXTREME_FIRMS = (137, 391, 407, 488, 538)
BASE = {
    "y": "invest",
    "x": (),
    "q": "debt",
    "endogenous": ("cashflow", "tobin_q", "debt"),
    "maxlag": (3, 8),
    "collapse": True,
}
SEED = 12345
#: The scalars of ``e()`` the examples compare, under the names of Stata and of the package.
SCALARS = (
    "N", "N_units", "N_clust", "N_iv", "N_iv_common", "N_iv_dep", "N_switch", "gamma", "obj",
    "gamma_lo", "gamma_hi", "ci_nseg", "ci_empty", "ci_incomplete", "boundary_warn", "level",
    "pval_lin", "citest_gamma", "citest_D", "citest_crit", "citest_accept", "citest_p",
    "citest_status", "citest_draws", "hansen", "hansen_df", "hansen_p", "ar1", "ar1_p", "ar2",
    "ar2_p", "ar_joint", "ar1_cond", "ar2_cond", "q_lo", "q_hi", "grid_admitted",
    "estimator_twostep", "W1_fallback", "joint_vce", "vce_applied", "gamma_bw", "q_nvals_bw",
    "kink_refined", "rseed",
)  # fmt: skip
#: Scalars that depend on the bootstrap: they are not compared when the example has ``noboot``.
BOOTSTRAP_SCALARS = frozenset(SCALARS[SCALARS.index("gamma_lo") : SCALARS.index("pval_lin") + 1]) | {
    "citest_gamma", "citest_D", "citest_crit", "citest_accept", "citest_p", "citest_status",
    "citest_draws", "rseed",
}  # fmt: skip
#: Matrices of ``e()``: key, Stata name.
MATRICES = (
    ("b", "e(b)"), ("V", "e(V)"), ("V_cond", "e(V_cond)"), ("b_upper", "e(b_upper)"),
    ("V_upper", "e(V_upper)"), ("ci_segments", "e(ci_segments)"), ("ci_grid", "e(ci_grid)"),
)  # fmt: skip


@dataclass(frozen=True)
class Example:
    """One command of the help file."""

    name: str
    title: str
    stata: str  # the command, as printed in the help
    args: dict[str, Any]  # the same call for the package
    data: str = "full"  # "full", "unbalanced" or "peer"
    predict: bool = False

    @property
    def bootstrap(self) -> bool:
        return bool(self.args.get("bootstrap", True))


_FD = "xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse"
EXAMPLES: tuple[Example, ...] = (
    Example(
        "point", "Point estimates and diagnostics", f"{_FD} noboot", {**BASE, "bootstrap": False}
    ),
    Example(
        "inference",
        "Full inference and the test of Hansen's threshold",
        f"{_FD} citest(0.0157) rseed(12345)",
        {**BASE, "gamma_test": 0.0157, "seed": SEED},
    ),
    Example(
        "lag2",
        "Instruments from lag 2",
        "xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(2 10) collapse "
        "rseed(12345)",
        {**BASE, "maxlag": (2, 10), "seed": SEED},
    ),
    Example("kink", "Kink model", f"{_FD} kink rseed(12345)", {**BASE, "kink": True, "seed": SEED}),
    Example(
        "unbalanced_fd",
        "Unbalanced panel, first differences",
        f"{_FD} method(fd) rseed(12345)",
        {**BASE, "method": "fd", "seed": SEED},
        data="unbalanced",
    ),
    Example(
        "unbalanced_fod",
        "Unbalanced panel, forward orthogonal deviations",
        f"{_FD} method(fod) rseed(12345)",
        {**BASE, "method": "fod", "seed": SEED},
        data="unbalanced",
    ),
    Example(
        "external_iv",
        "External instrument",
        "xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) iv(L2.peer_q) "
        "maxlag(3 8) collapse noboot",
        {**BASE, "iv": ("L2.peer_q",), "bootstrap": False},
        data="peer",
    ),
    Example(
        "predict",
        "Postestimation: residuals and regime",
        f"{_FD} noboot",
        {**BASE, "bootstrap": False},
        predict=True,
    ),
)
BY_NAME = {e.name: e for e in EXAMPLES}


# ------------------------------------------------------------------------------- Stata side
def render_do() -> str:
    """Do-file: the commands of the help, one after the other, with their results exported."""
    scalars = ", ".join(f'pyx_sc("e({n})")' for n in SCALARS)
    drop = ", ".join(str(f) for f in EXTREME_FIRMS)
    out = [
        "version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC,
        'use "../data/invest.dta", clear',
        "xtset firm year",
        f"drop if inlist(firm, {drop})",
    ]  # fmt: skip
    for ex in EXAMPLES:
        tag = f"../out/he_{ex.name}"
        if ex.data == "unbalanced":
            out += [
                "preserve", "set seed 20260418", "drop if runiform() < 0.15",
                "bysort firm: drop if _N < 4",
            ]  # fmt: skip
        if ex.data == "peer":
            out.append("egen double peer_q = mean(tobin_q), by(year)")
        out += [
            f'display "@@CASE {ex.name}"',
            f"capture noisily {ex.stata}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", ({scalars}))',
        ]
        out += [
            f'    mata: pyx_export("{tag}_{key}.csv", st_matrix("{name}"))'
            for key, name in MATRICES
        ]
        if ex.predict:
            out += [
                "    predict double ehat, residuals",
                "    predict byte upper, regime",
                f'    export delimited firm year ehat upper using "{tag}_predict.csv", replace',
                "    drop ehat upper",
            ]
        out.append("}")
        if ex.data == "unbalanced":
            out += [
                'export delimited firm year invest tobin_q cashflow debt using '
                '"../out/he_sample.csv", replace' if ex.name == "unbalanced_fd" else "",
                "restore",
            ]  # fmt: skip
        out.append("")
    out.append("exit, clear")
    return "\n".join(line for line in out if line is not None) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/help_examples.do``."""
    path = path or STATA_DIR / "help_examples.do"
    path.write_text(render_do(), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(log: Path = LOG, path: Path = GOLDEN, out_dir: Path = OUT_DIR) -> Path:
    """Freeze the Stata results into ``tests/golden/help_examples_golden.json``."""
    parsed = parse_log(log.read_text(encoding="utf-8", errors="replace"))
    with gzip.open(SAMPLE, "wt", encoding="utf-8", newline="\n") as handle:
        pd.read_csv(out_dir / "he_sample.csv").to_csv(handle, index=False)
    cases: dict[str, dict[str, Any]] = {}
    for ex in EXAMPLES:
        entry: dict[str, Any] = dict(parsed[ex.name], command=ex.stata)
        if entry["rc"] == 0:
            tag = out_dir / f"he_{ex.name}"
            values = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(SCALARS, (float(v) for v in values), strict=True))
            for key, _ in MATRICES:
                entry[key] = pack(read_matrix(Path(f"{tag}_{key}.csv")))
            if ex.predict:
                frame = pd.read_csv(Path(f"{tag}_predict.csv"))
                entry["predict"] = pack(frame[["firm", "year", "ehat", "upper"]].to_numpy(float))
        cases[ex.name] = entry
    master = {"meta": {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38"}, "cases": cases}
    path.write_text(json.dumps(master), encoding="utf-8", newline="\n")
    return path


def frozen() -> dict[str, dict[str, Any]]:
    """The frozen Stata results."""
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


# ------------------------------------------------------------------------------- Python side
def frame(example: Example) -> pd.DataFrame:
    """The panel of the example, built the way the help file builds it."""
    if example.data == "unbalanced":
        return pd.read_csv(SAMPLE)
    df = pd.read_stata(DATA_DIR / "invest.dta")
    df["firm"], df["year"] = df["firm"].astype("int64"), df["year"].astype("int64")
    df = df[~df["firm"].isin(EXTREME_FIRMS)].reset_index(drop=True)
    if example.data == "peer":
        df["peer_q"] = df.groupby("year")["tobin_q"].transform("mean")
    return df


def fit(example: Example) -> Any:
    """Estimate one example with the package; returns the ``PointFit``."""
    from pyxtdpthresh._errors import PyxdpthreshWarning
    from pyxtdpthresh.models.xtdpthresh.fit import fit_point

    args = dict(example.args)
    y, q, x = args.pop("y"), args.pop("q"), args.pop("x")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return fit_point(frame(example), y, x, q=q, id="firm", time="year", **args)


# ------------------------------------------------------------------------------- comparison
@dataclass(frozen=True)
class Row:
    """One compared object: a number, or a whole matrix summarised by its largest deviation."""

    example: str
    group: str
    name: str
    python: float | None
    stata: float | None
    abs_dev: float
    rel_dev: float

    @property
    def ok(self) -> bool:
        return self.abs_dev <= ATOL or self.rel_dev <= RTOL


def _deviation(got: Any, want: Any) -> tuple[float, float]:
    """Largest absolute and relative deviation; ``inf`` when the shape or the missing differ."""
    got, want = np.atleast_1d(np.asarray(got, float)), np.atleast_1d(np.asarray(want, float))
    if got.shape != want.shape:
        if got.size == 0 and want.size == 0:
            return 0.0, 0.0
        return math.inf, math.inf
    miss = np.isnan(got) | np.isnan(want)
    if (np.isnan(got) != np.isnan(want)).any():
        return math.inf, math.inf
    keep = ~miss
    if not keep.any():
        return 0.0, 0.0
    diff = np.abs(got[keep] - want[keep])
    rel = diff / np.maximum(np.abs(want[keep]), np.finfo(float).tiny)
    return float(diff.max()), float(rel.max())


def _row(example: str, group: str, name: str, got: Any, want: Any) -> Row:
    abs_dev, rel_dev = _deviation(got, want)
    scalar = np.size(got) == 1 and np.size(want) == 1
    py = float(np.ravel(got)[0]) if scalar else None
    st = float(np.ravel(want)[0]) if scalar else None
    return Row(example, group, name, py, st, abs_dev, rel_dev)


def _matrices(fit_: Any) -> dict[str, np.ndarray]:
    """What the package holds under the name of each matrix of ``e()``."""
    var, boot = fit_.variance, fit_.bootstrap
    upper = fit_.upper
    empty = np.empty((0, 0))
    ci = boot.ci if boot is not None else None
    return {
        "b": fit_.search.fit.theta.reshape(1, -1),
        "V": fit_.cov,
        "V_cond": var.cond if var.joint else empty,
        "b_upper": np.asarray(upper.b).reshape(1, -1) if upper is not None else empty,
        "V_upper": np.asarray(upper.cov) if upper is not None else empty,
        "ci_segments": ci.segments if ci is not None and ci.segments.size else empty,
        "ci_grid": ci.table if ci is not None else empty,
    }


def _flat(array: np.ndarray) -> np.ndarray:
    return array.reshape(array.shape[0], -1) if array.size else array.reshape(0, 0)


def compare(example: Example, ref: dict[str, Any], fit_: Any | None = None) -> list[Row]:
    """Every object of the example, Python against the frozen Stata value."""
    fit_ = fit(example) if fit_ is None else fit_
    name, rows = example.name, []
    scalars = fit_.scalars
    b_ref, v_ref = unpack(ref["b"]).ravel(), unpack(ref["V"])
    b, v = fit_.search.fit.theta, fit_.cov
    for label, got, want in zip(fit_.names, b, b_ref, strict=True):
        rows.append(_row(name, "coefficient", label, got, want))
    for i, label in enumerate(fit_.names):
        rows.append(_row(name, "std. error", label, math.sqrt(v[i, i]), math.sqrt(v_ref[i, i])))
    for key in SCALARS:
        if key in BOOTSTRAP_SCALARS and not example.bootstrap and key != "rseed":
            continue
        rows.append(_row(name, "scalar", f"e({key})", scalars.get(key, math.nan),
                         ref["scalars"][key]))  # fmt: skip
    mats = _matrices(fit_)
    for key, stata in MATRICES:
        want = unpack(ref[key])
        if key in ("ci_grid", "ci_segments") and not example.bootstrap:
            continue
        rows.append(_row(name, "matrix", stata, _flat(mats[key]), _flat(want)))
    if example.predict:
        rows += _predict_rows(example, ref, fit_)
    return rows


def _predict_rows(example: Example, ref: dict[str, Any], fit_: Any) -> list[Row]:
    """``predict, residuals`` and ``predict, regime``, matched on (firm, year)."""
    data = frame(example)
    stata = pd.DataFrame(unpack(ref["predict"]), columns=["firm", "year", "ehat", "upper"])
    stata = stata.astype({"firm": "int64", "year": "int64"}).set_index(["firm", "year"])
    rows = []
    for kind, column in (("residuals", "ehat"), ("regime", "upper")):
        got = fit_.predict(kind, data)
        got.index = pd.MultiIndex.from_frame(data[["firm", "year"]])
        merged = stata[[column]].join(got.rename("py"), how="outer")
        rows.append(
            _row(example.name, "predict", f"predict, {kind}", merged["py"].to_numpy(float),
                 merged[column].to_numpy(float))
        )  # fmt: skip
    return rows


def worst(rows: list[Row]) -> dict[str, float]:
    """Largest absolute deviation of the rows, by group."""
    out: dict[str, float] = {}
    for row in rows:
        out[row.group] = max(out.get(row.group, 0.0), row.abs_dev)
    return out


# ------------------------------------------------------------------------------- the report
def _num(value: float | None) -> str:
    if value is None:
        return "-"
    if math.isnan(value):
        return "."
    return f"{value:.6g}"


def _dev(value: float) -> str:
    return "0" if value == 0 else f"{value:.1e}"


def canonical(command: str) -> list[str]:
    """Options of a command, sorted, to compare two spellings of the same call."""
    head, _, rest = command.partition(",")
    return sorted([*head.split()[:2], *re.findall(r"\w+\([^)]*\)|\w+", rest)])


def command_from_args(example: Example) -> str:
    """The Stata command that the arguments of the package correspond to."""
    return stata_command(example.args)


def report(rows_by_example: dict[str, list[Row]]) -> str:
    """Markdown of the side-by-side tables of every example."""
    lines = [
        "# The examples of the help file, in Stata and in Python",
        "",
        "Each command is the one printed in the help file of `xtdpthresh` (section *Examples*), "
        "run with the default options of Stata (`boot(299)`, `gridci(100)`, `grid(100)`). "
        "The Stata column is Stata 17 MP; the Python column is `pyxtdpthresh` on the same data. "
        f"A value agrees when the absolute deviation is at most {ATOL:g} or the relative "
        f"deviation is at most {RTOL:g}.",
        "",
        "| Example | Objects compared | Largest deviation | All agree |",
        "|---|---:|---:|:---:|",
    ]
    for ex in EXAMPLES:
        rows = rows_by_example[ex.name]
        peak = max(r.abs_dev for r in rows)
        lines.append(
            f"| {ex.title} | {len(rows)} | {_dev(peak)} | {'yes' if all(r.ok for r in rows) else 'NO'} |"
        )
    for ex in EXAMPLES:
        rows = rows_by_example[ex.name]
        lines += ["", f"## {ex.title}", "", f"`{ex.stata}`", ""]
        if ex.data == "unbalanced":
            lines += ["Data: the sample Stata drew with `set seed 20260418` (15% of the "
                      "observations dropped, then the firms with fewer than four left).", ""]  # fmt: skip
        for group, header in (("coefficient", "Coefficients"), ("std. error", "Standard errors")):
            part = [r for r in rows if r.group == group]
            lines += _table(header, part)
        for group, header in (("scalar", "Stored scalars"), ("matrix", "Stored matrices (largest "
                                                                      "deviation over all elements)"),
                              ("predict", "predict")):  # fmt: skip
            part = [r for r in rows if r.group == group]
            if part:
                lines += _table(header, part)
    return "\n".join(lines) + "\n"


def _table(header: str, rows: list[Row]) -> list[str]:
    out = [
        f"**{header}**",
        "",
        "| Object | Python | Stata | Abs. deviation |",
        "|---|---:|---:|---:|",
    ]
    out += [
        f"| `{r.name}` | {_num(r.python)} | {_num(r.stata)} | {_dev(r.abs_dev)} |" for r in rows
    ]
    return [*out, ""]


def run_all() -> dict[str, list[Row]]:
    """Run every example with the package and compare it with the frozen Stata results."""
    ref = frozen()
    fits: dict[str, Any] = {}
    out: dict[str, list[Row]] = {}
    for ex in EXAMPLES:
        key = (ex.data, str(ex.args))
        fits.setdefault(key, fit(ex))
        out[ex.name] = compare(ex, ref[ex.name], fits[key])
    return out


if __name__ == "__main__":
    import sys

    if "--freeze" in sys.argv:
        print(freeze())
    elif "--report" in sys.argv:
        REPORT.write_text(report(run_all()), encoding="utf-8", newline="\n")
        print(REPORT)
    else:
        print(write_do())
