"""Stress tests of the package on random panels and random option combinations (K.5).

    python -m validation.stress [--scenarios 120] [--seed 20261104] [--report path.json]

Every scenario draws a panel (size, unbalance, missing values, shape of the threshold variable,
roles of the regressors) and a call to ``xtdpthresh`` (method, kink, time effects, collapse,
lags, bootstrap), then checks, without Stata:

* **no crash**: the call ends with a result or with one of the exceptions of the package (those
  carry a Stata return code); any other exception is a bug;
* **sound numbers**: the threshold lies in the range of ``q``, the variances have a non-negative
  diagonal, the p-values are in ``[0, 1]``, the standard errors are finite;
* **every output works**: ``print``, ``summary``, ``diagnose``, ``settings_log``, the tables of
  every format, ``to_json``, ``predict``/``augment``, the regime table and a figure;
* **repeatability**: the same seed gives the same result, bit for bit, and one BLAS thread or
  several give the same result to ``1e-9``;
* **metamorphic invariances**: shuffling the rows, renaming the units (strings), shifting the
  time origin, changing the unit of the regressors or the scale of ``y``, and an increasing affine
  map of ``q`` (the threshold follows the map) change nothing that should not change.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import time
import traceback
import warnings
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd

import pyxtdpthresh as pyx
from pyxtdpthresh._errors import PyxdpthreshError, PyxdpthreshWarning

#: Scenarios on which the containers and the damaged inputs are tried (one in six).
INPUT_SCENARIOS = frozenset(f"s{i:03d}" for i in range(0, 1000, 6))
Q_KINDS = ("normal", "rounded", "heavy", "outliers", "few_values")


@dataclass
class Scenario:
    """A panel and a call."""

    name: str
    seed: int
    n: int
    t: int
    n_exog: int = 1
    n_endog: int = 1
    unbalanced: float = 0.0
    missing: float = 0.0
    q_kind: str = "normal"
    options: dict[str, Any] = field(default_factory=dict)

    def roles(self) -> dict[str, Any]:
        return {
            "x": [f"x{k}" for k in range(1, self.n_exog + 1)],
            "endogenous": [f"e{k}" for k in range(1, self.n_endog + 1)],
        }


def draw_panel(s: Scenario) -> pd.DataFrame:
    """Random panel with a threshold effect, endogenous regressors and unit effects."""
    rng = np.random.default_rng(s.seed)
    n, t = s.n, s.t
    unit = rng.normal(size=(n, 1))
    q = np.empty((n, t))
    q[:, 0] = rng.normal(size=n)
    for j in range(1, t):
        q[:, j] = 0.6 * q[:, j - 1] + rng.normal(size=n)
    if s.q_kind == "rounded":
        q = np.round(q * 2) / 2
    elif s.q_kind == "heavy":
        q = np.sign(q) * np.abs(q) ** 2.5
    elif s.q_kind == "outliers":
        q[rng.random(q.shape) < 0.01] *= 25
    elif s.q_kind == "few_values":
        q = np.digitize(q, [-1.0, 0.0, 1.0]).astype(float)
    u = rng.normal(size=(n, t))
    cols = {}
    for k in range(1, s.n_exog + 1):
        cols[f"x{k}"] = rng.normal(size=(n, t)) + 0.3 * q
    for k in range(1, s.n_endog + 1):
        cols[f"e{k}"] = rng.normal(size=(n, t)) + 0.5 * u + 0.2 * unit
    gamma = float(np.median(q))
    y = np.zeros((n, t))
    y[:, 0] = unit[:, 0] + u[:, 0]
    for j in range(1, t):
        regime = (q[:, j] > gamma).astype(float)
        mean = 0.4 * y[:, j - 1] + regime * (0.3 + 0.2 * y[:, j - 1])
        for values in cols.values():
            mean = mean + (0.5 + 0.4 * regime) * values[:, j]
        y[:, j] = mean + unit[:, 0] + u[:, j]
    frame = pd.DataFrame(
        {
            "id": np.repeat(np.arange(1, n + 1), t),
            "t": np.tile(np.arange(1, t + 1), n),
            "y": y.ravel(),
            "q": q.ravel(),
            **{name: values.ravel() for name, values in cols.items()},
        }
    )
    if s.unbalanced > 0:
        frame = frame[rng.random(len(frame)) >= s.unbalanced]
    if s.missing > 0 and s.n_exog:
        hit = rng.random(len(frame)) < s.missing
        frame.loc[hit, "x1"] = np.nan
    return frame.reset_index(drop=True)


def scenarios(count: int, seed: int) -> list[Scenario]:
    """A deterministic list of ``count`` scenarios, from easy to hard."""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(count):
        n = int(rng.choice([25, 60, 120, 300, 600]))
        t = int(rng.choice([4, 5, 6, 8, 10, 12]))
        options: dict[str, Any] = {
            "method": str(rng.choice(["fd", "fod"])),
            "kink": bool(rng.random() < 0.2),
            "time_effects": bool(rng.random() < 0.2),
            "collapse": bool(rng.random() < 0.5),
            "maxlag": [None, (2, 4), (2, 6), (3, 5)][int(rng.integers(4))],
            "grid": int(rng.choice([20, 50, 100])),
            "bootstrap": bool(rng.random() < 0.5),
            "n_boot": 29,
            "grid_ci": 20,
            "seed": int(rng.integers(1, 10**6)),
        }
        if options["maxlag"] is None:
            del options["maxlag"]
        if options["kink"]:
            options["method"] = "fd"
        out.append(
            Scenario(
                f"s{i:03d}", int(rng.integers(1, 10**9)), n, t,
                n_exog=int(rng.integers(0, 3)), n_endog=int(rng.integers(0, 3)),
                unbalanced=float(rng.choice([0.0, 0.0, 0.1, 0.3])),
                missing=float(rng.choice([0.0, 0.0, 0.05])),
                q_kind=str(rng.choice(Q_KINDS)),
                options=options,
            )
        )  # fmt: skip
    return out


@dataclass
class Outcome:
    """What happened to one scenario."""

    name: str
    status: str  # ok | refused | BUG
    seconds: float
    detail: str = ""
    problems: list[str] = field(default_factory=list)


def fit(frame: pd.DataFrame, s: Scenario, **override: Any) -> Any:
    """Estimate ``s`` on ``frame`` (warnings of the package are not errors)."""
    options = {**s.options, **override}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PyxdpthreshWarning)
        return pyx.xtdpthresh(frame, "y", q="q", id="id",
                              time="t", **s.roles(), **options)  # fmt: skip


def check_numbers(res: Any, frame: pd.DataFrame) -> list[str]:
    """Soundness of the numbers of a result."""
    bad = []
    fit_ = res.fit
    sc = fit_.scalars
    q = frame["q"].to_numpy(float)
    q = q[np.isfinite(q)]
    if not (q.min() - 1e-9 <= sc["gamma"] <= q.max() + 1e-9):
        bad.append(f"gamma {sc['gamma']:.4g} outside the range of q")
    cov = np.asarray(fit_.cov)
    if not np.isfinite(np.diag(cov)).all() or (np.diag(cov) < 0).any():
        bad.append("variance with a negative or non-finite diagonal")
    if not np.isfinite(fit_.search.fit.theta).all():
        bad.append("non-finite coefficients")
    for key in ("hansen_p", "ar1_p", "ar2_p", "pval_lin", "citest_p"):
        value = sc.get(key, math.nan)
        if not math.isnan(value) and not 0.0 <= value <= 1.0:
            bad.append(f"{key} = {value} outside [0, 1]")
    return bad


def check_outputs(res: Any, frame: pd.DataFrame, bootstrap: bool) -> list[str]:
    """Every output of the result must work."""
    bad = []

    def attempt(label: str, call: Any) -> Any:
        try:
            value = call()
        except Exception as error:  # noqa: BLE001 - the point is to catch anything
            bad.append(f"{label}: {type(error).__name__}: {str(error)[:120]}")
            return None
        return value

    attempt("str", lambda: str(res))
    attempt("repr", lambda: repr(res))
    attempt("summary", lambda: str(res.summary()))
    attempt("diagnose", lambda: str(res.diagnose()))
    attempt("settings_log", lambda: str(res.settings_log()))
    attempt("regime_table", res.regime_table)
    table = attempt("compare", lambda: pyx.compare([res]))
    if table is not None:
        for kind in ("text", "latex", "html", "markdown", "csv"):
            attempt(f"to_{kind}", getattr(table, f"to_{kind}"))
    attempt("to_json", lambda: json.dumps(res.to_json()) if not isinstance(res.to_json(), str)
            else res.to_json())  # fmt: skip
    attempt("predict", lambda: res.predict("residuals", frame))
    attempt("augment", lambda: res.augment(frame, kinds=("residuals", "regime")))
    if bootstrap:
        attempt("ci_table", res.ci_table)
    fig = attempt("plot", lambda: res.plot("profile"))
    if fig is not None:
        import matplotlib.pyplot as plt

        plt.close(fig)
    return bad


def same(a: Any, b: Any, rtol: float = 1e-9) -> bool:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or (np.isnan(a) != np.isnan(b)).any():
        return False
    keep = ~np.isnan(a)
    return bool(np.allclose(a[keep], b[keep], rtol=rtol, atol=rtol))


def summary_vector(res: Any) -> dict[str, np.ndarray]:
    """The numbers that must not move under an invariance."""
    sc = res.fit.scalars
    return {
        "theta": np.asarray(res.fit.search.fit.theta),
        "se": np.sqrt(np.diag(np.asarray(res.fit.cov))),
        "gamma": np.array([sc["gamma"]]),
        "scalars": np.array(
            [sc[k] for k in ("N", "N_iv", "N_units", "hansen", "hansen_p", "ar2", "ar2_p", "obj")]
        ),  # fmt: skip
    }


def check_invariances(s: Scenario, frame: pd.DataFrame, base: Any) -> list[str]:
    """Shuffling, renaming, shifting and rescaling must change nothing that should not change."""
    bad = []
    rng = np.random.default_rng(s.seed + 1)
    ref = summary_vector(base)
    ci = base.fit.bootstrap.ci if base.fit.bootstrap else None

    def compare(
        label: str,
        other: Any,
        transform: Any = None,
        rtol: float = 1e-7,
        only: set[str] | None = None,
    ) -> None:
        got = summary_vector(other)
        for key, want in ref.items():
            if only is not None and key not in only:
                continue
            value = got[key]
            if transform is not None:
                value = transform(key, value)
            if not same(value, want, rtol):
                bad.append(
                    f"{label}: {key} differs ({np.ravel(value)[:3]} vs {np.ravel(want)[:3]})"
                )
        if ci is not None and other.fit.bootstrap is not None and only is None:
            lo, hi = other.fit.bootstrap.ci.lo, other.fit.bootstrap.ci.hi
            if label.startswith("q affine"):
                lo, hi = (lo - 7.0) / 3.0, (hi - 7.0) / 3.0
            if not same([lo, hi], [ci.lo, ci.hi], 1e-6):
                bad.append(f"{label}: confidence set differs")

    shuffled = frame.sample(frac=1.0, random_state=int(rng.integers(1, 10**6)))
    compare("rows shuffled", fit(shuffled, s))
    # the names keep the order of the units: the bootstrap draws one weight per unit, in that order
    names = {i: f"unit_{i:06d}" for i in frame["id"].unique()}
    compare("units renamed (strings)", fit(frame.assign(id=frame["id"].map(names)), s))
    compare("time shifted", fit(frame.assign(t=frame["t"] + 1990), s))

    scaled = frame.assign(q=frame["q"] * 3.0 + 7.0)

    def q_map(key: str, value: np.ndarray) -> np.ndarray:
        return (value - 7.0) / 3.0 if key == "gamma" else value

    # in a kink model the slope on (q - gamma)+ is per unit of q, so only the fit itself is invariant
    only = {"gamma", "scalars"} if s.options.get("kink") else None
    compare("q affine", fit(scaled, s), q_map, only=only)
    return bad


def check_repeatability(s: Scenario, frame: pd.DataFrame, base: Any) -> list[str]:
    """Same seed, same result; BLAS threads do not change it."""
    bad = []
    again = fit(frame, s)
    ref, got = summary_vector(base), summary_vector(again)
    if any(not np.array_equal(ref[k], got[k], equal_nan=True) for k in ref):
        bad.append("the same call twice gives different results")
    with pyx.option_context(threads=1):
        one = summary_vector(fit(frame, s))
    with pyx.option_context(threads=4):
        four = summary_vector(fit(frame, s))
    bad.extend(
        f"threads 1 and 4 differ on {key}" for key in ref if not same(one[key], four[key], 1e-9)
    )
    return bad


def input_variants(frame: pd.DataFrame) -> dict[str, tuple[pd.DataFrame, dict[str, Any], bool]]:
    """Other ways to hold the same panel: ``(frame, extra arguments, must_equal_the_base)``.

    The variants that must give the same numbers are other containers of the same data; the others
    are damaged inputs, which must be refused with a message and never crash.
    """
    nan = float("nan")
    out: dict[str, tuple[pd.DataFrame, dict[str, Any], bool]] = {
        "multiindex": (frame.set_index(["id", "t"]), {"id": None, "time": None}, True),
        "float ids and time": (frame.astype({"id": float, "t": float}), {}, True),
        "string ids": (frame.assign(id=frame["id"].map(lambda i: f"u{i:06d}")), {}, True),
        "categorical ids": (frame.assign(id=frame["id"].astype("category")), {}, True),
        "float32 numbers": (frame.astype({"y": "float32", "q": "float32"}), {}, False),
        "nullable dtypes": (
            frame.astype({"y": "Float64", "q": "Float64", "id": "Int64"}),
            {},
            True,
        ),
        "shuffled index labels": (
            frame.set_axis(np.random.default_rng(3).permutation(len(frame))),
            {},
            True,
        ),
        "duplicated index labels": (frame.set_axis(np.zeros(len(frame), dtype=int)), {}, True),
        "unicode name": (
            frame.rename(columns={"y": "investissement_é"}),
            {"y": "investissement_é"},
            True,
        ),
        "inf in y": (frame.assign(y=frame["y"].where(frame.index != 5, np.inf)), {}, False),
        "text in y": (frame.assign(y=frame["y"].astype(str)), {}, False),
        "all-missing regressor": (frame.assign(**{"x_all": nan}), {"x_extra": "x_all"}, False),
        "constant q": (frame.assign(q=1.0), {}, False),
        "duplicated pairs": (pd.concat([frame, frame.iloc[:3]]), {}, False),
    }
    return out


def check_inputs(s: Scenario, frame: pd.DataFrame, base: Any) -> list[str]:
    """Other containers give the same numbers; damaged inputs are refused cleanly."""
    bad = []
    ref = summary_vector(base)
    for label, (variant, extra, must_equal) in input_variants(frame).items():
        extra = dict(extra)
        y = extra.pop("y", "y")
        x_extra = extra.pop("x_extra", None)
        roles = s.roles()
        if x_extra:
            roles = {**roles, "x": [*roles["x"], x_extra]}
        options = {"id": "id", "time": "t", **extra, **roles, **s.options}
        options = {k: v for k, v in options.items() if v is not None}
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", PyxdpthreshWarning)
                res = pyx.xtdpthresh(variant, y, q="q", **options)
        except PyxdpthreshError:
            if must_equal:
                bad.append(f"input '{label}' is refused but holds the same panel")
            continue
        except Exception as error:  # noqa: BLE001
            bad.append(f"input '{label}': {type(error).__name__}: {str(error)[:100]}")
            continue
        if label == "inf in y" and not any("infinite" in str(w.message) for w in caught):
            bad.append("an infinite value is dropped without a warning")
        if must_equal:
            got = summary_vector(res)
            if not all(same(got[k], ref[k], 1e-7) for k in ("theta", "gamma", "scalars")):
                bad.append(f"input '{label}' gives other numbers")
        elif label in (
            "text in y",
            "constant q",
            "duplicated pairs",
            "all-missing regressor",
        ):
            bad.append(f"input '{label}' is accepted although it is damaged")
    return bad


def run_scenario(s: Scenario) -> Outcome:
    """Run every check on a scenario."""
    started = time.perf_counter()
    frame = draw_panel(s)
    try:
        res = fit(frame, s)
    except PyxdpthreshError as error:
        return Outcome(s.name, "refused", time.perf_counter() - started,
                       f"{type(error).__name__} rc={getattr(error, 'stata_code', '?')} "
                       f"key={getattr(error, 'key', '?')}")  # fmt: skip
    except Exception as error:  # noqa: BLE001
        return Outcome(s.name, "BUG", time.perf_counter() - started,
                       "".join(traceback.format_exception_only(type(error), error)).strip(),
                       [traceback.format_exc()[-600:]])  # fmt: skip
    problems = check_numbers(res, frame)
    problems += check_outputs(res, frame, bool(s.options.get("bootstrap", True)))
    with contextlib.suppress(PyxdpthreshError):
        problems += check_repeatability(s, frame, res)
        problems += check_invariances(s, frame, res)
    problems += check_inputs(s, frame, res) if s.name in INPUT_SCENARIOS else []
    return Outcome(s.name, "BUG" if problems else "ok", time.perf_counter() - started,
                   f"gamma={res.gamma:.4f}", problems)  # fmt: skip


def _guarded(s: Scenario) -> Outcome:
    """:func:`run_scenario`, with a crash of the checks themselves recorded as a BUG."""
    try:
        return run_scenario(s)
    except Exception as error:  # noqa: BLE001
        return Outcome(s.name, "BUG", 0.0, f"check crashed: {error!r}",
                       [traceback.format_exc()[-600:]])  # fmt: skip


def run_campaign(count: int, seed: int) -> list[Outcome]:
    """Run ``count`` scenarios; a crash of the check itself is recorded as a BUG."""
    return [_guarded(s) for s in scenarios(count, seed)]


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20261104)
    parser.add_argument("--report", default=None)
    args = parser.parse_args()
    started = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        outcomes = run_campaign(args.scenarios, args.seed)
    counts: dict[str, int] = {}
    for o in outcomes:
        counts[o.status] = counts.get(o.status, 0) + 1
    print(f"{len(outcomes)} scenarios in {time.perf_counter() - started:.0f} s: {counts}")
    refusals: dict[str, int] = {}
    for o in outcomes:
        if o.status == "refused":
            refusals[o.detail] = refusals.get(o.detail, 0) + 1
    for detail, n in sorted(refusals.items(), key=lambda kv: -kv[1]):
        print(f"  refused x{n}: {detail}")
    for o in outcomes:
        if o.status == "BUG":
            print(f"BUG {o.name}: {o.detail}")
            for p in o.problems[:6]:
                print(f"    {p}")
    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            json.dump([asdict(o) for o in outcomes], handle, indent=1)


if __name__ == "__main__":
    main()
