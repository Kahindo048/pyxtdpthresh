version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
timer clear 1
timer on 1
quietly xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse rseed(1)
timer off 1
timer clear 2
timer on 2
quietly xtdpthresh invest, qx(debt) endogenous(cashflow tobin_q debt) maxlag(3 8) collapse noboot
timer off 2
quietly timer list
display "@@T boot " r(t1)
display "@@T noboot " r(t2)
exit, clear
