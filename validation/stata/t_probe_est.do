version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
xtdpthresh invest cashflow, qx(debt) endogenous(tobin_q) noboot grid(10) exportgmm
ereturn list
matrix list e(b)
capture matrix list e(V)
capture matrix list e(V_cond)
mata: printf("Zf %g x %g ; Xf %g x %g ; A %g x %g\n", rows(xdpt_best_Z_f), cols(xdpt_best_Z_f), rows(xdpt_best_X_f), cols(xdpt_best_X_f), rows(xdpt_best_A), cols(xdpt_best_A))
exit, clear
