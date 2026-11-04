* Small .dta files saved by Stata 17 with and without xtset, to test the reading of the characteristics.
version 17
set more off
local out "C:/Users/Fred-derick/Desktop/Dynamic threshold/pyxtdpthresh/tests/unit/data"
local src "C:/Users/Fred-derick/Desktop/Dynamic threshold/pyxtdpthresh/validation/data/invest.dta"

use "`src'", clear
keep if firm <= 30
save "`out'/xtset_none.dta", replace

xtset firm year
save "`out'/xtset_firm_year.dta", replace

rename firm company
rename year period
xtset company period
save "`out'/xtset_renamed.dta", replace

use "`src'", clear
keep if firm == 1
tsset year
save "`out'/tsset_only.dta", replace

* delta(2): characteristics beyond the two variable names
use "`src'", clear
keep if firm <= 30 & mod(year, 2) == 1
xtset firm year, delta(2)
save "`out'/xtset_delta2.dta", replace

display "DONE xtset files"
