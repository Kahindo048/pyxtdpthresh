version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
local base "invest cashflow, qx(debt) noboot grid(10)"
local i 0
foreach opt in "grid(5.5)" "grid(abc)" "maxlag(0)" "maxlag(1 2 3)" "maxlag(1.5)" "maxlag(3 2)" "level(5)" "level(100)" "citest(1 2)" "minregime(1.5)" "refine(2.5)" "trim(abc)" "bwscale(abc)" "grid(9)" "vce(Robust)" "method(FOD)" "bogus" "rseed(1.5)" {
    local ++i
    display "@@CASE p`i' `opt'"
    capture noisily xtdpthresh `base' `opt'
    display "@@RC " _rc
}
foreach t in "l1.invest" "L2.invest" "ld.invest" "L0.invest" "f.invest" "S12.invest" "l.invest" "L(1/2).cashflow" "l2.cashflow" "L1D.cashflow" "d2.cashflow" "L0.debt" {
    local ++i
    display "@@CASE p`i' indep `t'"
    capture noisily xtdpthresh invest `t', qx(debt) noboot grid(10)
    display "@@RC " _rc
}
exit, clear
