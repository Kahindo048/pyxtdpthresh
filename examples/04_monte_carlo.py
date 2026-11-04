"""A Monte Carlo experiment: size and power of the linearity test, coverage of the threshold.

The design is equation (12) of Gong and Seo (2026), with a threshold variable that is an AR(1)
process correlated with the errors. The experiment is reproducible (``seed``) whatever the number of
worker processes. The paper uses far more replications; this example uses few, so the figures are
only an illustration of the tools.

Run:  python examples/04_monte_carlo.py [output_directory]
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pyxtdpthresh as pyx  # noqa: E402

N, T, REPLICATIONS = 200, 6, 24


def main(out: Path) -> None:
    """Run the experiment under the null and under the alternative; write tables and figures."""
    out.mkdir(parents=True, exist_ok=True)
    options = {"reps": REPLICATIONS, "seed": 3, "workers": 2, "n_boot": 99, "grid_ci": 40}

    # Under the alternative: a threshold effect exists. Coverage and power.
    effect = pyx.monte_carlo("gong_seo", N, T, **options)
    print(effect.summary())
    print("coverage of the threshold:", effect.threshold_coverage())

    # Under the null: no threshold. The rejection rate of the linearity test is its size.
    null = pyx.monte_carlo("linear", N, T, **options)
    print("size of the linearity test:", null.linearity())

    effect.to_dataframe().to_csv(out / "replications.csv", index=False)
    pyx.plot(effect, "coverage", path=out / "coverage.png")
    pyx.plot(effect, "power", path=out / "power.png")


if __name__ == "__main__":  # the guard matters: the replications run in worker processes
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output_monte_carlo"))
