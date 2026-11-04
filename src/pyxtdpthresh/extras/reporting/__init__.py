"""Tables, summaries and exports of a fit (layer 6): read the results, never estimate.

``ThresholdStargazer`` and ``compare`` put models side by side; ``summary`` prints one fit;
``to_dataframe``, ``ci_table`` and ``regime_table`` return data frames; ``to_json`` records a fit
so that it can be reproduced; ``diagnose`` writes the alerts of a fit in plain language;
``settings_log`` lists the settings the estimation really used (sample, instruments kept and
removed, grid, seed).  The Word and Excel renderers import ``python-docx`` and ``openpyxl`` only
when used.
"""

from pyxtdpthresh.extras.reporting.diagnose import Alert, Diagnosis, diagnose
from pyxtdpthresh.extras.reporting.frames import ci_table, regime_table, to_dataframe, to_json
from pyxtdpthresh.extras.reporting.settings_log import SettingsLog, settings_log
from pyxtdpthresh.extras.reporting.stargazer import ThresholdStargazer, compare
from pyxtdpthresh.extras.reporting.summary import summary

__all__ = [
    "Alert",
    "Diagnosis",
    "SettingsLog",
    "ThresholdStargazer",
    "ci_table",
    "compare",
    "diagnose",
    "regime_table",
    "settings_log",
    "summary",
    "to_dataframe",
    "to_json",
]
