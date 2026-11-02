version 17
set more off
clear all
mata:
void pyx_export(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
    if (fileexists(fname)) unlink(fname)
    fh = fopen(fname, "w")
    for (i = 1; i <= rows(M); i++) {
        line = strofreal(M[i,1], "%21.15g")
        for (j = 2; j <= cols(M); j++) line = line + "," + strofreal(M[i,j], "%21.15g")
        fput(fh, line)
    }
    fclose(fh)
}
end

matrix pyxbench = J(1, 3, .)
forvalues r = 1/5 {
    use "../data/invest.dta", clear
    xtset firm year
    keep if year <= 1980
    set seed 2024
    timer clear 1
    timer on 1
    quietly xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(100) trim_rate(0.4)
    timer off 1
    quietly timer list 1
    local sec = r(t1)
    matrix pyxbench = (pyxbench \ (1, `r', `sec'))
}
forvalues r = 1/3 {
    use "../data/invest.dta", clear
    xtset firm year
    keep if year <= 1980
    set seed 2024
    timer clear 1
    timer on 1
    quietly xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(100) trim_rate(0.4) boost(399)
    timer off 1
    quietly timer list 1
    local sec = r(t1)
    matrix pyxbench = (pyxbench \ (2, `r', `sec'))
}
forvalues r = 1/5 {
    use "../data/invest.dta", clear
    xtset firm year
    * all years
    set seed 2024
    timer clear 1
    timer on 1
    quietly xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(100) trim_rate(0.4)
    timer off 1
    quietly timer list 1
    local sec = r(t1)
    matrix pyxbench = (pyxbench \ (3, `r', `sec'))
}
forvalues r = 1/3 {
    use "../data/invest.dta", clear
    xtset firm year
    * all years
    set seed 2024
    timer clear 1
    timer on 1
    quietly xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(100) trim_rate(0.4) boost(399)
    timer off 1
    quietly timer list 1
    local sec = r(t1)
    matrix pyxbench = (pyxbench \ (4, `r', `sec'))
}
mata: pyx_export("../out/bench_stata.csv", st_matrix("pyxbench")[2..rows(st_matrix("pyxbench")), .])
exit, clear
