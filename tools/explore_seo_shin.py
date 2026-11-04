"""Exploration of the gap between the package and the tables of Seo and Shin (2016).

Replays the same simulated panels (same seeds) with variants of the estimation, to see which
feature explains the heavy tail of the threshold estimates seen in ``monte_carlo_seo_shin.py``:

``constants``  the estimator as it is (one constant instrument per equation, 44 at T = 10);
``noconst``    the same estimator without the constant instruments (36, as in the paper): the
               constant columns of the instrument matrix are zeroed, which removes them;
``onestep``    not implemented here (kept for the record: the paper uses a two-step estimator).

The variant is applied inside the worker processes, in this script only; nothing in the package
is changed.  Run from the project root:

    PYTHONPATH=. python tools/explore_seo_shin.py --variant noconst --design seo_shin_jump --n 200
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path

import numpy as np
import pandas as pd

from pyxtdpthresh.extras.simulation import coverage_table, monte_carlo
from pyxtdpthresh.extras.simulation import montecarlo as mc

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = {
    "gamma": "gamma",
    "beta": "lower:L.y",
    "delta1": "change:_cons",
    "delta2": "change:L.y",
}


def _without_constants() -> None:
    """Make the instrument builder leave out the constant instrument of every block."""
    from pyxtdpthresh.instruments import builder
    from pyxtdpthresh.models.xtdpthresh import stack

    original = builder.build_instruments

    def build(**kwargs):  # type: ignore[no-untyped-def]
        raw = original(**kwargs)
        layout = raw.layout
        if kwargs["settings"].collapse:
            columns = np.array([0])
        else:
            columns = np.arange(layout.n_blocks) * layout.block_width
        z = raw.z.copy()
        z[:, columns] = 0.0
        return builder.RawInstruments(z, raw.keep, raw.layout, raw.col_block)

    stack.build_instruments = build


def init_without_constants() -> None:
    """Worker initializer: one thread per worker (as the package does), then the variant."""
    mc._init_worker()
    _without_constants()


def statistics(run: mc.MonteCarloResult, truth: dict[str, float]) -> pd.DataFrame:
    """Bias, standard deviation, MSE, robust standard deviation and far share per parameter."""
    rows = []
    for label, key in PARAMETERS.items():
        column = "gamma" if key == "gamma" else f"b:{key}"
        values = run.ok[column].astype(float)
        errors = values - truth[key]
        iqr = (values.quantile(0.75) - values.quantile(0.25)) / 1.349
        scale = 0.5 if key == "gamma" else 1.0
        rows.append(
            {
                "parameter": label, "bias": errors.mean(), "median_bias": errors.median(),
                "sd": values.std(), "mse": float(np.mean(errors**2)), "robust_sd": iqr,
                "far": float((errors.abs() > scale).mean()),
            }
        )  # fmt: skip
    return pd.DataFrame(rows).set_index("parameter")


def main() -> None:
    """Run one variant on one cell and print the statistics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=["constants", "noconst"], default="constants")
    parser.add_argument("--design", default="seo_shin_jump")
    parser.add_argument("--n", type=int, default=200)
    parser.add_argument("--reps", type=int, default=300)
    parser.add_argument("--n-boot", type=int, default=199)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--tag", default="explore")
    parser.add_argument(
        "--opt", action="append", default=[], metavar="NAME=VALUE",
        help="an option of the estimator (repeatable), e.g. --opt trim=0.25 --opt bootstrap=False",
    )  # fmt: skip
    args = parser.parse_args()
    if args.variant == "noconst":
        mc._init_worker = init_without_constants  # the pool reads it when it is created
    options = {"grid": 100, "grid_ci": 100}
    options |= {k: ast.literal_eval(v) for k, v in (item.split("=", 1) for item in args.opt)}
    run = monte_carlo(
        args.design, args.n, 10, reps=args.reps, seed=args.seed, n_boot=args.n_boot, **options
    )
    out = ROOT / "docs" / "montecarlo" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    suffix = "".join(f"_{item.replace('=', '')}" for item in args.opt)
    stem = f"records_{args.design}_n{args.n}_{args.variant}{suffix}"
    run.to_dataframe().to_csv(out / f"{stem}.csv", index=False)
    print("options:", options)
    stats = statistics(run, run.design.truth)
    cover = run.threshold_coverage()
    table = coverage_table(run)
    print(f"{args.design} n={args.n} variant={args.variant}: {run.elapsed:.0f} s, ", end="")
    print(f"failed {run.n_failed}")
    print("instruments:", sorted(run.ok["n_instruments"].unique().tolist()))
    print(stats.round(3).to_string())
    print(
        "hull coverage", round(float(cover.loc["hull", "coverage"]), 3),
        "segments", round(float(cover.loc["segments", "coverage"]), 3),
        "incomplete", round(float(table["incomplete"].iloc[0]), 3),
        "linearity", round(float(table["linearity_rate"].iloc[0]), 3),
    )  # fmt: skip
    if math.isnan(float(cover.loc["hull", "coverage"])):
        print("no complete confidence set")


if __name__ == "__main__":
    main()
