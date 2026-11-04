"""Investment and leverage: the model of Seo and Shin (2016, section 7) on Hansen's (1999) panel.

Investment on its lag, cash flow, Tobin's q and leverage, all slopes changing at a leverage
threshold, with cash flow, Tobin's q and leverage endogenous. This is the main example of the help
file of ``xtdpthresh``; the package reproduces it to four decimals (tests/golden).

Run:  python examples/01_hansen_investment.py [output_directory]
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pyxtdpthresh as pyx  # noqa: E402

#: Five firms with extreme values, excluded by Seo and Shin (2016).
EXTREME_FIRMS = [137, 391, 407, 488, 538]
MODEL = {
    "q": "debt",
    "endogenous": ["cashflow", "tobin_q", "debt"],
    "maxlag": (3, 8),
    "collapse": True,
    "id": "firm",
    "time": "year",
    "seed": 12345,
}


def main(out: Path) -> None:
    """Estimate the model, compare variants, and write tables, figures and reports to ``out``."""
    out.mkdir(parents=True, exist_ok=True)
    df = pyx.load_dataset("invest")
    df = df[~df["firm"].isin(EXTREME_FIRMS)]

    # 1. Point estimates, inference and tests, in one call.
    fd = pyx.xtdpthresh(df, "invest", **MODEL)
    print(fd)
    print(f"\nThreshold {fd.gamma:.4f}, interval {fd.gamma_ci}, seed {fd.seed}\n")

    # 2. Variants: forward orthogonal deviations, and a kink instead of a jump.
    fod = pyx.xtdpthresh(df, "invest", method="fod", **MODEL)
    kink = pyx.xtdpthresh(df, "invest", kink=True, **MODEL)

    # 3. A publication table with the three side by side (also .html, .md, .docx, .xlsx).
    table = pyx.compare([fd, fod, kink], model_names=["FD jump", "FOD jump", "FD kink"])
    table.to_latex(out / "table.tex")
    table.to_markdown(out / "table.md")
    print(table.to_text())

    # 4. What deserves attention, and what the estimation really used.
    (out / "diagnosis.txt").write_text(str(fd.diagnose()), encoding="utf-8")
    (out / "settings.txt").write_text(str(fd.settings_log()), encoding="utf-8")
    print(fd.diagnose())

    # 5. Figures (English or French with lang="fr").
    for kind in ("profile", "ci", "regimes", "coef"):
        fd.plot(kind, path=out / f"{kind}.png")

    # 6. Residuals and regime of every observation, as columns of the data.
    augmented = fd.augment(df, kinds=("residuals", "regime"))
    share = augmented["regime"].mean()
    print(f"\nShare of firm-years above the threshold: {share:.1%}")
    fd.to_json(out / "fit.json")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output_hansen"))
