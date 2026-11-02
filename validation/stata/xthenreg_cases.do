version 17
set more off
clear all
capture log close

mata:
void pyx_export(string scalar fname, real matrix M)
{
    real scalar fh, i, j
    string scalar line
    fh = fopen(fname, "w")
    for (i = 1; i <= rows(M); i++) {
        line = strofreal(M[i,1], "%21.15g")
        for (j = 2; j <= cols(M); j++) line = line + "," + strofreal(M[i,j], "%21.15g")
        fput(fh, line)
    }
    fclose(fh)
}
end

program define pyx_save_xthenreg
    args tag
    mata: pyx_export("../out/`tag'_b.csv", st_matrix("e(b)")')
    mata: pyx_export("../out/`tag'_V.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/`tag'_CI.csv", st_matrix("e(CI)"))
    mata: pyx_export("../out/`tag'_scal.csv", (st_numscalar("e(N)") \ st_numscalar("e(T)") \ st_numscalar("e(boots_p)")))
end

use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(50) trim_rate(0.4)
pyx_save_xthenreg c1

use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
xthenreg invest debt, endogenous(cashflow tobin_q debt) grid_num(50) trim_rate(0.4) kink
pyx_save_xthenreg c2

use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
xthenreg invest debt cashflow, endogenous(tobin_q) exogenous(debt) grid_num(40) trim_rate(0.3) static
pyx_save_xthenreg c3

use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
xthenreg invest debt cashflow, endogenous(tobin_q debt) inst(z1 z2) grid_num(50) trim_rate(0.4)
pyx_save_xthenreg c4

use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
xthenreg invest debt cashflow, endogenous(tobin_q) grid_num(40) trim_rate(0.3) static kink
pyx_save_xthenreg c5

use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
xthenreg invest debt cashflow, endogenous(tobin_q) exogenous(debt) grid_num(60) trim_rate(0.2)
pyx_save_xthenreg c6

exit, clear
