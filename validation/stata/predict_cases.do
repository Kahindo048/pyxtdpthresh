version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_jump"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fd_jump.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fd_kink.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fd_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fd_td.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE fd_short_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fd_short_wind.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fod_jump"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fod_jump.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fod_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fod_kink.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
display "@@CASE fod_td"
capture noisily xtdpthresh invest cashflow, qx(debt) td noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fod_td.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if mod(firm + 3*year, 11) == 0
display "@@CASE fod_gaps_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fod_gaps_wind.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE fod_short"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fod_short.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
keep if firm <= 100 & year <= 1981
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
gen double macro = ln(year - 1960)
gen double ysum = L2.invest + L3.invest
gen double ageish = firm + year
gen double qdisc = floor(debt/0.25 + 0.5)*0.25
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE fod_alternate_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_fod_alternate_wind.csv", replace
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_fod"
capture noisily xtdpthresh invest , qx(debt) collapse noboot method(fod) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    predict double p_residuals, residuals
    predict double p_xb, xb
    predict double p_ar_residuals, arresiduals
    predict double p_regime, regime
    predict double p_if, residuals
    replace p_if = . if !(year >= 1977)
    export delimited firm year p_residuals p_xb p_ar_residuals p_regime p_if using "../out/pr_full_help_fod.csv", replace
}

exit, clear
