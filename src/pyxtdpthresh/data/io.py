"""Reading panel data from files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pyxtdpthresh._errors import DataError
from pyxtdpthresh._i18n import message


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


def from_stata(path: str | Path) -> pd.DataFrame:
    """Read a Stata ``.dta`` file (shortcut of :func:`read_table`)."""
    return pd.read_stata(Path(path), convert_categoricals=False)
