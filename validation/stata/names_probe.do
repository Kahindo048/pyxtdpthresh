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
quietly xtdpthresh invest cashflow, qx(debt) noboot grid(30) endogenous(tobin_q)
local cn : colfullnames e(b)
foreach w of local cn {
    display "@@N `w'"
}
capture confirm matrix e(b_upper)
if !_rc {
    local un : colfullnames e(b_upper)
    foreach w of local un {
        display "@@U `w'"
    }
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
display "@@CASE fd_kink_q_regressor"
quietly xtdpthresh invest cashflow debt, qx(debt) kink noboot grid(30) endogenous(tobin_q)
local cn : colfullnames e(b)
foreach w of local cn {
    display "@@N `w'"
}
capture confirm matrix e(b_upper)
if !_rc {
    local un : colfullnames e(b_upper)
    foreach w of local un {
        display "@@U `w'"
    }
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
display "@@CASE fd_jump_q_regressor"
quietly xtdpthresh invest cashflow debt, qx(debt) noboot grid(30) endogenous(tobin_q)
local cn : colfullnames e(b)
foreach w of local cn {
    display "@@N `w'"
}
capture confirm matrix e(b_upper)
if !_rc {
    local un : colfullnames e(b_upper)
    foreach w of local un {
        display "@@U `w'"
    }
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
display "@@CASE fd_predet"
quietly xtdpthresh invest cashflow, qx(debt) noboot grid(30) predetermined(tobin_q)
local cn : colfullnames e(b)
foreach w of local cn {
    display "@@N `w'"
}
capture confirm matrix e(b_upper)
if !_rc {
    local un : colfullnames e(b_upper)
    foreach w of local un {
        display "@@U `w'"
    }
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
display "@@CASE fd_static"
quietly xtdpthresh invest cashflow L.tobin_q, qx(debt) static noboot grid(30)
local cn : colfullnames e(b)
foreach w of local cn {
    display "@@N `w'"
}
capture confirm matrix e(b_upper)
if !_rc {
    local un : colfullnames e(b_upper)
    foreach w of local un {
        display "@@U `w'"
    }
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
quietly xtdpthresh invest cashflow, qx(debt) kink noboot method(fod) grid(30) endogenous(tobin_q)
local cn : colfullnames e(b)
foreach w of local cn {
    display "@@N `w'"
}
capture confirm matrix e(b_upper)
if !_rc {
    local un : colfullnames e(b_upper)
    foreach w of local un {
        display "@@U `w'"
    }
}
exit, clear
