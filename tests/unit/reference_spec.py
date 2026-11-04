"""A hand-built table whose renderings are frozen in ``reference_tables/`` (block I.7.3)."""

from pyxtdpthresh.extras.reporting.table_spec import Cell, CoefRow, StatRow, TableSpec

SPEC = TableSpec(
    dep_var_label="Dependent variable",
    dep_vars=("y", "y"),
    columns=("(1)", "(2)"),
    rows=(
        CoefRow("L.y", (Cell("0.306", 3, "(0.091)"), Cell("0.341", 0, "(0.311)")), "Lower regime"),
        CoefRow("_cons", (Cell("-0.967", 1, "(1.323)"), Cell()), "Change at the threshold"),
    ),
    stats=(StatRow("Observations", ("2000", "2000")), StatRow("Threshold γ̂", ("0.499", "-"))),
    notes=("*p<0.1; **p<0.05; ***p<0.01", "Standard errors in parentheses."),
    title="Results & 50%",
    label="tab:main",
    font_size="footnotesize",
)
