"""Data generators and Monte Carlo."""

from pyxtdpthresh.extras.simulation.dgp import DESIGNS, Design, resolve_design, simulate_panel
from pyxtdpthresh.extras.simulation.montecarlo import (
    DEFAULT_SHIFTS,
    MonteCarloResult,
    monte_carlo,
)
from pyxtdpthresh.extras.simulation.report import (
    coverage_markdown,
    coverage_report,
    coverage_table,
)

__all__ = [
    "DEFAULT_SHIFTS",
    "DESIGNS",
    "Design",
    "MonteCarloResult",
    "coverage_markdown",
    "coverage_report",
    "coverage_table",
    "monte_carlo",
    "resolve_design",
    "simulate_panel",
]
