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

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d0_dyn"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d0_dyn.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d0_dyn_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d0_dynw"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d0_dynw.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d0_dynw_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d0_dyns"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d0_dyns.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d0_dyns_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d0_ops"
capture noisily xtdpthresh invest cashflow L.tobin_q if year >= 1976, qx(debt) static noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d0_ops.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d0_ops_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if mod(firm + 3*year, 11) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d1_dyn"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d1_dyn.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d1_dyn_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if mod(firm + 3*year, 11) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d1_dynw"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d1_dynw.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d1_dynw_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if mod(firm + 3*year, 11) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d1_dyns"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d1_dyns.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d1_dyns_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if mod(firm + 3*year, 11) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d1_ops"
capture noisily xtdpthresh invest cashflow L.tobin_q if year >= 1976, qx(debt) static noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d1_ops.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d1_ops_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace cashflow = . if mod(firm*year, 13) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d2_dyn"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d2_dyn.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d2_dyn_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace cashflow = . if mod(firm*year, 13) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d2_dynw"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d2_dynw.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d2_dynw_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace cashflow = . if mod(firm*year, 13) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d2_dyns"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d2_dyns.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d2_dyns_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace cashflow = . if mod(firm*year, 13) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d2_ops"
capture noisily xtdpthresh invest cashflow L.tobin_q if year >= 1976, qx(debt) static noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d2_ops.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d2_ops_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d3_dyn"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d3_dyn.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d3_dyn_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d3_dynw"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d3_dynw.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d3_dynw_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d3_dyns"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d3_dyns.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d3_dyns_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d3_ops"
capture noisily xtdpthresh invest cashflow L.tobin_q if year >= 1976, qx(debt) static noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d3_ops.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d3_ops_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d4_dyn"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d4_dyn.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d4_dyn_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d4_dynw"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d4_dynw.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d4_dynw_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d4_dyns"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d4_dyns.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d4_dyns_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d4_ops"
capture noisily xtdpthresh invest cashflow L.tobin_q if year >= 1976, qx(debt) static noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d4_ops.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d4_ops_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace tobin_q = . if firm <= 50 & year == 1975
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d5_dyn"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d5_dyn.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d5_dyn_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace tobin_q = . if firm <= 50 & year == 1975
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d5_dynw"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d5_dynw.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d5_dynw_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace tobin_q = . if firm <= 50 & year == 1975
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d5_dyns"
capture noisily xtdpthresh invest cashflow if year >= 1976, qx(debt) noboot grid(10) history(sample) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d5_dyns.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d5_dyns_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
replace tobin_q = . if firm <= 50 & year == 1975
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE d5_ops"
capture noisily xtdpthresh invest cashflow L.tobin_q if year >= 1976, qx(debt) static noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_d5_ops.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_d5_ops_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_const_unit"
capture noisily xtdpthresh invest cu, qx(debt) noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_const_unit.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_const_unit_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_const_time"
capture noisily xtdpthresh invest ct, qx(debt) td noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_const_time.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_const_time_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_q_const_unit"
capture noisily xtdpthresh invest cashflow, qx(cu) noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_q_const_unit.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_q_const_unit_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_q_const_time"
capture noisily xtdpthresh invest cashflow, qx(ct) td noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_q_const_time.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_q_const_time_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_few_units"
capture noisily xtdpthresh invest cashflow if firm <= 4, qx(debt) noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_few_units.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_few_units_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_q_missing"
capture noisily xtdpthresh invest cashflow, qx(qm) noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_q_missing.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_q_missing_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_x_missing"
capture noisily xtdpthresh invest qm, qx(debt) noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_x_missing.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_x_missing_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
drop if firm > 3 & year != 1980
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE e_few_after_drop"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_e_few_after_drop.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_e_few_after_drop_es.csv", st_data(., "pyxes"))
    drop pyxes
}

use "../data/invest.dta", clear
xtset firm year
gen double cu = firm
gen double ct = year
gen double qm = .
gen double qone = 1
display "@@CASE ok_time_effects"
capture noisily xtdpthresh invest cashflow, qx(debt) td noboot grid(10)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/sc_ok_time_effects.csv", (st_numscalar("e(N)"), st_numscalar("e(N_stack)"), st_numscalar("e(N_units)")))
    quietly gen byte pyxes = e(sample)
    mata: pyx_export("../out/sc_ok_time_effects_es.csv", st_data(., "pyxes"))
    drop pyxes
}

exit, clear
