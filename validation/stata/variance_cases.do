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

mata:
real scalar pyx_sc(string scalar name)
{
    real matrix v
    v = st_numscalar(name)
    return(rows(v) * cols(v) == 1 ? v : .)
}
end

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
    mata: pyx_export("../out/vc_fd_jump_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_jump_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_jump_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_jump_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_jump_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_jump_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_jump_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_jump_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_jump_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_jump_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_jump_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_jump_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_jump_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fd_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_kink_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_kink_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_kink_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_kink_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_kink_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_kink_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_kink_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_kink_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_kink_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_kink_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_kink_wind_vup.csv", st_matrix("e(V_upper)"))
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
capture noisily xtdpthresh invest cashflow debt, qx(debt) kink noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_kink_q_regressor_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_kink_q_regressor_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_kink_q_regressor_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_kink_q_regressor_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_kink_q_regressor_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_kink_q_regressor_vup.csv", st_matrix("e(V_upper)"))
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
capture noisily xtdpthresh invest cashflow debt, qx(debt) noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_jump_q_regressor_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_jump_q_regressor_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_jump_q_regressor_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_jump_q_regressor_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_jump_q_regressor_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_jump_q_regressor_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_bw_small"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) bwscale(0.8) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_bw_small_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_bw_small_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_bw_small_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_bw_small_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_bw_small_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_bw_small_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_bw_large"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) bwscale(3.0) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_bw_large_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_bw_large_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_bw_large_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_bw_large_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_bw_large_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_bw_large_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_nocenter"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot nocenter grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_nocenter_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_nocenter_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_nocenter_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_nocenter_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_nocenter_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_nocenter_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_nocenter_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot nocenter grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_nocenter_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_nocenter_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_nocenter_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_nocenter_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_nocenter_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_nocenter_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_exog_only"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_exog_only_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_exog_only_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_exog_only_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_exog_only_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_exog_only_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_exog_only_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_exog_only_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) vce(windmeijer)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_exog_only_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_exog_only_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_exog_only_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_exog_only_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_exog_only_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_exog_only_wind_vup.csv", st_matrix("e(V_upper)"))
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
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) predetermined(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_predet_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_predet_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_predet_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_predet_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_predet_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_predet_vup.csv", st_matrix("e(V_upper)"))
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
capture noisily xtdpthresh invest cashflow L.tobin_q, qx(debt) static noboot grid(30)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_static_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_static_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_static_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_static_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_static_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_static_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_collapse_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) collapse noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_collapse_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_collapse_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_collapse_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_collapse_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_collapse_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_collapse_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_refine_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(15) refine(2) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_refine_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_refine_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_refine_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_refine_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_refine_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_refine_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_iv_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) vce(windmeijer) endogenous(tobin_q) iv(z1 z2)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_iv_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_iv_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_iv_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_iv_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_iv_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_iv_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fd_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_td_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_td_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_td_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_td_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_td_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_td_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) td noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_td_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_td_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_td_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_td_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_td_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_td_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_gaps"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_gaps_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_gaps_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_gaps_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_gaps_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_gaps_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_gaps_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_gaps_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_gaps_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_gaps_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_gaps_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_gaps_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_gaps_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_gaps_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fd_short_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_short_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_short_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_short_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_short_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_short_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_alternate_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_alternate_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_alternate_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_alternate_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_alternate_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_alternate_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_alternate_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fd_discrete_q"
capture noisily xtdpthresh invest cashflow, qx(qdisc) noboot grid(30) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fd_discrete_q_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fd_discrete_q_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fd_discrete_q_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fd_discrete_q_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fd_discrete_q_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fd_discrete_q_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fod_jump_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_jump_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_jump_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_jump_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_jump_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_jump_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fod_jump_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fod_jump_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_jump_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_jump_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_jump_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_jump_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_jump_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fod_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_kink_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_kink_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_kink_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_kink_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fod_kink_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot method(fod) grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fod_kink_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_kink_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_kink_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_kink_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_kink_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_kink_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fod_td_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_td_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_td_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_td_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_td_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_td_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fod_td_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) td noboot method(fod) grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fod_td_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_td_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_td_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_td_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_td_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_td_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fod_gaps_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_gaps_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_gaps_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_gaps_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_gaps_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_gaps_wind_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fod_short_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_short_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_short_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_short_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_short_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_short_vup.csv", st_matrix("e(V_upper)"))
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
    mata: pyx_export("../out/vc_fod_alternate_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_alternate_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_alternate_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_alternate_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_alternate_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_alternate_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fod_nocenter_wind"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot nocenter method(fod) grid(30) vce(windmeijer) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fod_nocenter_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_nocenter_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_nocenter_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_nocenter_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_nocenter_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_nocenter_wind_vup.csv", st_matrix("e(V_upper)"))
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
display "@@CASE fod_bw_small"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(30) bwscale(0.8) endogenous(tobin_q)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_fod_bw_small_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_fod_bw_small_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_fod_bw_small_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_fod_bw_small_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_fod_bw_small_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_fod_bw_small_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_help_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_help_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_help_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_help_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_help_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_help_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_wind"
capture noisily xtdpthresh invest , qx(debt) collapse noboot vce(windmeijer) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_help_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_help_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_help_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_help_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_help_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_help_wind_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_kink"
capture noisily xtdpthresh invest , qx(debt) kink collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_help_kink_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_help_kink_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_help_kink_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_help_kink_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_help_kink_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_help_kink_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_kink_wind"
capture noisily xtdpthresh invest , qx(debt) kink collapse noboot vce(windmeijer) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_help_kink_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_help_kink_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_help_kink_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_help_kink_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_help_kink_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_help_kink_wind_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_fod"
capture noisily xtdpthresh invest , qx(debt) collapse noboot method(fod) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_help_fod_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_help_fod_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_help_fod_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_help_fod_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_help_fod_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_help_fod_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_help_fod_wind"
capture noisily xtdpthresh invest , qx(debt) collapse noboot method(fod) vce(windmeijer) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_help_fod_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_help_fod_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_help_fod_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_help_fod_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_help_fod_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_help_fod_wind_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
display "@@CASE full_maxlag_2_10_wind"
capture noisily xtdpthresh invest , qx(debt) collapse noboot vce(windmeijer) maxlag(2 10) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_maxlag_2_10_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_maxlag_2_10_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_maxlag_2_10_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_maxlag_2_10_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_maxlag_2_10_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_maxlag_2_10_wind_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
drop if mod(firm + 3*year, 11) == 0
display "@@CASE full_unbalanced_gaps_wind"
capture noisily xtdpthresh invest , qx(debt) collapse noboot vce(windmeijer) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_unbalanced_gaps_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_unbalanced_gaps_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_unbalanced_gaps_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_unbalanced_gaps_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_unbalanced_gaps_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_unbalanced_gaps_wind_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
drop if firm <= 10 & year > 1973
drop if firm >= 11 & firm <= 20 & year > 1974
display "@@CASE full_unbalanced_short"
capture noisily xtdpthresh invest , qx(debt) collapse noboot maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_unbalanced_short_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_unbalanced_short_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_unbalanced_short_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_unbalanced_short_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_unbalanced_short_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_unbalanced_short_vup.csv", st_matrix("e(V_upper)"))
}

use "../data/invest.dta", clear
xtset firm year
egen double peer_q = mean(tobin_q), by(year)
drop if firm >= 11 & firm <= 40 & mod(year, 2) == 0
display "@@CASE full_unbalanced_alternate_wind"
capture noisily xtdpthresh invest , qx(debt) collapse noboot vce(windmeijer) maxlag(3 8) endogenous(cashflow tobin_q debt)
display "@@RC " _rc
if _rc == 0 {
    mata: pyx_export("../out/vc_full_unbalanced_alternate_wind_sc.csv", (pyx_sc("e(gamma)"), pyx_sc("e(obj)"), pyx_sc("e(estimator_twostep)"), pyx_sc("e(N)"), pyx_sc("e(N_units)"), pyx_sc("e(N_clust)"), pyx_sc("e(N_switch)"), pyx_sc("e(hansen)"), pyx_sc("e(hansen_df)"), pyx_sc("e(hansen_p)"), pyx_sc("e(ar1)"), pyx_sc("e(ar1_p)"), pyx_sc("e(ar2)"), pyx_sc("e(ar2_p)"), pyx_sc("e(ar_joint)"), pyx_sc("e(ar1_cond)"), pyx_sc("e(ar2_cond)"), pyx_sc("e(ar1_b0)"), pyx_sc("e(ar1_T1)"), pyx_sc("e(ar1_TT)"), pyx_sc("e(ar2_b0)"), pyx_sc("e(ar2_T1)"), pyx_sc("e(ar2_TT)"), pyx_sc("e(joint_vce)"), pyx_sc("e(gamma_bw)"), pyx_sc("e(q_nvals_bw)"), pyx_sc("e(vce_applied)"), pyx_sc("e(wind_same_threshold)")))
    mata: pyx_export("../out/vc_full_unbalanced_alternate_wind_b.csv", st_matrix("e(b)"))
    mata: pyx_export("../out/vc_full_unbalanced_alternate_wind_v.csv", st_matrix("e(V)"))
    mata: pyx_export("../out/vc_full_unbalanced_alternate_wind_vcond.csv", st_matrix("e(V_cond)"))
    mata: pyx_export("../out/vc_full_unbalanced_alternate_wind_bup.csv", st_matrix("e(b_upper)"))
    mata: pyx_export("../out/vc_full_unbalanced_alternate_wind_vup.csv", st_matrix("e(V_upper)"))
}

exit, clear
