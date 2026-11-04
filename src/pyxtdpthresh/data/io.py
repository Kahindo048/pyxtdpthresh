"""Reading panel data from files."""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message

#: Width of the names stored in the characteristics section, by ``.dta`` release.
_NAME_WIDTH = {117: 33, 118: 129, 119: 129}
#: Index, in the ``<map>`` of a release 117-119 file, of the characteristics and the data sections.
_MAP_CHARACTERISTICS, _MAP_DATA = 8, 9


@dataclass(frozen=True)
class XtsetInfo:
    """What Stata recorded in a ``.dta`` file when ``xtset`` or ``tsset`` was run.

    Attributes
    ----------
    panel, time
        Panel and time variables (``None`` when the file was saved without ``xtset``, or without
        a panel variable after ``tsset``).
    delta
        The time unit (``1`` for consecutive periods).
    """

    panel: str | None = None
    time: str | None = None
    delta: float | None = None


def _stata_delta(text: str) -> float | None:
    """Read ``_dta[_TSdelta]``, which Stata stores in its hexadecimal format (``%21x``)."""
    match = re.fullmatch(r"([+-]?)(\d)\.([0-9a-fA-F]*)X([+-])([0-9a-fA-F]+)", text.strip())
    if match is None:
        return None
    sign, lead, fraction, exp_sign, exponent = match.groups()
    mantissa = float.fromhex(f"0x{lead}.{fraction or '0'}")
    value = mantissa * 2.0 ** (int(exponent, 16) * (-1 if exp_sign == "-" else 1))
    return -value if sign == "-" else value


def _characteristics(raw: bytes, release: int, order: str) -> dict[tuple[str, str], str]:
    """Return the characteristics ``(variable, name) -> text`` of the section ``raw``."""
    width = _NAME_WIDTH[release]
    found: dict[tuple[str, str], str] = {}
    position = raw.find(b"<ch>")
    while position >= 0:
        (size,) = struct.unpack(f"{order}I", raw[position + 4 : position + 8])
        body = raw[position + 8 : position + 8 + size]
        names = (body[:width], body[width : 2 * width], body[2 * width :])
        variable, name, text = (part.split(b"\0")[0].decode("latin-1") for part in names)
        found[(variable, name)] = text
        position = raw.find(b"<ch>", position + 8 + size)
    return found


def stata_xtset(path: str | Path) -> XtsetInfo:
    """Read the ``xtset`` panel and time variables recorded in a ``.dta`` file.

    Stata keeps them as characteristics of the dataset (``_dta[_TSpanel]``, ``_dta[_TStvar]``,
    ``_dta[_TSdelta]``) when the file is saved after ``xtset``.  Releases 117 to 119 (Stata 13 and
    later) are read; any other file, or a file that cannot be parsed, gives an empty result.
    """
    try:
        with Path(path).open("rb") as handle:
            head = handle.read(4096)
            release_tag = re.search(rb"<release>(\d+)</release>", head)
            order_tag = re.search(rb"<byteorder>(MSF|LSF)</byteorder>", head)
            map_at = head.find(b"<map>")
            if release_tag is None or order_tag is None or map_at < 0:
                return XtsetInfo()
            release = int(release_tag.group(1))
            if release not in _NAME_WIDTH:
                return XtsetInfo()
            order = "<" if order_tag.group(1) == b"LSF" else ">"
            offsets = struct.unpack(f"{order}14Q", head[map_at + 5 : map_at + 5 + 14 * 8])
            start, stop = offsets[_MAP_CHARACTERISTICS], offsets[_MAP_DATA]
            handle.seek(start)
            section = handle.read(stop - start)
        facts = _characteristics(section, release, order)
    except (OSError, struct.error, ValueError, UnicodeDecodeError):
        return XtsetInfo()
    delta = facts.get(("_dta", "_TSdelta"))
    return XtsetInfo(
        panel=facts.get(("_dta", "_TSpanel")) or None,
        time=facts.get(("_dta", "_TStvar")) or None,
        delta=_stata_delta(delta) if delta else None,
    )


def read_table(path: str | Path) -> pd.DataFrame:
    """Read a ``.dta``, ``.csv`` or ``.parquet`` file into a DataFrame.

    Stata value labels are not applied (``convert_categoricals=False``), so labelled
    variables stay numeric as they are inside Stata.
    """
    file = Path(path)
    suffix = file.suffix.lower()
    if suffix == ".dta":
        return pd.read_stata(file, convert_categoricals=False)
    if suffix == ".csv":
        return pd.read_csv(file)
    if suffix == ".parquet":
        return pd.read_parquet(file)
    raise DataError(message("unsupported_file", suffix=suffix or "(none)"))


def from_stata(path: str | Path, *, set_index: bool = True) -> pd.DataFrame:
    """Read a Stata ``.dta`` file and use its ``xtset`` panel and time variables.

    When the file was saved after ``xtset`` (or ``xtset ..., delta()``), the panel and time
    variables Stata recorded become the two levels of the index, ready for the estimators
    (``id`` and ``time`` can then be left out), and ``attrs`` keeps their names and the time unit.
    A file without ``xtset`` is returned as it is: the names are **never guessed** from the
    columns, pass ``id=`` and ``time=`` to the estimator.

    Parameters
    ----------
    path
        The ``.dta`` file.
    set_index
        Move the panel and time variables into the index (default).  With ``False`` they stay
        columns and only ``attrs`` records them.

    Returns
    -------
    pandas.DataFrame
        Stata value labels are not applied.  ``attrs["id"]``, ``attrs["time"]`` and
        ``attrs["delta"]`` are ``None`` when the file carries no ``xtset``.
    """
    frame = pd.read_stata(Path(path), convert_categoricals=False)
    info = stata_xtset(path)
    usable = info.panel in frame.columns and info.time in frame.columns
    frame.attrs.update(
        id=info.panel if usable else None,
        time=info.time if usable else None,
        delta=info.delta if usable else None,
    )
    if set_index and usable:
        frame = frame.set_index([str(info.panel), str(info.time)])
    return frame
