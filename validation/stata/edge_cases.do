version 17
set more off
clear all
display "@@CASE min_n1_t5"
import delimited using "../data/edge/min_n1_t5.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE min_n2_t4"
import delimited using "../data/edge/min_n2_t4.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE min_n3_t3"
import delimited using "../data/edge/min_n3_t3.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE min_n4_t4"
import delimited using "../data/edge/min_n4_t4.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE min_n5_t2"
import delimited using "../data/edge/min_n5_t2.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE min_n20_t3"
import delimited using "../data/edge/min_n20_t3.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE minregime_huge"
import delimited using "../data/edge/minregime_huge.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot minregime(10000)
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE trim_049"
import delimited using "../data/edge/trim_049.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot trim(0.49)
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE q_constant"
import delimited using "../data/edge/q_constant.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE q_rare_ones"
import delimited using "../data/edge/q_rare_ones.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE q_binary"
import delimited using "../data/edge/q_binary.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE q_four_values"
import delimited using "../data/edge/q_four_values.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) boot(99) rseed(7) gridci(20)
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE x_duplicate"
import delimited using "../data/edge/x_duplicate.csv", clear
xtset id t
capture noisily xtdpthresh y x1 x2, qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE iv_equals_x"
import delimited using "../data/edge/iv_equals_x.csv", clear
xtset id t
capture noisily xtdpthresh y x1, qx(q) noboot iv(z)
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE x_constant"
import delimited using "../data/edge/x_constant.csv", clear
xtset id t
capture noisily xtdpthresh y c, qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE units_fewer_than_iv"
import delimited using "../data/edge/units_fewer_than_iv.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE units_fewer_than_iv_boot"
import delimited using "../data/edge/units_fewer_than_iv_boot.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) boot(99) rseed(7) gridci(20)
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE y_zero"
import delimited using "../data/edge/y_zero.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
display "@@CASE y_constant"
import delimited using "../data/edge/y_constant.csv", clear
xtset id t
capture noisily xtdpthresh y , qx(q) noboot
display "@@RC " _rc
if _rc == 0 display "@@S gamma " %21.15g e(gamma)
if _rc == 0 display "@@S N " %21.15g e(N)
if _rc == 0 display "@@S N_units " %21.15g e(N_units)
if _rc == 0 display "@@S N_iv " %21.15g e(N_iv)
if _rc == 0 display "@@S estimator_twostep " %21.15g e(estimator_twostep)
if _rc == 0 display "@@S gamma_lo " %21.15g e(gamma_lo)
if _rc == 0 display "@@S gamma_hi " %21.15g e(gamma_hi)
exit, clear
