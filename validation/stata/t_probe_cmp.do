version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
keep if year <= 1980
xthenreg invest debt cashflow, endogenous(tobin_q) exogenous(debt) grid_num(60) trim_rate(0.2)
display "XTHENREG gamma " e(gamma)
ereturn list
xtdpthresh invest cashflow, qx(debt) endogenous(tobin_q) exogenous(debt) grid(60) trim(0.2) noboot
display "XTDPTHRESH gamma " e(gamma) " niv " e(N_iv)
exit, clear
