"""What the Monte Carlo graphs share: the experiments to draw and their names."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pyxtdpthresh._types import Lang
from pyxtdpthresh.extras.plotting.labels import label
from pyxtdpthresh.extras.simulation.montecarlo import MonteCarloResult

#: One or several experiments, or a mapping from a name to each experiment.
Experiments = MonteCarloResult | Sequence[MonteCarloResult] | Mapping[str, MonteCarloResult]


def experiment_name(result: MonteCarloResult, lang: Lang) -> str:
    """Name of an experiment: its sample size, periods and the jump of the design."""
    if not result.design.has_threshold:
        return label("mc_name_linear", lang, n=result.n, t=result.t)
    jump = f"{round(result.design.jump, 6):g}"
    return label(
        "mc_name",
        lang,
        n=result.n,
        t=result.t,
        jump=jump.replace(".", ",") if lang == "fr" else jump,
    )


def named(results: Experiments, lang: Lang) -> list[tuple[str, MonteCarloResult]]:
    """Return the experiments as ``(name, result)`` pairs, naming those the caller did not."""
    if isinstance(results, MonteCarloResult):
        results = [results]
    if isinstance(results, Mapping):
        return [(str(name), result) for name, result in results.items()]
    runs = list(results)
    names = [experiment_name(result, lang) for result in runs]
    designs = {result.design.name for result in runs}
    if len(designs) > 1:  # several designs: say which one each row is
        names = [f"{run.design.name}: {name}" for run, name in zip(runs, names, strict=True)]
    return list(zip(names, runs, strict=True))


def level_of(results: Sequence[MonteCarloResult]) -> float:
    """Confidence level (in %) the experiments were run at (that of the first one)."""
    return float(results[0].options.get("level", 95.0))
