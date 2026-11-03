"""Progress indicator of the long bootstraps (no dependency; silent unless the option is set).

``set_options(progress=True)`` (or ``option_context(progress=True)``) prints, on the standard error
stream, one line per bootstrap component that is updated in place: step, share done and the
estimated remaining time.
"""

from __future__ import annotations

import sys
import time
from types import TracebackType

from pyxtdpthresh._config import get_options


class Progress:
    """Context manager that reports ``done / total`` steps of a named bootstrap component.

    Parameters
    ----------
    label
        Name shown in front of the counter.
    total
        Number of steps.
    """

    def __init__(self, label: str, total: int) -> None:
        self.label, self.total = label, max(int(total), 1)
        self.active = bool(get_options().progress)
        self.done = 0
        self._start = time.perf_counter()

    def __enter__(self) -> Progress:
        self._start = time.perf_counter()
        return self

    def step(self, count: int = 1) -> None:
        """Record ``count`` finished steps and refresh the line."""
        self.done += count
        if not self.active:
            return
        elapsed = time.perf_counter() - self._start
        remaining = elapsed / self.done * (self.total - self.done) if self.done else 0.0
        share = 100.0 * self.done / self.total
        line = f"{self.label}: {self.done}/{self.total} ({share:3.0f} %)"
        sys.stderr.write(f"\r{line}, about {remaining:.0f} s left")
        sys.stderr.flush()

    def __exit__(
        self,
        kind: type[BaseException] | None,
        value: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        if self.active:
            sys.stderr.write(f"\r{self.label}: {self.done}/{self.total} done" + " " * 24 + "\n")
            sys.stderr.flush()
