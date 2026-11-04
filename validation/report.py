"""The validation report (K.3.2): how far the package is from Stata 17, case by case and object by object.

    python -m validation.report --record   # run tests/golden and record every deviation
    python -m validation.report            # build docs/validation_report.tex and .pdf

``--record`` runs the golden tests with ``PYX_RECORD_DEVIATIONS`` set (see
``tests/golden/conftest.py``); the deviations land in ``validation/deviations.jsonl``.  The
report adds the examples of the help file (:mod:`validation.help_examples`), which are compared
there object by object.  It is a LaTeX document compiled twice with XeLaTeX.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from validation.compare import ATOL, RTOL

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "validation" / "deviations.jsonl"
OUTPUT = ROOT / "docs" / "validation_report.pdf"
#: Test module -> title of the block of the report, in the order of the report.
BLOCKS: dict[str, str] = {
    "test_rng_golden": "Random numbers (Stata's Mersenne Twister)",
    "test_linalg_golden": "Matrix routines (invsym, cholinv, syminv)",
    "test_grid_golden": "Quantiles and threshold grids",
    "test_data_golden": "Data layer: xtset, lags, missing values",
    "test_operators_golden": "Time-series operators",
    "test_design_golden": "xthenreg: data and instruments",
    "test_linearity_golden": "xthenreg: sup-Wald statistic and linearity test",
    "test_covariance_golden": "xthenreg: covariance and confidence intervals",
    "test_gate_golden": "xthenreg: complete result",
    "test_xthenreg_public_h0": "xthenreg: bandwidth multiplier h_0() through the public function",
    "test_sample_golden": "xtdpthresh: estimation sample",
    "test_estimation_golden": "xtdpthresh: instruments and fixed-threshold GMM",
    "test_search_golden": "xtdpthresh: threshold search and final estimate",
    "test_point_golden": "xtdpthresh: point estimates on the full panel",
    "test_transform_golden": "xtdpthresh: deviations, time effects, unbalanced panels, history",
    "test_variance_golden": "xtdpthresh: variances and diagnostics",
    "test_predict_golden": "xtdpthresh: predict",
    "test_bootstrap_golden": "xtdpthresh: bootstraps, confidence set, tests",
    "test_help_unbalanced_golden": "xtdpthresh: unbalanced panel of the help file (no bootstrap)",
    "test_edge_golden": "xtdpthresh: hostile inputs",
    "test_simulated_golden": "Simulated panels of the Seo-Shin design",
}


@dataclass(frozen=True)
class Record:
    """One comparison of the package with a frozen Stata value (a number or a matrix)."""

    module: str
    case: str
    object: str
    n: int
    abs: float
    margin: float
    rtol: float | None = None  # a looser relative tolerance declared by the test, if any


# ------------------------------------------------------------------------------- data
def case_name(test: str) -> str:
    """The case a test ran on: the parameter of the test, or its name."""
    found = re.search(r"\[(.*)\]$", test)
    if found:
        return found.group(1)
    return re.sub(r"^test_", "", test)


def load(path: Path = RECORDS) -> list[Record]:
    """Recorded deviations of the golden tests, without the comparisons that are not with Stata."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        if raw["module"] in BLOCKS:
            out.append(
                Record(
                    raw["module"],
                    case_name(raw["test"]),
                    raw["object"],
                    raw["n"],
                    raw["abs"],
                    raw["margin"],
                    raw["rtol"] if raw.get("rtol", 0) > RTOL else None,
                )  # fmt: skip
            )
    return out


def help_records() -> list[Record]:
    """The examples of the help file, object by object, as records."""
    from validation import help_examples as he

    out = []
    for name, rows in he.run_all().items():
        for r in rows:
            margin = min(r.abs_dev / ATOL, r.rel_dev / RTOL)
            out.append(Record("help_examples", name, f"{r.group}: {r.name}", 1, r.abs_dev, margin))
    return out


def summarise(records: list[Record]) -> dict[str, dict[str, Any]]:
    """Per block: cases, objects, values, largest absolute deviation and largest margin."""
    out: dict[str, dict[str, Any]] = {}
    for module in dict.fromkeys(r.module for r in records):
        part = [r for r in records if r.module == module and r.rtol is None]
        if not part:
            continue
        out[module] = {
            "cases": len({r.case for r in part}),
            "objects": len({r.object for r in part}),
            "comparisons": len(part),
            "values": sum(r.n for r in part),
            "abs": max(r.abs for r in part),
            "margin": max(r.margin for r in part),
        }
    return out


def by_object(records: list[Record]) -> list[tuple[str, int, int, float]]:
    """Per object name: cases, values, largest absolute deviation (sorted by name)."""
    groups: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        if r.rtol is None:
            groups[r.object].append(r)
    return sorted(
        (name, len({r.case for r in part}), sum(r.n for r in part), max(r.abs for r in part))
        for name, part in groups.items()
    )


def by_case(records: list[Record]) -> list[tuple[str, int, int, str, float]]:
    """Per case: objects, values, the object that deviates most, and its deviation."""
    groups: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        if r.rtol is None:
            groups[r.case].append(r)
    out = []
    for case, part in groups.items():
        worst = max(part, key=lambda r: r.abs)
        out.append((case, len({r.object for r in part}), sum(r.n for r in part), worst.object,
                    worst.abs))  # fmt: skip
    return sorted(out)


# ------------------------------------------------------------------------------- LaTeX
_TEX = {"\\": r"\textbackslash{}", "_": r"\_", "&": r"\&", "%": r"\%", "#": r"\#", "$": r"\$",
        "{": r"\{", "}": r"\}", "^": r"\^{}", "~": r"\~{}"}  # fmt: skip


def tex(text: str) -> str:
    """Escape ``text`` for LaTeX."""
    return "".join(_TEX.get(c, c) for c in text)


def code(text: str) -> str:
    """``text`` in typewriter, breakable after the usual separators."""
    out = tex(text)
    for sep in (r"\_", ":", ","):
        out = out.replace(sep, sep + r"\allowbreak{}")
    return rf"\texttt{{{out}}}"


def dev(value: float) -> str:
    """A deviation, in scientific notation."""
    if value == 0:
        return "0"
    mantissa, exponent = f"{value:.1e}".split("e")
    return rf"${mantissa}\times10^{{{int(exponent)}}}$"


def _table(spec: str, head: str, rows: list[str]) -> str:
    return "\n".join(
        [rf"\begin{{longtable}}{{{spec}}}", r"\toprule", head + r" \\", r"\midrule", r"\endhead",
         *rows, r"\bottomrule", r"\end{longtable}"]
    )  # fmt: skip


PREAMBLE = r"""\documentclass[10.5pt,a4paper]{article}
\usepackage[margin=2.3cm]{geometry}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}
\setmonofont{Latin Modern Mono}[Scale=0.92]
\usepackage{amsmath}
\usepackage{booktabs,longtable,array}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\footnotesize}
\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue]{hyperref}
\usepackage{fancyhdr}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small pyxtdpthresh validation report}
\fancyfoot[C]{\small\thepage}
\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.12}
\setlength{\tabcolsep}{4pt}
\newcommand{\code}[1]{\texttt{#1}}
"""


def render(blocks: dict[str, list[Record]], help_rows: list[Record], meta: dict[str, str]) -> str:
    """The LaTeX source of the report."""
    every = [r for part in blocks.values() for r in part if r.rtol is None] + help_rows
    total = {"cases": 0, "objects": 0, "comparisons": 0, "values": 0}
    worst_abs = max(r.abs for r in every)
    worst_margin = max(r.margin for r in every)
    summary = {**summarise([r for part in blocks.values() for r in part])}
    summary["help_examples"] = summarise(help_rows)["help_examples"]
    titles = {
        **BLOCKS,
        "help_examples": "xtdpthresh: the examples of the help file (default options)",
    }
    rows = []
    for module, s in summary.items():
        for key in total:
            total[key] += s[key]
        rows.append(
            f"{tex(titles[module])} & {s['cases']} & {s['objects']} & {s['values']:,} & "
            f"{dev(s['abs'])} & {s['margin']:.2g} \\\\".replace(",", r"\,")
        )
    rows.append(r"\midrule")
    rows.append(
        f"\\textbf{{All blocks}} & \\textbf{{{total['cases']}}} & & \\textbf{{{total['values']:,}}} & "
        f"\\textbf{{{dev(worst_abs)}}} & \\textbf{{{worst_margin:.2g}}} \\\\".replace(",", r"\,")
    )
    parts = [
        PREAMBLE,
        rf"\title{{\textbf{{pyxtdpthresh {tex(meta['version'])}: validation against Stata 17}}\\[2pt]"
        r"\large Largest deviation by block, by case and by object}",
        r"\author{}",
        rf"\date{{{tex(meta['date'])}}}",
        r"\begin{document}\maketitle",
        r"\section{Rule and method}",
        rf"""Every number the package reports must equal the one computed by Stata 17 to four
decimals: the absolute difference is at most ${ATOL:g}$ \emph{{or}} the relative difference is at
most ${RTOL:g}$ (the relative branch keeps the rule meaningful for large values such as the
objective function). The \emph{{margin}} of a value is $\min(|\Delta|/{ATOL:g},\;
(|\Delta|/|x|)/{RTOL:g})$; it is at most $1$ when the value agrees, and the tables report the
largest margin of each block.

The references are produced by the real commands ({tex(meta["commands"])}) run in batch with {tex(meta["stata"])};
each object is exported at 15 significant digits and frozen in \code{{tests/golden/}}. The test
suite compares the package with the frozen values, and the deviations in this report are recorded
by those very comparisons ({tex(meta["count"])} comparisons of matrices or numbers in the golden tests, plus the
objects of the help-file examples). The random numbers of Stata are reproduced exactly, so the
seeded bootstraps draw the weights of the command and their $p$-values and confidence sets are
compared directly.""",
        r"\section{Summary by block}",
        _table(
            r"@{}p{7.4cm}rrrrr@{}",
            r"Block & Cases & Objects & Values & Largest $|\Delta|$ & Margin",
            rows,
        ),
        r"""\noindent \emph{Cases} are the distinct designs or samples of a block; \emph{Objects} are the
distinct names compared (for example \code{e(b)}); \emph{Values} counts every number compared, a
matrix counting for all its elements. The absolute deviation is large only where the values
are (the matrix routines are tested on very large and very small matrices); the margin says
whether the rule holds. Integer results (counts of equations, instruments, return
codes of the refusals, sets of rows) are compared for exact equality and are not listed in the
deviations: the tests fail on the first difference.""",
        r"\section{The examples of the help file}",
        r"""The eight commands of the help file of \code{xtdpthresh} were run as printed, with the default options of Stata
(\code{boot(299)}, \code{gridci(100)}, \code{grid(100)}), on Hansen's investment panel without the five extreme firms.
The tables of the values, Python against Stata, are in \code{docs/help\_examples.md}; the largest deviation of each
kind of object is below.""",
        _help_table(help_rows),
    ]
    parts.append(r"\section{Largest deviation by object}")
    parts.append(
        "The objects are named as the tests name them (\\code{e(b)}, \\code{e(V)}, \\code{e(ci\\_grid)}\\ldots). "
        "A block appears here when it compares several named objects over several cases; "
        "the other blocks compare one kind of value, or one object per case, and are described "
        "by the table of their cases in the next section."
    )
    for module, part in blocks.items():
        objects = by_object(part)
        if len(objects) < 2 or len(objects) == len({r.case for r in part}):
            continue
        parts.append(rf"\subsection*{{{tex(BLOCKS[module])}}}")
        parts.append(
            _table(
                r"@{}p{8.2cm}rrr@{}",
                r"Object & Cases & Values & Largest $|\Delta|$",
                [
                    f"{code(o)} & {c} & {v:,} & {dev(a)} \\\\".replace(",", r"\,")
                    for o, c, v, a in objects
                ],
            )
        )
    parts.append(r"\section{Largest deviation by case}")
    for module, part in blocks.items():
        if not part:
            continue
        parts.append(rf"\subsection*{{{tex(BLOCKS[module])}}}")
        parts.append(
            _table(
                r"@{}p{3.6cm}rrp{4.9cm}r@{}",
                r"Case & Objects & Values & Worst object & $|\Delta|$",
                [
                    f"{code(c)} & {o} & {v:,} & {code(w)} & {dev(a)} \\\\".replace(",", r"\,")
                    for c, o, v, w, a in by_case(part)
                ],
            )
        )
    relaxed = [r for part in blocks.values() for r in part if r.rtol is not None]
    parts.append(_relaxed_section(relaxed))
    parts.append(
        rf"""\section{{What this report does not cover}}
\begin{{itemize}}
\item The statistical behaviour of the package's own seeds (size and power of the tests, coverage
of the confidence set over many panels) is measured by Monte Carlo and compared with the papers,
not with Stata.
\item The tables written by the package (LaTeX, HTML, Word, Excel) repeat the validated numbers;
the tests check the printed digits, not the typography. They are not in the deviations above.
\item Timings are measured on the same machine one run after the other and are not a validation.
\item The messages that Stata prints and the package does not (the warning of an unbalanced
\code{{boottype(unit)}} and the hint on near-common variables in a rank failure) are not compared;
they do not change any number.
\end{{itemize}}
\section{{Environment}}
\begin{{tabular}}{{@{{}}ll@{{}}}}
Reference & {tex(meta["stata"])}; {tex(meta["commands"])} \\
Package & pyxtdpthresh {tex(meta["version"])} \\
Python & {tex(meta["python"])}; NumPy {tex(meta["numpy"])}; Numba {tex(meta["numba"])} \\
Platform & {tex(meta["platform"])} \\
Report built & {tex(meta["date"])} \\
\end{{tabular}}
\end{{document}}"""
    )
    return "\n\n".join(parts)


def _relaxed_section(relaxed: list[Record]) -> str:
    """The comparisons whose test declares a looser tolerance than the rule of the project."""
    head = r"\section{Comparisons under a looser tolerance}"
    if not relaxed:
        return head + "\nNo comparison uses a tolerance looser than the rule of Section 1."
    rows = [
        f"{code(r.case)} & {code(r.object)} & {dev(r.rtol or 0)} & {dev(r.abs)} \\\\"
        for r in relaxed
    ]
    text = (
        "The rule of Section 1 holds for every other value of this report. "
        f"{len(relaxed)} comparison(s) are made under a looser relative tolerance, declared in the "
        "test and not hidden in the tables above: the input is so ill-conditioned that the error "
        "of any implementation is of the order of the condition number times the machine "
        "precision (a matrix of condition number $10^{13}$ gives about $10^{-3}$), so two correct "
        "inverses legitimately differ in the fourth digit."
    )
    spec, columns = r"@{}p{3cm}p{3cm}rr@{}", r"Case & Object & Relative tolerance & $|\Delta|$"
    return "\n".join([head, text, _table(spec, columns, rows)])


def _help_table(help_rows: list[Record]) -> str:
    """Per example and kind of object: objects compared and largest deviation."""
    from validation import help_examples as he

    rows = []
    for ex in he.EXAMPLES:
        part = [r for r in help_rows if r.case == ex.name]
        kinds: dict[str, list[Record]] = defaultdict(list)
        for r in part:
            kinds[r.object.split(":", 1)[0]].append(r)
        for i, (kind, items) in enumerate(kinds.items()):
            label = tex(ex.title) if i == 0 else ""
            rows.append(
                f"{label} & {tex(kind)} & {len(items)} & {dev(max(r.abs for r in items))} \\\\"
            )
        rows.append(r"\addlinespace")
    return _table(
        r"@{}p{7.2cm}p{2.8cm}rr@{}", r"Example & Objects & Compared & Largest $|\Delta|$", rows
    )


# ------------------------------------------------------------------------------- build
def metadata(n_records: int) -> dict[str, str]:
    """Versions and dates printed in the report."""
    import numba
    import numpy

    sys.path.insert(0, str(ROOT / "src"))
    from pyxtdpthresh._version import __version__

    master = json.loads((ROOT / "tests" / "golden" / "help_examples_golden.json").read_text())
    stata = master["meta"]["stata"]
    return {
        "version": __version__,
        "date": f"{dt.date.today():%d %B %Y}",
        "stata": stata,
        "commands": f"xthenreg (Seo, Kim and Kim 2019) and xtdpthresh {master['meta']['xtdpthresh']}",
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "numba": numba.__version__,
        "platform": f"{platform.system()} {platform.release()}",
        "count": f"{n_records:,}".replace(",", "\\,"),
    }


def record() -> Path:
    """Run the golden tests and record their deviations."""
    if RECORDS.exists():
        RECORDS.unlink()
    env = {**os.environ, "PYX_RECORD_DEVIATIONS": str(RECORDS)}
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/golden", "-q", "-p", "no:cacheprovider"],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )  # fmt: skip
    if done.returncode != 0:
        raise SystemExit(f"the golden tests failed:\n{done.stdout[-3000:]}")
    return RECORDS


def build(output: Path = OUTPUT) -> Path:
    """Write ``validation_report.tex`` next to ``output``, compile it, and return the PDF path."""
    if shutil.which("xelatex") is None:
        raise SystemExit("xelatex is needed to build the report and was not found on the PATH")
    records = load()
    blocks = {module: [r for r in records if r.module == module] for module in BLOCKS}
    source = render(blocks, help_records(), metadata(len(records)))
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "validation_report.tex").write_text(source, encoding="utf-8")
        for _ in range(2):
            done = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "validation_report.tex"],
                cwd=work, capture_output=True, text=True, encoding="utf-8", errors="replace",
            )  # fmt: skip
            if done.returncode != 0:
                raise SystemExit(f"xelatex failed:\n{done.stdout[-3000:]}")
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work / "validation_report.pdf", output)
        shutil.copyfile(work / "validation_report.tex", output.with_suffix(".tex"))
    return output


if __name__ == "__main__":
    print(record() if "--record" in sys.argv else build())
