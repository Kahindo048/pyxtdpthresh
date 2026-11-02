"""Exceptions and warnings of the package (layer 0).

Errors that Stata reports with a return code keep it in :attr:`PyxdpthreshError.stata_code`
(198 for invalid syntax or options, 498 for regressors removed by the transformation,
459 for data changed since the fit), so that users migrating from Stata recognise them.
"""

from __future__ import annotations


class PyxdpthreshError(Exception):
    """Base class of every error raised by pyxtdpthresh."""

    stata_code: int | None = None

    def __init__(self, message: str, *, stata_code: int | None = None) -> None:
        super().__init__(message)
        if stata_code is not None:
            self.stata_code = stata_code


class DataError(PyxdpthreshError, ValueError):
    """The data do not satisfy a requirement (balance, duplicates, missing values...)."""


class SpecificationError(PyxdpthreshError, ValueError):
    """The model specification or an option is invalid or inconsistent."""

    stata_code = 198


class NumericalError(PyxdpthreshError, ArithmeticError):
    """A numerical step failed (singular matrix, empty regime, no admissible threshold)."""


class PyxdpthreshWarning(UserWarning):
    """Non-fatal condition worth reporting (fallback used, boundary threshold...)."""
