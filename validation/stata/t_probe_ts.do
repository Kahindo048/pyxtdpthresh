version 17
set more off
clear all

capture program drop pyx_canon
program define pyx_canon
    syntax varlist(min=1 ts)
    display "@@CANON `varlist'"
end

use "../data/invest.dta", clear
xtset firm year
foreach t in "l.cashflow" "l1.cashflow" "L2.cashflow" "ll.cashflow" "l2l.cashflow" "ld.cashflow" "l1d.cashflow" "d1.cashflow" "d.cashflow" "d2.cashflow" "f.cashflow" "f1.cashflow" "f2.cashflow" "s.cashflow" "s1.cashflow" "s12.cashflow" "L0.cashflow" "d0.cashflow" "l(1).cashflow" "l(2).cashflow" "l(0/2).cashflow" "l(1/2).cashflow" "l(1 3).cashflow" "ld2.cashflow" "L2D.cashflow" "dl.cashflow" "lf.cashflow" "fl.cashflow" "l0f.cashflow" "ls.cashflow" "ll2.cashflow" "L3L.cashflow" "d(1/2).cashflow" "LLL.cashflow" "FF.cashflow" "dd.cashflow" "ss.cashflow" "L(1/2)D.cashflow" "l01.cashflow" "L10.cashflow" "cashflow" "L.debt L2.tobin_q" {
    display "@@IN `t'"
    capture noisily pyx_canon `t'
    display "@@RC " _rc
}

* values of operated terms on a panel with calendar gaps
use "../data/invest.dta", clear
xtset firm year
keep if firm <= 30
drop if mod(firm + 3*year, 7) == 0
sort firm year
local terms "L.cashflow L2.cashflow F.cashflow F2.cashflow D.cashflow D2.cashflow LD.cashflow DL.cashflow L2D.cashflow S2.cashflow S3.cashflow LS2.cashflow FD.cashflow DF.cashflow L3.cashflow L.D2.cashflow"
local i 0
foreach t of local terms {
    local ++i
    quietly gen double pyxv`i' = `t'
}
preserve
keep firm year cashflow pyxv*
export delimited using "../out/ts_values.csv", replace
restore
file open fh using "../out/ts_terms.txt", write replace text
file write fh "`terms'" _n
file close fh
exit, clear
