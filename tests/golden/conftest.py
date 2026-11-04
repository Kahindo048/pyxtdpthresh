"""Optional recorder of the deviations the golden tests measure (for the validation report).

Set ``PYX_RECORD_DEVIATIONS`` to a file name and run ``pytest tests/golden``: every comparison
of the package with a frozen Stata value that goes through ``close`` (the helper of a test module),
``numpy.testing.assert_allclose`` or ``validation.compare.compare_arrays`` is appended to the file
as one JSON line (module, test, object, comparisons, largest absolute and relative deviation).
Without the variable the tests run untouched.  ``validation/report.py`` reads the file.
"""

from __future__ import annotations

import json
import math
import os
from typing import Any

import numpy as np
import pytest
from validation import compare

ENV = "PYX_RECORD_DEVIATIONS"


def deviation(got: Any, want: Any) -> tuple[int, float, float, float]:
    """Compared values, largest absolute and relative deviation, and the largest margin.

    The margin of a value is ``min(abs / ATOL, rel / RTOL)``: it is at most 1 when the value
    agrees with Stata under the rule of the project.
    """
    try:
        a, b = np.asarray(got, dtype=float), np.asarray(want, dtype=float)
    except (TypeError, ValueError):
        return 0, 0.0, 0.0, 0.0
    if a.shape != b.shape:
        if a.size == b.size and (a.ndim < 2 or b.ndim < 2 or 1 in a.shape and 1 in b.shape):
            a, b = a.ravel(), b.ravel()  # a vector and the same vector as a column or a row
        else:
            return int(b.size), math.inf, math.inf, math.inf
    if (np.isnan(a) != np.isnan(b)).any():
        return int(b.size), math.inf, math.inf, math.inf
    keep = ~(np.isnan(a) | np.isnan(b))
    if not keep.any():
        return 0, 0.0, 0.0, 0.0
    diff = np.abs(a[keep] - b[keep])
    rel = diff / np.maximum(np.abs(b[keep]), 1e-300)
    margin = np.minimum(diff / compare.ATOL, rel / compare.RTOL)
    return int(diff.size), float(diff.max()), float(rel.max()), float(margin.max())


@pytest.fixture(autouse=True)
def _record_deviations(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    path = os.environ.get(ENV)
    if not path:
        yield
        return
    records: list[dict[str, Any]] = []
    module = request.module.__name__.rsplit(".", 1)[-1]

    def note(what: str, got: Any, want: Any, rtol: float | None = None) -> None:
        n, abs_dev, rel_dev, margin = deviation(got, want)
        if n:
            record = {"module": module, "test": request.node.name, "object": what, "n": n,
                      "abs": abs_dev, "rel": rel_dev, "margin": margin}  # fmt: skip
            if rtol is not None and rtol > compare.RTOL:
                record["rtol"] = rtol  # a looser relative tolerance, declared by the test
            records.append(record)

    if hasattr(request.module, "close"):
        original = request.module.close

        def close(got: Any, want: Any, *rest: Any) -> Any:
            note(str(rest[0]) if rest else "value", got, want)
            return original(got, want, *rest)

        monkeypatch.setattr(request.module, "close", close)

    original_allclose = np.testing.assert_allclose

    def assert_allclose(actual: Any, desired: Any, *args: Any, **kwargs: Any) -> Any:
        note("value", actual, desired)
        return original_allclose(actual, desired, *args, **kwargs)

    monkeypatch.setattr(np.testing, "assert_allclose", assert_allclose)

    original_compare = compare.compare_arrays

    def compare_arrays(name: str, python: Any, stata: Any, *args: Any, **kwargs: Any) -> Any:
        note(name, python, stata, kwargs.get("rtol", args[1] if len(args) > 1 else None))
        return original_compare(name, python, stata, *args, **kwargs)

    monkeypatch.setattr(compare, "compare_arrays", compare_arrays)
    yield
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
