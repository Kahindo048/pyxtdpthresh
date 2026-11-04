r"""Build the LaTeX source and the PDF of the user guide from ``docs/user_guide.md``.

    python tools/build_guide_pdf.py [output.pdf]

The Markdown file is the source of the guide, ``docs/methodological_note.tex`` the source of its
Appendix A (the methodological note) and ``docs/validation_appendix.tex`` (written by
``python -m validation.report``) the source of its Appendix B (the validation against Stata 17).
The script writes ``docs/user_guide.tex`` (a standalone XeLaTeX document in the typeface of the
author's articles: Latin Modern text, Computer Modern maths) and compiles it into
``docs/user_guide.pdf``. The note and the validation appendix are inserted before
``\end{document}``, and the line ``\input{ported_functions.tex}`` of the note is replaced by the
tables of ``docs/ported_functions.md`` (the Stata functions and where they live) converted by
pandoc.
Before pandoc runs on the guide, the script

* drops the hand-written list of contents (LaTeX builds the real one, with page numbers);
* turns a Greek letter carrying a hat (the letter and a combining accent) into one private
  character that the preamble draws as a maths hat;
* gives every pipe table column a width proportional to its text, so that the wide notes column
  of the option tables wraps instead of squeezing every column to the same width.

The code blocks keep their text and wrap at the margin. Needs ``pandoc`` and ``xelatex`` on the
PATH. The compilation runs twice, for the table of contents, and fails if a character has no glyph.
"""

from __future__ import annotations

import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "user_guide.md"
NOTE = ROOT / "docs" / "methodological_note.tex"
VALIDATION = ROOT / "docs" / "validation_appendix.tex"
PORTED = ROOT / "docs" / "ported_functions.md"
DEFAULT_OUTPUT = ROOT / "docs" / "user_guide.pdf"
#: The line of the note that is replaced by the table generated from ``PORTED``.
INCLUDE_PORTED = r"\input{ported_functions.tex}"

MAIN_FONT, MONO_FONT = "Latin Modern Roman", "Latin Modern Mono"
#: A hatted gamma (letter and combining circumflex) and the private character standing for it.
HATTED_GAMMA, PRIVATE_CHARACTER = "γ̂", ""

HEADER = r"""
\usepackage{newunicodechar}
\newunicodechar{PRIVATE}{\ensuremath{\hat{\gamma}}}
\newunicodechar{γ}{\ensuremath{\gamma}}
\newunicodechar{δ}{\ensuremath{\delta}}
\newunicodechar{β}{\ensuremath{\beta}}
\newunicodechar{η}{\ensuremath{\eta}}
\newunicodechar{ε}{\ensuremath{\varepsilon}}
\newunicodechar{₀}{\ensuremath{{}_0}}
\newunicodechar{₁}{\ensuremath{{}_1}}
\newunicodechar{₂}{\ensuremath{{}_2}}
\usepackage{fvextra}
\fvset{breaklines=true, breakanywhere=true, fontsize=\footnotesize}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
\RecustomVerbatimEnvironment{verbatim}{Verbatim}{breaklines,breakanywhere}
\usepackage{booktabs}
\usepackage{longtable}
\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.15}
\setlength{\tabcolsep}{4pt}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{quote}{\small}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small pyxtdpthresh user guide}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
""".replace("PRIVATE", PRIVATE_CHARACTER)


def strip_contents(text: str) -> str:
    """Remove the hand-written ``**Contents**`` list (up to the first blank line after it)."""
    return re.sub(r"\*\*Contents\*\*\n\n(?:\d+\. .*\n)+\n", "", text)


def hatted_gamma(text: str) -> str:
    """Replace the hatted gamma by the private character the preamble draws."""
    return text.replace(HATTED_GAMMA, PRIVATE_CHARACTER)


def _cells(line: str) -> list[str]:
    """Cells of a pipe-table row, honouring the escaped bar ``\\|``."""
    inner = line.strip().strip("|")
    return [c.strip() for c in re.split(r"(?<!\\)\|", inner)]


def weight_tables(text: str, total: int = 100) -> str:
    """Rewrite the separator row of each pipe table with dashes proportional to column text."""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        is_head = (
            lines[i].lstrip().startswith("|")
            and i + 1 < len(lines)
            and re.fullmatch(r"\s*\|(\s*:?-+:?\s*\|)+\s*", lines[i + 1])
        )
        if not is_head:
            out.append(lines[i])
            i += 1
            continue
        end = i + 2
        while end < len(lines) and lines[end].lstrip().startswith("|"):
            end += 1
        rows = [_cells(lines[i]), *(_cells(r) for r in lines[i + 2 : end])]
        aligns = [c.strip() for c in _cells(lines[i + 1])]
        k = len(aligns)
        # width of a column: its longest cell, with a floor and a ceiling so that no column
        # vanishes and the notes column does not take everything
        longest = [max((len(r[j]) for r in rows if j < len(r)), default=1) for j in range(k)]
        weights = [min(max(w, 8), 70) for w in longest]
        dashes = [max(3, round(total * w / sum(weights))) for w in weights]
        sep = "|" + "|".join(_align(a, d) for a, d in zip(aligns, dashes, strict=True)) + "|"
        out += [lines[i], sep, *lines[i + 2 : end]]
        i = end
    return "\n".join(out)


def _align(spec: str, dashes: int) -> str:
    left, right = spec.startswith(":"), spec.endswith(":")
    return (":" if left else "") + "-" * dashes + (":" if right else "")


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace")  # fmt: skip


def ported_functions_tex(work: Path) -> str:
    """LaTeX of the inventory of the ported Stata functions (``docs/ported_functions.md``)."""
    text = PORTED.read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)  # the title: the note has its own heading
    (work / "ported.md").write_text(weight_tables(text), encoding="utf-8")
    done = _run(["pandoc", "ported.md", "-f", "markdown+pipe_tables", "-t", "latex",
                 "--shift-heading-level-by=1"], work)  # fmt: skip
    if done.returncode != 0:
        raise SystemExit(f"pandoc failed on the inventory:\n{done.stderr[-2000:]}")
    return done.stdout


def insert_note(tex: str, work: Path) -> str:
    """Put the methodological note, then the validation appendix, before ``\\end{document}``."""
    note = NOTE.read_text(encoding="utf-8")
    lines = note.split("\n")
    if lines.count(INCLUDE_PORTED) != 1 or tex.count(r"\end{document}") != 1:
        raise SystemExit("the note or the guide does not have the expected structure")
    lines[lines.index(INCLUDE_PORTED)] = ported_functions_tex(work)
    note = "\n".join(lines)
    if not VALIDATION.exists():
        raise SystemExit(f"{VALIDATION} is missing: run python -m validation.report first")
    note += "\n" + VALIDATION.read_text(encoding="utf-8")
    return tex.replace(r"\end{document}", note + "\n\\end{document}")


def build(output: Path = DEFAULT_OUTPUT) -> Path:
    """Write ``user_guide.tex`` next to ``output``, compile it, and return the PDF path."""
    for tool in ("pandoc", "xelatex"):
        if shutil.which(tool) is None:
            raise SystemExit(f"{tool} is needed to build the PDF and was not found on the PATH")
    sys.path.insert(0, str(ROOT / "src"))
    from pyxtdpthresh._version import __version__

    text = weight_tables(hatted_gamma(strip_contents(SOURCE.read_text(encoding="utf-8"))))
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        (work / "guide.md").write_text(text, encoding="utf-8")
        (work / "header.tex").write_text(HEADER, encoding="utf-8")
        command = [
            "pandoc", "guide.md", "-s", "-o", "user_guide.tex",
            "--from", "markdown+pipe_tables+backtick_code_blocks-smart",
            "--pdf-engine", "xelatex",
            "--shift-heading-level-by=-1",  # the title heading becomes the document title
            "--toc", "--toc-depth=2",
            "--include-in-header", "header.tex",
            "-V", f"mainfont={MAIN_FONT}", "-V", f"monofont={MONO_FONT}",
            "-V", "monofontoptions=Scale=0.92",
            "-V", "fontsize=10.5pt", "-V", "geometry:margin=2.3cm", "-V", "papersize=a4",
            "-V", "colorlinks=true", "-V", "linkcolor=black", "-V", "urlcolor=blue",
            "-V", f"subtitle=Version {__version__} (alpha)",
            "-V", f"date={dt.date.today():%d %B %Y}",
            "--syntax-highlighting=pygments",
        ]  # fmt: skip
        done = _run(command, work)
        if done.returncode != 0:
            raise SystemExit(f"pandoc failed:\n{done.stderr[-3000:]}")
        guide_tex = work / "user_guide.tex"
        guide_tex.write_text(
            insert_note(guide_tex.read_text(encoding="utf-8"), work), encoding="utf-8"
        )
        for _ in range(2):  # the second pass resolves the table of contents
            done = _run(
                ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "user_guide.tex"], work
            )
            if done.returncode != 0:
                raise SystemExit(f"xelatex failed:\n{done.stdout[-3000:]}")
        log = (work / "user_guide.log").read_text(encoding="utf-8", errors="replace")
        missing = sorted(set(re.findall(r"Missing character: There is no (.) ", log)))
        if missing:
            raise SystemExit(f"characters without a glyph: {missing}")
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(work / "user_guide.pdf", output)
        shutil.copyfile(work / "user_guide.tex", output.with_suffix(".tex"))
    return output


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    print(build(target))
