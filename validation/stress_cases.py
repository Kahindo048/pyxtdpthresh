"""The random scenarios of :mod:`validation.stress`, run in Stata 17 and compared object by object.

    python -m validation.stress_cases            # write validation/stata/stress_cases.do and the panels
    python -m validation.stress_cases --freeze   # freeze the Stata results after the run
    python -m validation.stress_cases --report   # compare and print the verdict per scenario

Stata reads the CSV with ``asdouble``: by default ``import delimited`` stores the numbers as 32-bit
``float``, which rounds the data (1e-7) and moves weakly identified estimates by 1e-6.
The panels come from :func:`validation.stress.draw_panel` (seeded NumPy generator), exported to
CSV with every digit, so that Stata and Python read the same numbers.  A scenario Stata refuses
must be refused by the package with the same return code; one Stata estimates must agree on
every object of :mod:`validation.help_examples` (coefficients, standard errors, ``e()``
scalars and matrices, confidence set, tests).
"""

from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path
from typing import Any

import pandas as pd

from validation import help_examples as he
from validation import stress
from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix
from validation.estimation_cases import pack
from validation.search_cases import _MATA_SC
from validation.spec_cases import parse_log, stata_command

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "stress_golden.json"
LOG = STATA_DIR / "_run_stress_cases.log"
COUNT = 120
SEED = 20261104


def args_of(s: stress.Scenario) -> dict[str, Any]:
    """The call of a scenario, with the names of the Stata command."""
    roles = s.roles()
    return {"y": "y", "q": "q", **roles, **s.options}


def example_of(s: stress.Scenario) -> he.Example:
    """The scenario as an example of the help-file machinery."""
    args = args_of(s)
    return he.Example(s.name, s.name, stata_command(args), args)


def frame_of(s: stress.Scenario) -> pd.DataFrame:
    """The panel as Stata reads it: the CSV round trip does not change a double."""
    return stress.draw_panel(s)


def digest(frame: pd.DataFrame) -> str:
    """Fingerprint of a panel, to notice that the generator of NumPy has changed."""
    values = frame.to_numpy(float)
    return hashlib.sha256(values.tobytes()).hexdigest()[:16]


def render_do(scenarios: list[stress.Scenario]) -> str:
    """Do-file: every scenario, with its results exported."""
    scalars = ", ".join(f'pyx_sc("e({n})")' for n in he.SCALARS)
    out = ["version 17", "set more off", "clear all", _MATA_EXPORT, _MATA_SC]
    for s in scenarios:
        tag = f"../out/st_{s.name}"
        ex = example_of(s)
        out += [
            f'import delimited using "../out/stress_{s.name}.csv", clear case(preserve) asdouble',
            "xtset id t",
            f'display "@@CASE {s.name}"',
            f"capture noisily {ex.stata}",
            'display "@@RC " _rc',
            "if _rc == 0 {",
            f'    mata: pyx_export("{tag}_sc.csv", ({scalars}))',
        ]
        out += [
            f'    mata: pyx_export("{tag}_{key}.csv", st_matrix("{name}"))'
            for key, name in he.MATRICES
        ]
        out += ["}", ""]
    out.append("exit, clear")
    return "\n".join(out) + "\n"


def write_do(count: int = COUNT, seed: int = SEED) -> Path:
    """Write the panels and ``validation/stata/stress_cases.do``."""
    scenarios = stress.scenarios(count, seed)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for s in scenarios:
        frame_of(s).to_csv(OUT_DIR / f"stress_{s.name}.csv", index=False)
    path = STATA_DIR / "stress_cases.do"
    path.write_text(render_do(scenarios), encoding="ascii", errors="replace", newline="\n")
    return path


def freeze(count: int = COUNT, seed: int = SEED) -> Path:
    """Freeze the Stata results of the scenarios."""
    parsed = parse_log(LOG.read_text(encoding="utf-8", errors="replace"))
    cases: dict[str, dict[str, Any]] = {}
    for s in stress.scenarios(count, seed):
        entry: dict[str, Any] = {"command": example_of(s).stata, "digest": digest(frame_of(s))}
        entry.update(parsed[s.name])
        if entry["rc"] == 0:
            tag = OUT_DIR / f"st_{s.name}"
            values = read_matrix(Path(f"{tag}_sc.csv")).ravel()
            entry["scalars"] = dict(zip(he.SCALARS, (float(v) for v in values), strict=True))
            for key, _ in he.MATRICES:
                entry[key] = pack(read_matrix(Path(f"{tag}_{key}.csv")))
        cases[s.name] = entry
    meta = {"stata": "Stata 17.0 MP", "xtdpthresh": "0.9.38", "count": count, "seed": seed}
    GOLDEN.write_text(json.dumps({"meta": meta, "cases": cases}), encoding="utf-8", newline="\n")
    return GOLDEN


def frozen() -> dict[str, Any]:
    """The frozen Stata results."""
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def verdict(s: stress.Scenario, ref: dict[str, Any]) -> tuple[str, list[he.Row] | str]:
    """Run the package on the scenario and compare with Stata.

    Returns ``("ok", rows)`` when both estimate, ``("both refuse", detail)`` when both refuse with
    the same return code, and ``("DIFFERENT", detail)`` otherwise.
    """
    from pyxtdpthresh._errors import PyxdpthreshError

    example = example_of(s)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = stress.fit(frame_of(s), s)
    except PyxdpthreshError as error:
        code = getattr(error, "stata_code", None)
        if ref["rc"] == 0:
            return "DIFFERENT", f"Stata estimates, the package refuses ({code}, {error.key})"
        if code != ref["rc"]:
            return "DIFFERENT", f"return code {code} against Stata's {ref['rc']}"
        return "both refuse", f"rc {code} ({error.key})"
    if ref["rc"] != 0:
        return "DIFFERENT", f"Stata refuses (rc {ref['rc']}), the package estimates"
    return "ok", he.compare(example, ref, result.fit)


if __name__ == "__main__":
    import sys

    if "--freeze" in sys.argv:
        print(freeze())
    elif "--report" in sys.argv:
        golden = frozen()
        counts: dict[str, int] = {}
        for s in stress.scenarios(golden["meta"]["count"], golden["meta"]["seed"]):
            kind, detail = verdict(s, golden["cases"][s.name])
            counts[kind] = counts.get(kind, 0) + 1
            if kind == "DIFFERENT":
                print(s.name, detail)
            elif kind == "ok":
                bad = [r for r in detail if not r.ok]
                if bad:
                    counts["DIFFERENT"] = counts.get("DIFFERENT", 0) + 1
                    print(s.name, [(r.name, r.python, r.stata) for r in bad[:4]])
        print(counts)
    else:
        print(write_do())
