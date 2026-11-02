"""Comparison of Python results with the outputs exported from Stata.

Tolerance rule (four-decimal agreement): an element agrees when its absolute difference is
at most ``ATOL`` (5e-5) **or** its relative difference is at most ``RTOL`` (1e-6).  The
relative branch keeps the rule meaningful for large values (instrument counts, objective
values in the thousands) where an absolute 5e-5 would be stricter than four decimals.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

ATOL = 5e-5
RTOL = 1e-6


@dataclass(frozen=True)
class Diff:
    """Comparison of one named object."""

    name: str
    shape_python: tuple[int, ...]
    shape_stata: tuple[int, ...]
    max_abs: float
    max_rel: float
    ok: bool

    def line(self) -> str:
        status = "OK  " if self.ok else "FAIL"
        if self.shape_python != self.shape_stata:
            return f"{status} {self.name:<14} shape {self.shape_python} vs {self.shape_stata}"
        stats = f"max|abs| = {self.max_abs:.3e}   max|rel| = {self.max_rel:.3e}"
        return f"{status} {self.name:<14} {stats}"


def read_matrix(path: Path) -> np.ndarray:
    """Read a CSV written by the Stata ``pyx_export`` helper (missing values become NaN)."""
    rows = [
        [np.nan if f.strip() in ("", ".") else float(f) for f in raw.split(",")]
        for raw in path.read_text(encoding="ascii").splitlines()
        if raw.strip()
    ]
    return np.array(rows, dtype=float)


def load_stata(out_dir: Path, tag: str) -> dict[str, np.ndarray]:
    """All exported objects of one case: ``{name: array}`` from ``<tag>_<name>.csv``."""
    found = {}
    for path in sorted(out_dir.glob(f"{tag}_*.csv")):
        found[path.stem[len(tag) + 1 :]] = read_matrix(path)
    if not found:
        raise FileNotFoundError(f"No exported file for case {tag!r} in {out_dir}")
    return found


def compare_arrays(
    name: str, python: np.ndarray, stata: np.ndarray, atol: float = ATOL, rtol: float = RTOL
) -> Diff:
    """Compare two arrays element by element (NaN must be NaN on both sides)."""
    a = np.atleast_2d(np.asarray(python, dtype=float))
    b = np.atleast_2d(np.asarray(stata, dtype=float))
    # a column vector and its transpose are the same object for our purposes
    if a.shape != b.shape and a.T.shape == b.shape and 1 in a.shape:
        a = a.T
    if a.shape != b.shape:
        return Diff(name, a.shape, b.shape, np.inf, np.inf, False)
    both_nan = np.isnan(a) & np.isnan(b)
    one_nan = np.isnan(a) ^ np.isnan(b)
    if one_nan.any():
        return Diff(name, a.shape, b.shape, np.inf, np.inf, False)
    diff = np.abs(a - b)[~both_nan]
    scale = np.maximum(np.abs(b), 1e-300)[~both_nan]
    rel = diff / scale
    max_abs = float(diff.max()) if diff.size else 0.0
    max_rel = float(rel.max()) if rel.size else 0.0
    ok = bool(np.all((diff <= atol) | (rel <= rtol)))
    return Diff(name, a.shape, b.shape, max_abs, max_rel, ok)


def compare_case(
    python: dict[str, np.ndarray],
    stata: dict[str, np.ndarray],
    atol: float = ATOL,
    rtol: float = RTOL,
) -> list[Diff]:
    """Compare every object present on the Stata side; a missing Python object fails."""
    diffs = []
    for name, expected in stata.items():
        if name not in python:
            diffs.append(Diff(name, (), expected.shape, np.inf, np.inf, False))
        else:
            diffs.append(compare_arrays(name, python[name], expected, atol, rtol))
    return diffs


def report(tag: str, diffs: list[Diff]) -> str:
    """Readable report of one case."""
    verdict = "PASS" if all(d.ok for d in diffs) else "FAIL"
    return "\n".join([f"[{verdict}] case {tag}", *(f"  {d.line()}" for d in diffs)])
