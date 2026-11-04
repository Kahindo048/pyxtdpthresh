"""The self-exciting designs of Seo and Shin (2016): simulate, estimate, and look at the spread.

In these designs the threshold variable is the lagged outcome, ``q = y(t-1)``, so it is endogenous.
One estimate says little; a small Monte Carlo shows how the estimated threshold and the coverage of
its confidence set behave. The tables of the paper use 1,000 replications; this example runs a few
so that it finishes in seconds.

Run:  python examples/02_seo_shin_simulation.py [output_directory]
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pyxtdpthresh as pyx  # noqa: E402
from pyxtdpthresh.extras.simulation import resolve_design  # noqa: E402

DESIGN, N, T = "seo_shin_jump", 200, 6
REPLICATIONS = 24


def main(out: Path) -> None:
    """Estimate one simulated panel, then run a small Monte Carlo experiment."""
    out.mkdir(parents=True, exist_ok=True)
    design = resolve_design(DESIGN)
    print("True values:", design.truth)

    # One panel: the call is the same as for real data; the design says which variable is q.
    panel = pyx.simulate_panel(DESIGN, N, T, seed=5)
    options = {k: v for k, v in design.arguments().items() if k != "y"}
    res = pyx.xtdpthresh(panel, "y", id="id", time="t", seed=1, **options)
    print(res.params.round(3).to_string())
    print(f"Threshold {res.gamma:.3f} (true {design.gamma}), interval {res.gamma_ci}")

    # Many panels: bias, coverage and the distribution of the estimated threshold.
    experiment = pyx.monte_carlo(
        DESIGN, N, T, reps=REPLICATIONS, seed=11, workers=2, n_boot=99, grid_ci=40
    )
    print(experiment.summary())
    experiment.to_dataframe().to_csv(out / "replications.csv", index=False)
    pyx.plot(experiment, "distribution", path=out / "distribution.png")


if __name__ == "__main__":  # the guard matters: the replications run in worker processes
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output_seo_shin"))
