"""Monte Carlo experiments on the dynamic panel threshold estimator (layer 6).

``monte_carlo(design, n, t, reps=...)`` draws ``reps`` panels from a design of
:mod:`~pyxtdpthresh.extras.simulation.dgp`, estimates each one with the validated estimator and
gathers what the literature reports: bias and RMSE of the threshold and of the slopes, coverage of
the confidence set of the threshold (grid bootstrap) and of the slopes (asymptotic intervals), the
rejection rate of the linearity test (**size** when the design has no threshold, **power**
otherwise) and the rejection rate of the alternative thresholds ``gamma + c`` (power of the test
by inversion of the confidence set).

Nothing here estimates in a new way: each replication is a call to the estimator.  Replication
``r`` uses the ``r``-th child of ``SeedSequence(seed)`` for its data and for its bootstrap, so the
result is a function of ``seed`` alone, whatever the number of ``workers``.

On Windows (and macOS), the worker processes are spawned: a script that asks for several workers
must be guarded by ``if __name__ == "__main__":``.
"""

from __future__ import annotations

import math
import os
import time
import warnings
from collections.abc import Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd

from pyxtdpthresh._errors import PyxdpthreshError, PyxdpthreshWarning, SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh.extras.reporting.extract import extract
from pyxtdpthresh.extras.robustness.sensitivity import accepted_segments
from pyxtdpthresh.extras.simulation.dgp import Design, resolve_design, simulate_panel
from pyxtdpthresh.models.xtdpthresh.fit import PointFit, fit_point

#: Alternative thresholds ``gamma + c`` whose rejection rate is reported, as in the paper.
DEFAULT_SHIFTS = (0.10, 0.25, 0.50)
#: Arguments of ``simulate_panel`` that are not parameters of the design.
GENERATOR_ARGUMENTS = ("burn", "unbalanced", "min_obs")
_LEVEL = 95.0


@dataclass(frozen=True)
class _Job:
    """Everything a worker needs to run one replication (picklable)."""

    rep: int
    design: Design
    n: int
    t: int
    seed: np.random.SeedSequence
    simulation: Mapping[str, Any]
    options: Mapping[str, Any]
    shifts: tuple[float, ...]
    alpha: float


def _init_worker() -> None:
    """One thread per worker: the processes, not the kernels, share the cores."""
    from pyxtdpthresh._config import set_options

    set_options(threads=1)


def _gamma_columns(fit: PointFit, design: Design, shifts: Sequence[float]) -> dict[str, Any]:
    """Threshold, its confidence set and the coverage / rejections they imply."""
    scalars = fit.scalars
    segments = accepted_segments(fit)
    record: dict[str, Any] = {
        "gamma": scalars["gamma"],
        "gamma_lo": scalars.get("gamma_lo", math.nan),
        "gamma_hi": scalars.get("gamma_hi", math.nan),
        "ci_nseg": scalars.get("ci_nseg", math.nan),
        "ci_complete": segments is not None,
        "cover_segments": None,
        "cover_hull": None,
    }
    for shift in (0.0, *shifts):
        record[f"reject_{shift:g}"] = None
    if segments is None or not design.has_threshold:
        return record
    for shift in (0.0, *shifts):
        target = design.gamma + shift
        held = bool(np.any((segments[:, 0] <= target) & (target <= segments[:, 1])))
        record[f"reject_{shift:g}"] = not held
    record["cover_segments"] = not record["reject_0"]
    hull = (float(np.min(segments[:, 0])), float(np.max(segments[:, 1])))
    record["cover_hull"] = hull[0] <= design.gamma <= hull[1]
    return record


def _slope_columns(fit: PointFit, design: Design, z: float) -> dict[str, Any]:
    """Estimate, standard error and coverage of every coefficient the design has a truth for."""
    estimates = extract(fit).coefs
    record: dict[str, Any] = {}
    for name, truth in design.truth.items():
        if name == "gamma":
            continue
        block, _, variable = name.partition(":")
        estimate = estimates.get((block, variable))
        if estimate is None:
            continue
        record[f"b:{name}"] = estimate.b
        record[f"se:{name}"] = estimate.se
        record[f"cover:{name}"] = (
            bool(abs(estimate.b - truth) <= z * estimate.se) if math.isfinite(estimate.se) else None
        )
    return record


def _record(
    fit: PointFit, design: Design, shifts: Sequence[float], alpha: float, z: float
) -> dict[str, Any]:
    scalars = fit.scalars
    p_linearity = scalars.get("pval_lin", math.nan)
    record = _gamma_columns(fit, design, shifts)
    record.update(_slope_columns(fit, design, z))
    record["pval_lin"] = p_linearity
    record["reject_linearity"] = bool(p_linearity < alpha) if math.isfinite(p_linearity) else None
    record["n_obs"] = scalars.get("N", math.nan)
    record["n_units"] = scalars.get("N_units", math.nan)
    record["n_instruments"] = scalars.get("N_iv", math.nan)
    return record


def _replicate(job: _Job) -> dict[str, Any]:
    """Draw the panel of one replication, estimate it and return its record."""
    data_seed, boot_seed = job.seed.spawn(2)
    frame = simulate_panel(job.design, job.n, job.t, seed=data_seed, **job.simulation)
    options = {
        **job.design.arguments(),
        **job.options,
        "seed": int(boot_seed.generate_state(1)[0] & 0x7FFFFFFF),
    }
    z = NormalDist().inv_cdf(0.5 + float(options.get("level", _LEVEL)) / 200.0)
    base: dict[str, Any] = {"rep": job.rep, "status": "ok", "error": "", "key": None}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PyxdpthreshWarning)
            fit = fit_point(frame, "y", id="id", time="t", **options)
        return base | _record(fit, job.design, job.shifts, job.alpha, z)
    except PyxdpthreshError as error:
        return base | {"status": "failed", "error": str(error), "key": error.key}


def _statistics(values: pd.Series, truth: float) -> dict[str, float]:
    """Bias, RMSE and spread of the finite estimates of one parameter."""
    valid = values.dropna().to_numpy(dtype=float)
    count = len(valid)
    if count == 0:
        empty = dict.fromkeys(("mean", "bias", "bias_mcse", "median_bias", "sd", "rmse"), math.nan)
        return {"n": 0.0, **empty}
    errors = valid - truth
    spread = float(np.std(valid, ddof=1)) if count > 1 else math.nan
    return {
        "n": float(count),
        "mean": float(np.mean(valid)),
        "bias": float(np.mean(errors)),
        "bias_mcse": spread / math.sqrt(count) if count > 1 else math.nan,
        "median_bias": float(np.median(errors)),
        "sd": spread,
        "rmse": float(math.sqrt(np.mean(errors**2))),
    }


def rate(column: pd.Series) -> tuple[float, float, int]:
    """Share of ``True`` among the defined values of ``column``, its Monte Carlo error and count."""
    valid = column.dropna().astype(bool)
    count = len(valid)
    if count == 0:
        return math.nan, math.nan, 0
    share = float(valid.mean())
    return share, math.sqrt(share * (1.0 - share) / count), count


@dataclass(frozen=True)
class MonteCarloResult:
    """The replications of a Monte Carlo experiment and what they say.

    Attributes
    ----------
    design
        The data generating process.
    n, t, reps
        Units, periods and number of replications asked.
    seed
        Seed of the experiment (drawn and recorded when none was given).
    alpha
        Level of the linearity test.
    shifts
        The ``c`` of the alternative thresholds ``gamma + c``.
    records
        One row per replication (``status`` is ``failed`` when the estimation raised).
    options, simulation
        The options passed to the estimator and to the generator.
    elapsed
        Wall-clock seconds of the experiment.
    """

    design: Design
    n: int
    t: int
    reps: int
    seed: int
    alpha: float
    shifts: tuple[float, ...]
    records: pd.DataFrame
    options: Mapping[str, Any] = field(default_factory=dict)
    simulation: Mapping[str, Any] = field(default_factory=dict)
    elapsed: float = math.nan

    @property
    def ok(self) -> pd.DataFrame:
        """The replications that were estimated."""
        return self.records[self.records["status"] == "ok"]

    @property
    def n_failed(self) -> int:
        """Number of replications whose estimation raised."""
        return int((self.records["status"] != "ok").sum())

    def to_dataframe(self) -> pd.DataFrame:
        """Return the replications, one row each."""
        return self.records.copy()

    def estimates(self) -> pd.DataFrame:
        """Bias, RMSE and coverage of the threshold and of every slope, by parameter."""
        ok, truth = self.ok, self.design.truth
        rows: dict[str, dict[str, float]] = {}
        if self.design.has_threshold:
            rows["gamma"] = {"truth": truth["gamma"], **_statistics(ok["gamma"], truth["gamma"])}
            share, error, count = rate(ok["cover_segments"])
            rows["gamma"] |= {"coverage": share, "coverage_mcse": error, "n_coverage": count}
        for name, value in truth.items():
            if name == "gamma" or ok[f"b:{name}"].notna().sum() == 0:
                continue  # not estimated (every run failed, or the model has no such term)
            row = {"truth": value, **_statistics(ok[f"b:{name}"], value)}
            share, error, count = rate(ok[f"cover:{name}"])
            rows[name] = row | {"coverage": share, "coverage_mcse": error, "n_coverage": count}
        return pd.DataFrame.from_dict(rows, orient="index").rename_axis("parameter")

    def threshold_coverage(self) -> pd.DataFrame:
        """Coverage of the true threshold by the confidence set (segments and hull)."""
        ok = self.ok
        rows = {}
        for use, column in (("segments", "cover_segments"), ("hull", "cover_hull")):
            share, error, count = rate(ok[column])
            rows[use] = {"coverage": share, "mcse": error, "n": count}
        frame = pd.DataFrame.from_dict(rows, orient="index").rename_axis("set")
        frame["incomplete"] = (
            float(1.0 - ok["ci_complete"].astype(bool).mean()) if len(ok) else math.nan
        )
        return frame

    def linearity(self) -> dict[str, float | str]:
        """Rejection rate of the linearity test: ``size`` without threshold, ``power`` with one."""
        share, error, count = rate(self.ok["reject_linearity"])
        kind = "power" if self.design.has_threshold else "size"
        return {"kind": kind, "alpha": self.alpha, "rate": share, "mcse": error, "n": count}

    def power(self) -> pd.DataFrame:
        """Return the rejection rate of ``gamma = gamma_0 + c`` (``c = 0`` is the size)."""
        rows = {}
        for shift in (0.0, *self.shifts):
            share, error, count = rate(self.ok[f"reject_{shift:g}"])
            rows[shift] = {"rejection": share, "mcse": error, "n": count}
        return pd.DataFrame.from_dict(rows, orient="index").rename_axis("shift")

    def summary(self) -> str:
        """Return a short text report of the experiment (English)."""
        lines = [
            f"Monte Carlo: design {self.design.name}, n = {self.n}, T = {self.t}, "
            f"{self.reps} replications ({self.n_failed} failed), seed {self.seed}",
            self.estimates().round(4).to_string(),
        ]
        if self.design.has_threshold:
            lines += [self.threshold_coverage().round(4).to_string()]
        lin = self.linearity()
        lines.append(f"linearity test, {lin['kind']} at {self.alpha:g}: {lin['rate']:.4f}")
        return "\n".join(lines)


def _columns(design: Design, shifts: Sequence[float]) -> list[str]:
    """Columns of the records, in a fixed order (present even if every replication failed)."""
    names = ["rep", "status", "error", "key", "gamma", "gamma_lo", "gamma_hi", "ci_nseg"]
    names += ["ci_complete", "cover_segments", "cover_hull"]
    names += [f"reject_{shift:g}" for shift in (0.0, *shifts)]
    for name in design.truth:
        if name != "gamma":
            names += [f"b:{name}", f"se:{name}", f"cover:{name}"]
    return [*names, "pval_lin", "reject_linearity", "n_obs", "n_units", "n_instruments"]


def _check_experiment(reps: int, alpha: float, workers: int | None) -> None:
    if int(reps) != reps or reps < 1:
        raise SpecificationError(
            message("sim_bad_size", name="reps", minimum=1, value=reps), key="sim_bad_size"
        )
    if not 0.0 < alpha < 1.0:
        raise SpecificationError(message("sim_bad_alpha", value=alpha), key="sim_bad_alpha")
    if workers is not None and (int(workers) != workers or workers < 1):
        raise SpecificationError(
            message("sim_bad_size", name="workers", minimum=1, value=workers), key="sim_bad_size"
        )


def monte_carlo(
    design: str | Design = "gong_seo",
    n: int = 400,
    t: int = 6,
    *,
    reps: int = 200,
    seed: int | None = None,
    workers: int | None = None,
    alpha: float = 0.05,
    shifts: Sequence[float] = DEFAULT_SHIFTS,
    simulation: Mapping[str, Any] | None = None,
    **options: Any,
) -> MonteCarloResult:
    """Run a Monte Carlo experiment on ``xtdpthresh``.

    Parameters
    ----------
    design
        A name of :data:`~pyxtdpthresh.extras.simulation.dgp.DESIGNS` or a ``Design``.
    n, t
        Units and periods of each panel.
    reps
        Number of replications.
    seed
        Seed of the experiment: the result is a function of it alone (drawn and recorded when
        ``None``).  Replication ``r`` uses the ``r``-th child of ``SeedSequence(seed)``.
    workers
        Processes (one thread each).  ``None`` uses ``min(cpu_count, reps)``; ``1`` runs in this
        process with every thread.  The result does not depend on it.
    alpha
        Level of the linearity test.
    shifts
        The ``c`` of the alternative thresholds ``gamma + c`` whose rejection rate is reported.
    simulation
        Parameters of the generator (``jump``, ``unbalanced``, ``burn``, any parameter of the
        design).
    **options
        Options of the estimator (``n_boot``, ``grid``, ``grid_ci``, ``level``...); they override
        the arguments of the design (roles of the variables, ``collapse``).

    Returns
    -------
    MonteCarloResult
    """
    _check_experiment(reps, alpha, workers)
    spec = resolve_design(design)
    simulation = dict(simulation or {})
    drawing = {k: simulation.pop(k) for k in GENERATOR_ARGUMENTS if k in simulation}
    spec = resolve_design(spec, **simulation)  # what is left are parameters of the design
    if seed is None:
        seed = int(np.random.SeedSequence().generate_state(1)[0])
    children = np.random.SeedSequence(seed).spawn(reps)
    jobs = [
        _Job(r, spec, n, t, children[r], drawing, options, tuple(float(c) for c in shifts), alpha)
        for r in range(reps)
    ]
    count = min(os.cpu_count() or 1, reps) if workers is None else min(workers, reps)
    started = time.perf_counter()
    if count == 1:
        rows = [_replicate(job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=count, initializer=_init_worker) as pool:
            rows = list(pool.map(_replicate, jobs, chunksize=max(1, reps // (4 * count))))
    elapsed = time.perf_counter() - started
    grid = tuple(float(c) for c in shifts)
    records = pd.DataFrame(rows).reindex(columns=_columns(spec, grid))
    return MonteCarloResult(
        spec, n, t, reps, seed, alpha, grid, records, options, {**simulation, **drawing}, elapsed
    )
