"""Build the wheel and the sdist, install the wheel in a fresh environment and run it there.

    python tools/check_install.py

The check that a user's installation works, and not only the project's own checkout:

1. ``python -m build`` makes the sdist and the wheel in a temporary directory;
2. ``twine check`` validates their metadata;
3. the wheel holds the licence and the notice but no tests; the sdist holds the licence, the
   notice, the citation file and the PDFs of the documentation;
4. a new virtual environment installs the wheel (with its dependencies, from the index);
5. a script run there with ``-I`` from another directory estimates the model of the help file of
   ``xtdpthresh`` on the bundled panel and checks the threshold and its confidence set.

Needs network access for step 4.  Exits with an error message at the first failure.
"""

from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMOKE = """\
import importlib.metadata as md
import warnings

import matplotlib

matplotlib.use("Agg")
import pyxtdpthresh as pyx

assert "site-packages" in pyx.__file__, pyx.__file__
df = pyx.load_dataset("invest")
df = df[~df["firm"].isin([137, 391, 407, 488, 538])]
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    res = pyx.xtdpthresh(
        df, "invest", q="debt", endogenous=["cashflow", "tobin_q", "debt"], maxlag=(3, 8),
        collapse=True, id="firm", time="year", seed=12345,
    )
assert abs(res.gamma - 0.4194) < 5e-5, res.gamma
assert abs(res.gamma_ci[0] - 0.0122) < 5e-5, res.gamma_ci
assert md.version("pyxtdpthresh") == pyx.__version__
print("installed", pyx.__version__, "gamma", round(res.gamma, 4))
"""


def run(command: list[str], cwd: Path | None = None) -> str:
    """Run a command and return its output; stop with the output when it fails."""
    done = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace")  # fmt: skip
    if done.returncode != 0:
        raise SystemExit(f"{' '.join(command[:4])} failed:\n{(done.stdout + done.stderr)[-3000:]}")
    return done.stdout


def check_contents(wheel: Path, sdist: Path) -> None:
    """What the wheel and the sdist must and must not hold."""
    with zipfile.ZipFile(wheel) as z:
        names = z.namelist()
    licences = [n for n in names if "dist-info/licenses/" in n]
    if not {n.rsplit("/", 1)[1] for n in licences} >= {"LICENSE", "NOTICE.md"}:
        raise SystemExit(f"the wheel lacks the licence or the notice: {licences}")
    if any(n.startswith(("tests/", "validation/", "docs/")) for n in names):
        raise SystemExit("the wheel holds files that are not the package")
    with tarfile.open(sdist) as t:
        members = t.getnames()
    for need in ("LICENSE", "NOTICE.md", "CITATION.cff", "docs/user_guide.pdf",
                 "docs/validation_appendix.tex"):  # fmt: skip
        if not any(n.endswith("/" + need) for n in members):
            raise SystemExit(f"the sdist lacks {need}")
    if any("/validation/out/" in n or n.endswith(".log") for n in members):
        raise SystemExit("the sdist holds generated outputs")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        dist = work / "dist"
        run([sys.executable, "-m", "build", "--outdir", str(dist)], ROOT)
        wheel = next(dist.glob("*.whl"))
        sdist = next(dist.glob("*.tar.gz"))
        run([sys.executable, "-m", "twine", "check", str(wheel), str(sdist)])
        check_contents(wheel, sdist)
        env = work / "env"
        run([sys.executable, "-m", "venv", str(env)])
        python = env / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        run([str(python), "-m", "pip", "install", "-q", str(wheel)])
        elsewhere = work / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / "smoke.py").write_text(SMOKE, encoding="utf-8")
        print(run([str(python), "-I", "smoke.py"], elsewhere).strip())
    print("the wheel and the sdist are sound")


if __name__ == "__main__":
    main()
