"""Inventory of the Stata functions the package ports, and check of every provenance comment.

Every ported function carries ``# Stata: function (file.ado:line)`` (see CONTRIBUTING.md).
This tool

* reads the Mata functions and ado programs defined in the three Stata files and stores their line
  ranges in ``validation/stata_functions.json`` (so that the check also runs where the ``.ado``
  files are not available);
* scans ``src/`` for the comments, and checks that each reference names an existing file, a line
  inside it and, when a function is named, a line inside that function;
* writes ``docs/ported_functions.md``: Stata function, where it is ported, and the functions of the
  Stata files that no comment mentions.

    python tools/ported_functions.py manifest    # rebuild the manifest from the .ado files
    python tools/ported_functions.py check       # list the problems (exit 1 if any)
    python tools/ported_functions.py inventory   # write docs/ported_functions.md
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADO_DIR = ROOT.parent
ADO_FILES = ("xtdpthresh.ado", "xtdpthresh_p.ado", "xthenreg.ado")
MANIFEST = ROOT / "validation" / "stata_functions.json"
INVENTORY = ROOT / "docs" / "ported_functions.md"

_MATA_DEF = re.compile(
    r"^(?:real|void|struct|string|transmorphic|numeric|complex|pointer|class|matrix|colvector"
    r"|rowvector|scalar|vector)\b[^(]*?\b(?P<name>[A-Za-z_]\w*)\("
)
_FUNCTION_DEF = re.compile(r"^function\s+(?P<name>[A-Za-z_]\w*)\(")
_PROGRAM_DEF = re.compile(r"^program\s+(?:define\s+)?(?P<name>[A-Za-z_]\w*)")
_REFERENCE = re.compile(r"\((?P<file>[\w]+\.ado):(?P<first>\d+)(?:-(?P<last>\d+))?\)")
_BARE_REFERENCE = re.compile(r"(?<![\w(])(?P<file>[\w]+\.ado):(?P<first>\d+)(?:-(?P<last>\d+))?")
_SHORT_REFERENCE = re.compile(r"(?<![\w:.])\((?P<first>\d+)(?:-(?P<last>\d+))?\)")
_IDENTIFIER = re.compile(r"[A-Za-z_]\w*")


@dataclass(frozen=True)
class Reference:
    """One ``file:line`` reference found in a comment of the package."""

    source: str
    line: int
    ado: str
    first: int
    last: int
    names: tuple[str, ...]


def parse_ado(path: Path) -> dict[str, object]:
    """Return the number of lines, the digest and the line range of every function of ``path``."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    starts: list[tuple[int, str]] = []
    for number, line in enumerate(lines, start=1):
        function = _FUNCTION_DEF.match(line) or _PROGRAM_DEF.match(line)
        if function:
            starts.append((number, function["name"]))
            continue
        mata = _MATA_DEF.match(line)
        if mata:
            starts.append((number, mata["name"]))
    ranges = {
        name: [begin, (starts[i + 1][0] - 1) if i + 1 < len(starts) else len(lines)]
        for i, (begin, name) in enumerate(starts)
    }
    return {
        "lines": len(lines),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "functions": ranges,
    }


def build_manifest() -> dict[str, object]:
    """Return the manifest of the three Stata files."""
    return {name: parse_ado(ADO_DIR / name) for name in ADO_FILES}


def load_manifest() -> dict[str, dict[str, object]]:
    """Return the committed manifest."""
    loaded: dict[str, dict[str, object]] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return loaded


def _comment_references(text: str) -> list[tuple[str, int, int, tuple[str, ...]]]:
    """Return ``(file, first, last, names)`` for each reference of one comment, in order.

    A reference is ``(file.ado:100)``, ``file.ado:100-200`` or, after a file has been given in the
    same comment, the short form ``name (300)`` that reuses it.
    """
    spans = [
        (m.start(), m.end(), m["file"], m["first"], m["last"], False)
        for m in (*_REFERENCE.finditer(text), *_BARE_REFERENCE.finditer(text))
    ]
    spans += [
        (m.start(), m.end(), "", m["first"], m["last"], True)
        for m in _SHORT_REFERENCE.finditer(text)
    ]
    out: list[tuple[str, int, int, tuple[str, ...]]] = []
    cursor, current = 0, ""
    for start, end, file, first, last, short in sorted(spans):
        if start < cursor:
            continue  # inside a reference already read
        if short and not current:
            continue
        current = current if short else file
        names = tuple(_IDENTIFIER.findall(text[cursor:start]))
        out.append((current, int(first), int(last or first), names))
        cursor = end
    return out


def scan_sources(src: Path | None = None) -> list[Reference]:
    """Return every reference found in the ``# Stata:`` comments of the package."""
    found: list[Reference] = []
    for path in sorted((src or ROOT / "src").rglob("*.py")):
        try:
            name = str(path.relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            name = path.name
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            marker = line.find("# Stata:")
            if marker >= 0:
                text = line[marker + len("# Stata:") :]
                found += [
                    Reference(name, number, file, first, last, names)
                    for file, first, last, names in _comment_references(text)
                ]
    return found


def check(manifest: dict[str, dict[str, object]], references: list[Reference]) -> list[str]:
    """Return the problems of the references (an empty list when they are all valid)."""
    problems = []
    for ref in references:
        where = f"{ref.source}:{ref.line}"
        entry = manifest.get(ref.ado)
        if entry is None:
            problems.append(f"{where}: unknown Stata file {ref.ado}")
            continue
        total = int(entry["lines"])  # type: ignore[call-overload]
        if not 1 <= ref.first <= ref.last <= total:
            problems.append(f"{where}: lines {ref.first}-{ref.last} outside {ref.ado} ({total})")
            continue
        functions: dict[str, list[int]] = entry["functions"]  # type: ignore[assignment]
        named = [name for name in ref.names if name in functions]
        if named and not any(functions[n][0] <= ref.first <= functions[n][1] for n in named):
            spans = ", ".join(f"{n} {functions[n][0]}-{functions[n][1]}" for n in named)
            problems.append(f"{where}: line {ref.first} is not inside {spans}")
    return problems


def inventory(manifest: dict[str, dict[str, object]], references: list[Reference]) -> str:
    """Return the markdown inventory of the ported and of the unreferenced functions."""
    ported: dict[tuple[str, str], set[str]] = {}
    for ref in references:
        functions: dict[str, list[int]] = manifest[ref.ado]["functions"]  # type: ignore[assignment]
        names = [n for n in ref.names if n in functions] or [
            n for n, (a, b) in functions.items() if a <= ref.first <= b
        ]
        for name in names:
            ported.setdefault((ref.ado, name), set()).add(
                ref.source.removeprefix("src/pyxtdpthresh/")
            )
    out = [
        "# Stata functions ported by the package",
        "",
        "Generated by `tools/ported_functions.py inventory` from the `# Stata:` comments of `src/`",
        "and the function ranges of `validation/stata_functions.json`. A function is *ported* when",
        "at least one comment of the package points inside it.",
        "",
    ]
    for ado in ADO_FILES:
        functions: dict[str, list[int]] = manifest[ado]["functions"]  # type: ignore[assignment]
        done = sorted(n for (a, n) in ported if a == ado)
        todo = sorted(set(functions) - set(done))
        out += [
            f"## `{ado}` — {len(done)} of {len(functions)} functions referenced",
            "",
            "| Stata function | Lines | Ported in |",
            "|---|---|---|",
        ]
        out += [
            f"| `{n}` | {functions[n][0]}-{functions[n][1]} | "
            + ", ".join(f"`{m}`" for m in sorted(ported[(ado, n)]))
            + " |"
            for n in done
        ]
        out += [
            "",
            f"Not referenced by any comment ({len(todo)}): "
            + (", ".join(f"`{n}`" for n in todo) or "none"),
            "",
        ]
    return "\n".join(out)


def main(command: str) -> int:
    """Run one command of the tool and return the exit code."""
    if command == "manifest":
        MANIFEST.write_text(json.dumps(build_manifest(), indent=1, sort_keys=True) + "\n", "utf-8")
        print("written", MANIFEST)
        return 0
    manifest, references = load_manifest(), scan_sources()
    if command == "inventory":
        INVENTORY.write_text(inventory(manifest, references) + "\n", encoding="utf-8")
        print("written", INVENTORY)
        return 0
    problems = check(manifest, references)
    print(f"{len(references)} references, {len(problems)} problem(s)")
    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "check"))
