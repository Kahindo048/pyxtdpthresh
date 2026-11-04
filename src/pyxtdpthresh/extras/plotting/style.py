"""Common chart style of the package (matplotlib is imported when a figure is made).

The look follows the figures of the author's papers: Latin Modern Roman text to match a LaTeX
document (Computer Modern maths), thin marks with white edges, direct labels instead of legends
where possible, a single scale per axis, light grid, no top or right spine, and a categorical
palette whose first two slots (blue, orange) carry the contrast of a figure and whose remaining
slots are an aqua and greys.  Figures are 6.27 in wide, the text width of an A4 page with
1 in margins, so they are inserted at scale 1 and share the font size of the text.
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyxtdpthresh._config import get_options
from pyxtdpthresh._errors import SpecificationError
from pyxtdpthresh._i18n import message
from pyxtdpthresh._types import Lang

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

#: Categorical slots: 1 blue, 2 orange, 3 aqua, then neutrals; ink and muted text; grid.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GREY, INK, MUTED, GRID = "#8a8985", "#0b0b0b", "#52514e", "#e3e2de"
#: Width of the text of an A4 page with 1 in margins (inches).
TEXT_WIDTH = 6.27
#: Formats ``save_figure`` writes, by extension.
FORMATS = (".png", ".pdf", ".svg")

_LATIN_MODERN = ("lmroman10-regular", "lmroman10-bold", "lmroman10-italic", "lmroman10-bolditalic")
_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")


@lru_cache(maxsize=1)
def latin_modern() -> bool:
    """Register Latin Modern Roman with matplotlib when TeX Live provides it; say whether found."""
    # kpsewhich ships with TeX Live and MiKTeX; without it the sans-serif default is used
    from matplotlib import font_manager

    finder = shutil.which("kpsewhich")
    found = False
    for name in _LATIN_MODERN if finder else ():
        try:
            run = subprocess.run(  # noqa: S603
                [str(finder), name + ".otf"], capture_output=True, text=True, check=True, timeout=10
            )
        except (OSError, subprocess.SubprocessError):
            continue
        path = run.stdout.strip()
        if path:
            font_manager.fontManager.addfont(path)
            found = True
    if not found:
        logger.debug("Latin Modern Roman not found (kpsewhich); using the default font")
    return found


def rc_params(*, font: bool = True) -> dict[Any, Any]:
    """Style parameters of the charts (a mapping for ``matplotlib.rc_context``)."""
    serif = font and latin_modern()
    return {
        "font.family": "Latin Modern Roman" if serif else "DejaVu Sans",
        "mathtext.fontset": "cm" if serif else "dejavusans",
        "font.size": 9,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "axes.titlesize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.unicode_minus": False,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": INK,
        "legend.frameon": False,
        "figure.dpi": 150,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }


@contextmanager
def chart_style(*, font: bool = True) -> Iterator[None]:
    """Apply the chart style inside a ``with`` block, leaving matplotlib's settings untouched."""
    import matplotlib

    with matplotlib.rc_context(rc_params(font=font)):
        yield


def resolve_lang(lang: Lang | None) -> Lang:
    """Language of the figure texts: the argument, else the global ``lang`` option."""
    chosen = lang if lang is not None else get_options().lang
    if chosen not in ("en", "fr"):
        raise ValueError("lang must be 'en' or 'fr'")
    return chosen


def new_figure(
    *, height: float = 3.2, shape: tuple[int, int] = (1, 1), **kwargs: Any
) -> tuple[Figure, Any]:
    """Create a figure at the text width and its axes (an array when ``shape`` is not 1 x 1)."""
    from matplotlib.figure import Figure

    fig = Figure(figsize=(TEXT_WIDTH, height), layout="constrained")
    axes = fig.subplots(*shape, **kwargs)
    return fig, axes


def decimal_comma(fig: Figure) -> None:
    """French version: decimal comma in the tick labels and in the texts of the figure."""
    from matplotlib.ticker import ScalarFormatter

    class _Comma(ScalarFormatter):
        def __call__(self, x: float, pos: int | None = None) -> str:
            return super().__call__(x, pos).replace(".", ",")

    for ax in fig.axes:
        for text in ax.texts:
            text.set_text(_DECIMAL.sub(",", text.get_text()))
        for axis in (ax.xaxis, ax.yaxis):
            if isinstance(axis.get_major_formatter(), ScalarFormatter):
                axis.set_major_formatter(_Comma())


def finish(fig: Figure, lang: Lang) -> Figure:
    """Last touches of a figure: decimal comma in French."""
    if lang == "fr":
        decimal_comma(fig)
    return fig


def direct_label(ax: Axes, x: float, y: float, text: str, *, color: str = MUTED, **kw: Any) -> Any:
    """Small text placed at data coordinates (the labels that replace a legend)."""
    options: dict[str, Any] = {"fontsize": 7.5, "color": color, "ha": "left", "va": "bottom"}
    options.update(kw)
    return ax.text(x, y, text, **options)


def save_figure(
    fig: Figure, path: str | Path, *, dpi: int = 200, formats: tuple[str, ...] | None = None
) -> list[Path]:
    """Write ``fig`` as PNG, PDF or SVG according to the extension of ``path``.

    With ``formats`` (for example ``(".png", ".pdf")``) the extension of ``path`` is replaced by
    each of them, which writes one file per format.  Returns the files written.
    """
    target = Path(path)
    suffixes = formats if formats is not None else (target.suffix.lower(),)
    written: list[Path] = []
    with chart_style():
        for suffix in suffixes:
            if suffix not in FORMATS:
                raise SpecificationError(
                    message("plot_format", suffix=suffix), stata_code=198, key="plot_format"
                )
            out = target.with_suffix(suffix)
            fig.savefig(out, dpi=dpi)
            written.append(out)
    return written
