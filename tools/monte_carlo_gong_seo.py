"""Coverage experiments of the design of Gong and Seo (section 5, Table 1) with the package.

Runs the design ``gong_seo`` for the sample sizes and jumps ``delta_1 + delta_3 gamma`` asked and
writes, under ``docs/montecarlo/<tag>/``, the replications of each cell (CSV), the coverage table
and the three graphs in English and French.  Run from the project root:

    PYTHONPATH=. python tools/monte_carlo_gong_seo.py --reps 200 --jumps 0 0.1 0.2 0.5 1 --n 400

On Windows the worker processes are spawned, hence the ``__main__`` guard.  The paper uses 2000
replications and 500 bootstrap draws; ``--boot-type unit`` is the algorithm 1 of the paper (it
resamples the units) and is about 80 times slower than the default wild bootstrap.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pyxtdpthresh.extras.simulation import coverage_report, coverage_table, monte_carlo

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Run the cells and write the report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reps", type=int, default=200)
    parser.add_argument("--n", type=int, nargs="+", default=[400])
    parser.add_argument("--t", type=int, default=6)
    parser.add_argument("--jumps", type=float, nargs="+", default=[0.0, 0.1, 0.2, 0.5, 1.0])
    parser.add_argument("--n-boot", type=int, default=500)
    parser.add_argument("--boot-type", default="wild", choices=["wild", "unit"])
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--tag", default="gong_seo_wild")
    args = parser.parse_args()

    out = ROOT / "docs" / "montecarlo" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for n in args.n:
        for jump in args.jumps:
            name = f"n = {n}, jump = {jump:g}"
            run = monte_carlo(
                "gong_seo", n, args.t, reps=args.reps, seed=args.seed, workers=args.workers,
                n_boot=args.n_boot, grid=100, grid_ci=100, boot_type=args.boot_type,
                simulation={"jump": jump},
            )  # fmt: skip
            run.to_dataframe().to_csv(out / f"records_n{n}_jump{jump:g}.csv", index=False)
            results[name] = run
            cover = run.threshold_coverage().loc["segments", "coverage"]
            print(f"{name}: {run.elapsed:.0f} s, failed {run.n_failed}, coverage {cover:.3f}")
    coverage_report(results, out, stem="coverage")
    table = coverage_table(results)
    table.to_csv(out / "coverage_table.csv", index=False)
    (out / "settings.json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")
    print(
        table[
            [
                "experiment",
                "reps",
                "failed",
                "gamma_bias",
                "gamma_rmse",
                "coverage_segments",
                "coverage_hull",
                "incomplete",
                "linearity_rate",
            ]
        ]
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    main()
