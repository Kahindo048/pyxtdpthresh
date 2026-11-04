"""Bias, standard error, MSE and coverage on the designs of Seo and Shin (2016, section 6).

Runs the self-exciting designs ``seo_shin_jump`` (equation (16), Tong) and ``seo_shin_cont``
(equation (17), Chan and Tsay) for T = 10 and the sample sizes asked, with the package's FD-GMM
(no averaging of weight matrices), and writes under ``docs/montecarlo/<tag>/`` the replications of
each cell (CSV) and a comparison table with the numbers of their Tables 1 to 3.  Run from the
project root:

    PYTHONPATH=. python tools/monte_carlo_seo_shin.py --reps 300 --n 50 100 200

The paper uses 1,000 iterations.  The parameters of its tables are ``gamma`` (threshold), ``beta``
(slope of ``y(-1)`` below the threshold) and ``delta_1``, ``delta_2`` (changes of the intercept and
of the slope): ``lower:L.y``, ``change:_cons`` and ``change:L.y`` here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from pyxtdpthresh.extras.simulation import coverage_report, monte_carlo

ROOT = Path(__file__).resolve().parents[1]
#: Their Tables 1 (MSE), 2 (bias) and 3 (standard error), FD-GMM columns, by design and n.
PAPER = {
    ("seo_shin_jump", 50): {
        "mse": (0.063, 0.077, 0.179, 0.498), "bias": (-0.041, 0.005, -0.044, 0.100),
        "se": (0.247, 0.277, 0.421, 0.699),
    },
    ("seo_shin_jump", 100): {
        "mse": (0.089, 0.075, 0.207, 0.600), "bias": (-0.047, 0.007, -0.044, 0.095),
        "se": (0.294, 0.273, 0.452, 0.769),
    },
    ("seo_shin_jump", 200): {
        "mse": (0.066, 0.068, 0.174, 0.536), "bias": (-0.029, -0.011, -0.018, 0.098),
        "se": (0.255, 0.261, 0.417, 0.726),
    },
    ("seo_shin_cont", 50): {
        "mse": (0.077, 0.320, 0.588, 0.863), "bias": (0.057, 0.180, -0.288, 0.184),
        "se": (0.272, 0.537, 0.711, 0.911),
    },
    ("seo_shin_cont", 100): {
        "mse": (0.079, 0.383, 0.677, 1.002), "bias": (0.064, 0.145, -0.271, 0.199),
        "se": (0.274, 0.601, 0.777, 0.981),
    },
    ("seo_shin_cont", 200): {
        "mse": (0.083, 0.383, 0.662, 0.963), "bias": (0.074, 0.190, -0.298, 0.162),
        "se": (0.279, 0.589, 0.757, 0.968),
    },
}  # fmt: skip
PARAMETERS = ("gamma", "lower:L.y", "change:_cons", "change:L.y")
LABELS = ("gamma", "beta", "delta1", "delta2")


def comparison(name: str, n: int, run: object) -> pd.DataFrame:
    """Package and paper statistics of one cell, one row per parameter."""
    estimates = run.estimates()  # type: ignore[attr-defined]
    paper = PAPER[(name, n)]
    rows = []
    for position, (parameter, label) in enumerate(zip(PARAMETERS, LABELS, strict=True)):
        row = estimates.loc[parameter]
        rows.append(
            {
                "design": name, "n": n, "parameter": label,
                "bias": row["bias"], "bias_paper": paper["bias"][position],
                "se": row["sd"], "se_paper": paper["se"][position],
                "mse": row["rmse"] ** 2, "mse_paper": paper["mse"][position],
                "coverage": row["coverage"],
            }
        )  # fmt: skip
    return pd.DataFrame(rows)


def main() -> None:
    """Run the cells and write the comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reps", type=int, default=300)
    parser.add_argument("--n", type=int, nargs="+", default=[50, 100, 200])
    parser.add_argument("--designs", nargs="+", default=["seo_shin_jump", "seo_shin_cont"])
    parser.add_argument("--n-boot", type=int, default=199)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--tag", default="seo_shin")
    args = parser.parse_args()

    out = ROOT / "docs" / "montecarlo" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    results, tables = {}, []
    for name in args.designs:
        for n in args.n:
            run = monte_carlo(
                name, n, 10, reps=args.reps, seed=args.seed, workers=args.workers,
                n_boot=args.n_boot, grid=100, grid_ci=100,
            )  # fmt: skip
            run.to_dataframe().to_csv(out / f"records_{name}_n{n}.csv", index=False)
            results[f"{name}, n = {n}"] = run
            tables.append(comparison(name, n, run))
            gamma = run.threshold_coverage().loc["hull", "coverage"]
            print(f"{name} n={n}: {run.elapsed:.0f} s, failed {run.n_failed}, hull {gamma:.3f}")
    table = pd.concat(tables, ignore_index=True)
    table.to_csv(out / "comparison.csv", index=False)
    coverage_report(results, out, stem="coverage")
    (out / "settings.json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")
    print(table.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
