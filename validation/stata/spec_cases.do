version 17
set more off
clear all
use "../data/invest.dta", clear
xtset firm year
gen double z1 = cashflow*tobin_q + debt
gen double z2 = ln(1 + tobin_q)
display "@@CASE ok_default"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE ok_fod"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(FOD) grid(10)
display "@@RC " _rc
display "@@CASE ok_maxlag_pair"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) maxlag(2 8)
display "@@RC " _rc
display "@@CASE ok_maxlag_one"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) maxlag(3)
display "@@RC " _rc
display "@@CASE ok_vce_case"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) vce(Windmeijer)
display "@@RC " _rc
display "@@CASE ok_level"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) level(90)
display "@@RC " _rc
display "@@CASE ok_bad_seed_without_bootstrap"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) rseed(1.5)
display "@@RC " _rc
display "@@CASE ok_unit_without_bootstrap"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(10) boottype(unit)
display "@@RC " _rc
display "@@CASE ok_bad_nboot_without_bootstrap"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) boot(3)
display "@@RC " _rc
display "@@CASE ok_bad_gridci_without_bootstrap"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) gridci(3)
display "@@RC " _rc
display "@@CASE ok_coef_boot_onestep"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot nowarn grid(10) coefboot(onestep)
display "@@RC " _rc
display "@@CASE vce"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) vce(bogus)
display "@@RC " _rc
display "@@CASE coef_ci_type"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) coefcitype(bogus)
display "@@RC " _rc
display "@@CASE coef_boot_gs"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) coefboot(gs)
display "@@RC " _rc
display "@@CASE coef_boot"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) coefboot(bogus)
display "@@RC " _rc
display "@@CASE grid_type"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) gridtype(bogus)
display "@@RC " _rc
display "@@CASE min_regime"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) minregime(-1)
display "@@RC " _rc
display "@@CASE bw_scale_zero"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) bwscale(0)
display "@@RC " _rc
display "@@CASE bw_scale_negative"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) bwscale(-1)
display "@@RC " _rc
display "@@CASE refine_high"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) refine(21)
display "@@RC " _rc
display "@@CASE refine_negative"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) refine(-1)
display "@@RC " _rc
display "@@CASE refine_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink noboot grid(10) refine(2)
display "@@RC " _rc
display "@@CASE search_mode"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) searchmode(fixed)
display "@@RC " _rc
display "@@CASE search_max"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) searchmax(50)
display "@@RC " _rc
display "@@CASE search_tol"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) searchtol(1e-05)
display "@@RC " _rc
display "@@CASE history"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) history(bogus)
display "@@RC " _rc
display "@@CASE history_sample_lag"
capture noisily xtdpthresh invest L.cashflow, qx(debt) noboot grid(10) history(sample)
display "@@RC " _rc
display "@@CASE history_sample_ok"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) history(sample)
display "@@RC " _rc
display "@@CASE boot_type_exact"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) boottype(exact)
display "@@RC " _rc
display "@@CASE boot_type"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) boottype(bogus)
display "@@RC " _rc
display "@@CASE unit_fod"
capture noisily xtdpthresh invest cashflow, qx(debt) method(fod) grid(10) boottype(unit)
display "@@RC " _rc
display "@@CASE unit_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink grid(10) boottype(unit)
display "@@RC " _rc
display "@@CASE grid_sample"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) gridsample(bogus)
display "@@RC " _rc
display "@@CASE lev_maxlag"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) levmaxlag(2)
display "@@RC " _rc
display "@@CASE iv_maxlag"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(z1, maxlag(2))
display "@@RC " _rc
display "@@CASE method_system"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(system) grid(10)
display "@@RC " _rc
display "@@CASE method"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(bogus) grid(10)
display "@@RC " _rc
display "@@CASE grid_small"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(9)
display "@@RC " _rc
display "@@CASE grid_ci_small"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(10) gridci(9)
display "@@RC " _rc
display "@@CASE gamma_test_noboot"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) citest(0.2)
display "@@RC " _rc
display "@@CASE continuity_noboot"
capture noisily xtdpthresh invest cashflow, qx(debt) conttest noboot grid(10)
display "@@RC " _rc
display "@@CASE continuity_notest"
capture noisily xtdpthresh invest cashflow, qx(debt) conttest notest grid(10)
display "@@RC " _rc
display "@@CASE trim_high"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) trim(0.5)
display "@@RC " _rc
display "@@CASE trim_low"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) trim(0.005)
display "@@RC " _rc
display "@@CASE n_boot_small"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(10) boot(9) gridci(10)
display "@@RC " _rc
display "@@CASE seed_fraction"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(10) boot(10) rseed(1.5) gridci(10)
display "@@RC " _rc
display "@@CASE seed_negative"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(10) boot(10) rseed(-1) gridci(10)
display "@@RC " _rc
display "@@CASE seed_large"
capture noisily xtdpthresh invest cashflow, qx(debt) grid(10) boot(10) rseed(2147483648) gridci(10)
display "@@RC " _rc
display "@@CASE level_low"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) level(5)
display "@@RC " _rc
display "@@CASE level_high"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) level(100)
display "@@RC " _rc
display "@@CASE maxlag_zero"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) maxlag(0)
display "@@RC " _rc
display "@@CASE maxlag_three"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) maxlag(1 2 3)
display "@@RC " _rc
display "@@CASE maxlag_fraction"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) maxlag(1.5)
display "@@RC " _rc
display "@@CASE maxlag_order"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) maxlag(3 2)
display "@@RC " _rc
display "@@CASE grid_fraction"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(5.5)
display "@@RC " _rc
display "@@CASE min_regime_fraction"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) minregime(1.5)
display "@@RC " _rc
display "@@CASE refine_fraction"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) refine(2.5)
display "@@RC " _rc
display "@@CASE trim_text"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) trim(abc)
display "@@RC " _rc
display "@@CASE bw_scale_text"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) bwscale(abc)
display "@@RC " _rc
display "@@CASE td_unit"
capture noisily xtdpthresh invest cashflow, qx(debt) td grid(10) boot(10) boottype(unit) gridci(10)
display "@@RC " _rc
display "@@CASE td_twostep"
capture noisily xtdpthresh invest cashflow, qx(debt) td nowarn grid(10) boot(10) gridci(10) coefboot(twostep)
display "@@RC " _rc
display "@@CASE td_twostep_noboot"
capture noisily xtdpthresh invest cashflow, qx(debt) td noboot nowarn grid(10) coefboot(twostep)
display "@@RC " _rc
display "@@CASE ok_range"
capture noisily xtdpthresh invest L(1/2).cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE ok_predetermined_lag2"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(L2.invest)
display "@@RC " _rc
display "@@CASE ok_endogenous_lag2"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(L2.invest)
display "@@RC " _rc
display "@@CASE ok_iv_lag2"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(L2.invest)
display "@@RC " _rc
display "@@CASE ok_dl"
capture noisily xtdpthresh invest DL.cashflow F.tobin_q, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE y_operator"
capture noisily xtdpthresh L.invest cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE y_difference"
capture noisily xtdpthresh D.invest cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE x_lag2_y"
capture noisily xtdpthresh invest L2.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE x_lag3_y"
capture noisily xtdpthresh invest cashflow L3.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE exogenous_lag2_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) exogenous(L2.invest)
display "@@RC " _rc
display "@@CASE x_ld_y"
capture noisily xtdpthresh invest LD.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE x_lead_y"
capture noisily xtdpthresh invest F.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE x_seasonal_y"
capture noisily xtdpthresh invest S12.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE exogenous_diff_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) exogenous(D.invest)
display "@@RC " _rc
display "@@CASE endogenous_diff_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(D.invest)
display "@@RC " _rc
display "@@CASE endogenous_lead_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(F.invest)
display "@@RC " _rc
display "@@CASE predetermined_ld_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(LD.invest)
display "@@RC " _rc
display "@@CASE iv_diff_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(D.invest)
display "@@RC " _rc
display "@@CASE iv_lead_y"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(F2.invest)
display "@@RC " _rc
display "@@CASE bad_operator"
capture noisily xtdpthresh invest Q.cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE bad_name"
capture noisily xtdpthresh invest 2cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE ok_roles"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q) predetermined(L.debt)
display "@@RC " _rc
display "@@CASE ok_lag_not_overlapping"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(L.cashflow)
display "@@RC " _rc
display "@@CASE ok_exogenous_earlier_lag"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(L2.tobin_q) exogenous(L.tobin_q)
display "@@RC " _rc
display "@@CASE ok_predetermined_lag_exogenous_now"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(L.cashflow)
display "@@RC " _rc
display "@@CASE ok_iv_far_lag"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q) iv(L2.tobin_q)
display "@@RC " _rc
display "@@CASE ok_iv_fod_lag"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot method(fod) grid(10) iv(L.invest)
display "@@RC " _rc
display "@@CASE ok_conttest"
capture noisily xtdpthresh invest cashflow debt, qx(debt) conttest grid(10) boot(10) gridci(10)
display "@@RC " _rc
display "@@CASE overlap_endog_x"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(cashflow)
display "@@RC " _rc
display "@@CASE overlap_endog_x_lag"
capture noisily xtdpthresh invest L.cashflow, qx(debt) noboot grid(10) endogenous(L1.cashflow)
display "@@RC " _rc
display "@@CASE overlap_endog_x_l0"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(L0.cashflow)
display "@@RC " _rc
display "@@CASE overlap_endog_exog"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q) exogenous(tobin_q)
display "@@RC " _rc
display "@@CASE overlap_x_exog"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) exogenous(cashflow)
display "@@RC " _rc
display "@@CASE overlap_predet_x"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(cashflow)
display "@@RC " _rc
display "@@CASE overlap_predet_exog"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(tobin_q) exogenous(tobin_q)
display "@@RC " _rc
display "@@CASE overlap_predet_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q) predetermined(tobin_q)
display "@@RC " _rc
display "@@CASE iv_declared_endog"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(z1) iv(z1)
display "@@RC " _rc
display "@@CASE iv_declared_predet"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(z1) iv(z1)
display "@@RC " _rc
display "@@CASE static_empty"
capture noisily xtdpthresh invest , qx(debt) static noboot grid(10)
display "@@RC " _rc
display "@@CASE conttest_kink"
capture noisily xtdpthresh invest cashflow, qx(debt) kink conttest grid(10) boot(10) gridci(10)
display "@@RC " _rc
display "@@CASE conttest_q_missing"
capture noisily xtdpthresh invest cashflow, qx(debt) conttest grid(10) boot(10) gridci(10)
display "@@RC " _rc
display "@@CASE dup_x"
capture noisily xtdpthresh invest cashflow cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE dup_x_l0"
capture noisily xtdpthresh invest cashflow L0.cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE dup_x_lag"
capture noisily xtdpthresh invest L.cashflow l1.cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE dup_exogenous"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) exogenous(tobin_q tobin_q)
display "@@RC " _rc
display "@@CASE dup_endogenous"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q tobin_q)
display "@@RC " _rc
display "@@CASE dup_predetermined"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(tobin_q tobin_q)
display "@@RC " _rc
display "@@CASE dup_iv"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(z1 z1)
display "@@RC " _rc
display "@@CASE y_in_x"
capture noisily xtdpthresh invest invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE y_in_x_l0"
capture noisily xtdpthresh invest L0.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE y_endogenous"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(invest)
display "@@RC " _rc
display "@@CASE y_iv"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(invest)
display "@@RC " _rc
display "@@CASE q_is_y"
capture noisily xtdpthresh invest cashflow, qx(invest) noboot grid(10)
display "@@RC " _rc
display "@@CASE exogenous_lag_of_endogenous"
capture noisily xtdpthresh invest L.tobin_q, qx(debt) noboot grid(10) endogenous(tobin_q)
display "@@RC " _rc
display "@@CASE exogenous_same_date_as_predetermined"
capture noisily xtdpthresh invest , qx(debt) noboot grid(10) predetermined(cashflow) exogenous(L.cashflow)
display "@@RC " _rc
display "@@CASE exogenous_lag3_of_endogenous_lag2"
capture noisily xtdpthresh invest L3.tobin_q, qx(debt) noboot grid(10) endogenous(L2.tobin_q)
display "@@RC " _rc
display "@@CASE exogenous_difference_of_endogenous"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q) exogenous(D.tobin_q)
display "@@RC " _rc
display "@@CASE iv_lag_too_short"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(tobin_q) iv(L.tobin_q)
display "@@RC " _rc
display "@@CASE iv_lag_depvar_fd"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) iv(L.invest)
display "@@RC " _rc
display "@@CASE iv_lag_predetermined"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(L.tobin_q) iv(tobin_q)
display "@@RC " _rc
display "@@CASE ok_static_predetermined_lag"
capture noisily xtdpthresh invest cashflow, qx(debt) static noboot grid(10) predetermined(L.invest)
display "@@RC " _rc
display "@@CASE ok_dynamic_lag2_exogenous_as_predetermined"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(L2.invest L3.invest)
display "@@RC " _rc
display "@@CASE auto_lag_x"
capture noisily xtdpthresh invest L.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE auto_lag_x_l1"
capture noisily xtdpthresh invest l1.invest cashflow, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE auto_lag_fl2"
capture noisily xtdpthresh invest FL2.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE auto_lag_l2f"
capture noisily xtdpthresh invest L2F.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
display "@@CASE auto_lag_endogenous"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) endogenous(L.invest)
display "@@RC " _rc
display "@@CASE auto_lag_predetermined"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) predetermined(L.invest)
display "@@RC " _rc
display "@@CASE auto_lag_exogenous"
capture noisily xtdpthresh invest cashflow, qx(debt) noboot grid(10) exogenous(L.invest)
display "@@RC " _rc
display "@@CASE static_lag_exogenous"
capture noisily xtdpthresh invest L.invest, qx(debt) static noboot grid(10)
display "@@RC " _rc
display "@@CASE auto_lag_ld_is_not_the_lag"
capture noisily xtdpthresh invest LD.invest, qx(debt) noboot grid(10)
display "@@RC " _rc
exit, clear
