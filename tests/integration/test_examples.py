"""The code of the README and the example scripts run as written and write what they announce."""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.slow


def run(args, cwd):
    env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT / "src"), env.get("PYTHONPATH", "")])
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=600
    )


def test_the_quick_start_of_the_readme_runs_as_written(tmp_path):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    code = re.search(r"```python\n(.*?)```", readme, re.S).group(1)
    done = run(["-c", code], tmp_path)
    assert done.returncode == 0, done.stderr[-1500:]
    assert "Threshold Estimates" in done.stdout and "Threshold Effect Test" in done.stdout
    assert "Diagnostic Tests" in done.stdout and "Crit5" in done.stdout
    assert (tmp_path / "table.tex").exists() and (tmp_path / "regimes.png").exists()
    assert "0.4194" in done.stdout  # the threshold quoted in the README


def test_the_code_of_the_user_guide_runs_as_written(tmp_path):
    guide = (ROOT / "docs" / "user_guide.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", guide, re.S)
    run_blocks = [b for b in blocks if not b.startswith("# not run by the tests")]
    assert len(run_blocks) >= 12 and len(run_blocks) < len(blocks)
    script = tmp_path / "guide.py"
    script.write_text("\n".join(run_blocks), encoding="utf-8")
    done = run([str(script)], tmp_path)
    assert done.returncode == 0, done.stderr[-2000:]
    assert (tmp_path / "profile.png").exists()
    # the diagnoses and the table of instrument sets quoted in the text are what the code prints
    for line in re.findall(r"^\[(?:warning|notice)\] .*$", guide, re.M):
        assert line in done.stdout, line
    for row in ("collapsed, lags 3-8      0.4194", "not collapsed, all lags  0.1092"):
        assert row in done.stdout, row


EXAMPLES = {
    "01_hansen_investment": ("table.tex", "table.md", "profile.png", "ci.png", "fit.json"),
    "02_seo_shin_simulation": ("replications.csv", "distribution.png"),
    "03_unbalanced_panel": ("table.md", "settings_fd.txt", "switch.png"),
    "04_monte_carlo": ("replications.csv", "coverage.png", "power.png"),
}


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_each_example_runs_and_writes_its_files(name, tmp_path):
    done = run([str(ROOT / "examples" / f"{name}.py"), str(tmp_path / "out")], tmp_path)
    assert done.returncode == 0, done.stderr[-1500:]
    for file in EXAMPLES[name]:
        assert (tmp_path / "out" / file).stat().st_size > 0, file
