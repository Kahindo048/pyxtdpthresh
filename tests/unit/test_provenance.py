"""Provenance of the ported code: every ``# Stata:`` comment points to a real place (A.5.8)."""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import ported_functions as tool  # noqa: E402

#: Floors that only go up: a drop means provenance comments were removed.
MIN_REFERENCES = 125
MIN_FUNCTIONS = 50


@pytest.fixture(scope="module")
def manifest():
    return tool.load_manifest()


@pytest.fixture(scope="module")
def references():
    return tool.scan_sources()


def test_every_reference_names_an_existing_file_line_and_function(manifest, references):
    assert tool.check(manifest, references) == []


def test_the_references_are_numerous_and_cover_many_stata_functions(manifest, references):
    assert len(references) >= MIN_REFERENCES
    inventory = tool.inventory(manifest, references)
    covered = {
        line.split("`")[1]
        for line in inventory.splitlines()
        if line.startswith("| `") and line.count("|") >= 4
    }
    assert len(covered) >= MIN_FUNCTIONS


def test_the_manifest_matches_the_stata_files_when_they_are_available(manifest):
    missing = [name for name in tool.ADO_FILES if not (tool.ADO_DIR / name).exists()]
    if missing:
        pytest.skip(f"Stata files not next to the package: {missing}")
    assert tool.build_manifest() == manifest, "run: python tools/ported_functions.py manifest"


def test_the_checker_catches_a_bad_reference(manifest):
    bad_line = tool.Reference("x.py", 1, "xtdpthresh.ado", 10**7, 10**7, ())
    wrong_function = tool.Reference("x.py", 2, "xtdpthresh.ado", 5, 5, ("xdpt2_objtol",))
    unknown_file = tool.Reference("x.py", 3, "other.ado", 5, 5, ())
    problems = tool.check(manifest, [bad_line, wrong_function, unknown_file])
    assert len(problems) == 3
    assert "outside" in problems[0] and "not inside" in problems[1] and "unknown" in problems[2]


def test_the_reference_scanner_reads_the_comment_forms_of_the_package(tmp_path):
    source = tmp_path / "m.py"
    source.write_text(
        "# Stata: xdpt2_objtol (xtdpthresh.ado:2497)\n"
        "# Stata: xtdpthresh.ado:58-460 (syntax line)\n"
        "# Stata: a_function (xthenreg.ado:1175), other (xtdpthresh.ado:300)\n"
        "# Stata: a remark without a reference\n",
        encoding="utf-8",
    )
    found = tool.scan_sources(tmp_path)
    assert [(r.ado, r.first, r.last) for r in found] == [
        ("xtdpthresh.ado", 2497, 2497),
        ("xtdpthresh.ado", 58, 460),
        ("xthenreg.ado", 1175, 1175),
        ("xtdpthresh.ado", 300, 300),
    ]
    assert "xdpt2_objtol" in found[0].names and "a_function" in found[2].names


def test_a_quirk_marker_always_gives_its_reason():
    markers = []
    for path in (ROOT / "src").rglob("*.py"):
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if "STATA-QUIRK:" in line:
                reason = line.split("STATA-QUIRK:", 1)[1].strip()
                j = i + 1
                while (
                    j < len(lines) and re.match(r"\s*#\s+\S", lines[j]) and "STATA" not in lines[j]
                ):
                    reason += " " + lines[j].strip().lstrip("# ")
                    j += 1
                markers.append((path.name, i + 1, reason))
    assert len(markers) >= 5, "the quirks listed in the plan are marked"
    for name, line, reason in markers:
        assert len(reason) >= 60, f"{name}:{line} gives no reason for the quirk"
