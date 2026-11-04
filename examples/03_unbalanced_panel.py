"""An unbalanced panel: first differences against forward orthogonal deviations.

Drop 15 % of the observations of Hansen's panel at random, keep the firms with at least four
remaining observations, and estimate with both transformations, as in the help file of
``xtdpthresh``. (The help file draws the observations with Stata's generator; this script uses
NumPy's, so the sample is not the same one.) FOD keeps more equations when the panel has gaps.

Run:  python examples/03_unbalanced_panel.py [output_directory]
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")

import pyxtdpthresh as pyx  # noqa: E402

MODEL = {
    "q": "debt",
    "endogenous": ["cashflow", "tobin_q", "debt"],
    "maxlag": (3, 8),
    "collapse": True,
    "id": "firm",
    "time": "year",
    "seed": 12345,
}


def main(out: Path) -> None:
    """Make the panel unbalanced, estimate with FD and FOD, and compare."""
    out.mkdir(parents=True, exist_ok=True)
    df = pyx.load_dataset("invest")
    df = df[~df["firm"].isin([137, 391, 407, 488, 538])]
    rng = np.random.default_rng(20260418)
    df = df[rng.uniform(size=len(df)) >= 0.15]
    df = df[df.groupby("firm")["year"].transform("size") >= 4]
    print(f"{len(df)} firm-years, {df['firm'].nunique()} firms, not balanced")

    fd = pyx.xtdpthresh(df, "invest", method="fd", **MODEL)
    fod = pyx.xtdpthresh(df, "invest", method="fod", **MODEL)
    for name, res in (("FD", fd), ("FOD", fod)):
        print(f"{name}: {res.n_obs} equations, {res.n_instruments} instruments, "
              f"threshold {res.gamma:.4f}, interval {res.gamma_ci}")  # fmt: skip
    pyx.compare([fd, fod], model_names=["FD", "FOD"]).to_markdown(out / "table.md")
    (out / "settings_fd.txt").write_text(str(fd.settings_log()), encoding="utf-8")
    fod.plot("switch", path=out / "switch.png")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output_unbalanced"))
