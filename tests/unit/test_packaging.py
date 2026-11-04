"""The distribution carries the licence and the credits, and the metadata is valid."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import check_install  # noqa: E402

tomllib = pytest.importorskip("tomllib")  # Python 3.11 and later
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_the_licence_is_an_spdx_expression_and_its_files_are_distributed():
    meta = PROJECT["project"]
    assert meta["license"] == "MIT"
    assert set(meta["license-files"]) == {"LICENSE", "NOTICE.md"}
    assert all((ROOT / name).is_file() for name in meta["license-files"])
    assert not any(c.startswith("License ::") for c in meta["classifiers"])  # the SPDX field rules
    assert "tool.setuptools" not in PROJECT or "license-files" not in PROJECT["tool"]["setuptools"]


def test_the_build_backend_understands_the_spdx_licence_field():
    requirement = PROJECT["build-system"]["requires"][0]
    assert requirement.startswith("setuptools>=") and int(requirement.split(">=")[1]) >= 77


def test_the_notice_names_the_authors_of_the_programs_and_the_papers():
    text = (ROOT / "NOTICE.md").read_text(encoding="utf-8")
    for name in ("Myung Hwan Seo", "Sueyoul Kim", "Young-Joo Kim", "Duy Chinh Nguyen",
                 "Nhat Duy Lai", "Gong", "Hansen", "Windmeijer", "MIT License"):  # fmt: skip
        assert name in text
    assert "not part of" in text  # the Stata programs are not distributed


def test_the_manifest_leaves_out_generated_outputs():
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "prune validation/out" in manifest and "NOTICE.md" in manifest


def test_the_citation_file_credits_the_programs_and_the_papers():
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    for fragment in ("Nguyen", "Lai", "Gong", "Hansen", "Seo", "Kim"):
        assert fragment in text


@pytest.mark.slow
@pytest.mark.skipif(
    importlib.util.find_spec("build") is None or importlib.util.find_spec("twine") is None,
    reason="build and twine are needed",
)
def test_the_wheel_and_the_sdist_hold_what_they_must(tmp_path):
    check = check_install
    check.run([sys.executable, "-m", "build", "--outdir", str(tmp_path)], ROOT)
    check.check_contents(next(tmp_path.glob("*.whl")), next(tmp_path.glob("*.tar.gz")))
