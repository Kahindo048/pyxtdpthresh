"""Validation of core.linalg against Stata (block C.2; files ``la_*`` in ``validation/out``).

The Stata side runs Mata's built-in ``invsym`` / ``cholinv`` and the **verbatim** source of
``xdpt2_syminv``, ``xdpt2_psd_ok`` and ``xdpt2_objtol`` taken from ``xtdpthresh.ado`` (not a
re-implementation), on a fixed set of matrices, and exports every result to CSV.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from validation.cases import _MATA_EXPORT, OUT_DIR, STATA_DIR
from validation.compare import read_matrix

GOLDEN = Path(__file__).resolve().parents[1] / "tests" / "golden" / "linalg_golden.json"
#: Looser relative tolerance where the *input* is so ill-conditioned (cond 1e13, error ~ cond*eps
#: ~ 1e-3) that two correct implementations legitimately differ in the fourth digit.
RTOL_OVERRIDE = {"cond13": 1e-3}
ADO = Path.home() / "ado" / "plus" / "x" / "xtdpthresh.ado"
TAG = "la"


def _spd(n: int, seed: int, cond: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.standard_normal((n, n)))
    return (q * np.geomspace(1.0, 1.0 / cond, n)) @ q.T


def _gram(n: int, p: int, seed: int, dup: bool = False) -> np.ndarray:
    x = np.random.default_rng(seed).standard_normal((n, p))
    if dup:
        x = np.column_stack([x, x[:, 0] - 2.0 * x[:, 1]])
    return x.T @ x


def matrices() -> dict[str, np.ndarray]:
    """Named test matrices: regular, badly scaled, ill-conditioned, singular, indefinite."""
    mats = {
        "spd1": np.array([[3.0]]),
        "spd2": np.array([[2.0, 0.5], [0.5, 1.0]]),
        "spd4": _spd(4, 1, 10.0),
        "spd7": _spd(7, 2, 1e3),
        "spd12": _spd(12, 3, 50.0),
        "cond6": _spd(5, 4, 1e6),
        "cond8": _spd(5, 5, 1e8),
        "cond10": _spd(5, 6, 1e10),
        "cond11": _spd(5, 7, 1e11),
        "cond13": _spd(5, 8, 1e13),
        "tiny": _spd(4, 9, 3.0) * 1e-20,
        "huge": _spd(4, 10, 3.0) * 1e12,
        "mixed": np.diag([1e-8, 1.0, 1e6]) @ _spd(3, 11, 20.0) @ np.diag([1e-8, 1.0, 1e6]),
        "gram": _gram(40, 5, 12),
        "gram_sing": _gram(40, 3, 13, dup=True),
        "diag_wide": np.diag([1.0, 1e-17]),
        "diag_zero": np.diag([1.0, 0.0, 2.0]),
        "indef": np.array([[1.0, 2.0], [2.0, 1.0]]),
        "indef3": np.array([[2.0, 1.0, 0.0], [1.0, -1.0, 0.5], [0.0, 0.5, 3.0]]),
        "negdef": np.array([[-2.0, 1.0], [1.0, -2.0]]),
        "ones": np.ones((2, 2)),
        "nan": np.array([[1.0, np.nan], [np.nan, 1.0]]),
        "asym": np.array([[1.0, 0.5, 0.0], [0.4, 2.0, 0.1], [0.0, 0.1, 3.0]]),
    }
    return mats


OBJTOL_ARGS = np.array(
    [[2.0, -5.0, 1e-12], [0.0, 0.0, 1e-12], [2e-9, 5e-9, 1e-12], [-3.0, 0.0, 1e-10]]
)


def _mata_literal(a: np.ndarray) -> str:
    rows = [",".join("." if np.isnan(v) else f"{v:.17g}" for v in r) for r in a]
    return "(" + " \\ ".join(rows) + ")"


def _extract_stata_functions() -> str:
    """Verbatim Mata source of ``xdpt2_objtol``, ``xdpt2_syminv`` and ``xdpt2_psd_ok``."""
    lines = ADO.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("real scalar xdpt2_objtol"))
    end = next(i for i, ln in enumerate(lines) if ln.startswith("// Per-unit data structure"))
    return "\n".join(lines[start:end])


_MATA_RUN = """\
mata:
void run_case(string scalar tag, real matrix A)
{
    real scalar ok
    real matrix Ainv
    pyx_export("../out/" + tag + "_invsym.csv", invsym(A))
    pyx_export("../out/" + tag + "_cholinv.csv", cholinv(A))
    xdpt2_syminv(A, ok, Ainv)
    pyx_export("../out/" + tag + "_syminv_ok.csv", ok)
    pyx_export("../out/" + tag + "_syminv.csv", Ainv)
    pyx_export("../out/" + tag + "_psd.csv", xdpt2_psd_ok(A))
}
end
"""


def render_do(mats: dict[str, np.ndarray] | None = None) -> str:
    """Do-file that evaluates every matrix with Stata and exports the results."""
    mats = matrices() if mats is None else mats
    body = ["version 17", "set more off", "clear all", "", _MATA_EXPORT]
    body += ["mata:", _extract_stata_functions(), "end", "", _MATA_RUN]
    body.append("mata:")
    for name, a in mats.items():
        body.append(f'run_case("{TAG}_{name}", {_mata_literal(a)})')
    for k, (x, y, r) in enumerate(OBJTOL_ARGS):
        body.append(
            f'pyx_export("../out/{TAG}_objtol{k}.csv", xdpt2_objtol({x:.17g}, {y:.17g}, {r:.17g}))'
        )
    body += ["end", "exit, clear"]
    return "\n".join(body) + "\n"


def write_do(path: Path | None = None) -> Path:
    """Write ``validation/stata/linalg_cases.do``."""
    path = path or STATA_DIR / "linalg_cases.do"
    path.write_text(render_do(), encoding="ascii", newline="\n")
    return path


def python_results(name: str, a: np.ndarray) -> dict[str, np.ndarray]:
    """Same objects as the Stata export, computed with :mod:`pyxtdpthresh.core.linalg`."""
    from pyxtdpthresh.core import linalg

    res = linalg.syminv(a)
    return {
        "invsym": linalg.invsym(a),
        "cholinv": linalg.cholinv(a),
        "syminv_ok": np.array([[float(res.ok)]]),
        "syminv": res.inv,
        "psd": np.array([[float(linalg.psd_ok(a))]]),
    }


def stata_results(out_dir: Path = OUT_DIR) -> dict[str, dict[str, np.ndarray]]:
    """Exports of the Stata run, grouped by matrix name."""
    found: dict[str, dict[str, np.ndarray]] = {}
    for name in matrices():
        found[name] = {
            kind: read_matrix(out_dir / f"{TAG}_{name}_{kind}.csv")
            for kind in ("invsym", "cholinv", "syminv_ok", "syminv", "psd")
        }
    return found


def freeze(out_dir: Path = OUT_DIR, path: Path = GOLDEN) -> Path:
    """Freeze inputs and Stata results into ``tests/golden/linalg_golden.json``."""
    results = stata_results(out_dir)
    objtol = [
        float(read_matrix(out_dir / f"{TAG}_objtol{k}.csv")[0, 0]) for k in range(len(OBJTOL_ARGS))
    ]
    master = {
        "meta": {"stata": "Stata 17.0 MP", "source": "validation/linalg_cases.py"},
        "matrices": {n: a.tolist() for n, a in matrices().items()},
        "stata": {n: {k: v.tolist() for k, v in objs.items()} for n, objs in results.items()},
        "objtol_args": OBJTOL_ARGS.tolist(),
        "objtol": objtol,
        "rtol_override": RTOL_OVERRIDE,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(master, indent=1), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    import sys

    print(freeze() if "--freeze" in sys.argv else write_do())
