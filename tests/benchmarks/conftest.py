"""Speed benchmarks run on request: ``pytest -m bench`` (they take about a minute)."""

import pytest


def pytest_collection_modifyitems(config, items):
    if "bench" in (config.getoption("-m") or ""):
        return
    skip = pytest.mark.skip(reason="speed benchmarks run with: pytest -m bench")
    for item in items:
        if "benchmarks" in item.path.parts:
            item.add_marker(skip)
