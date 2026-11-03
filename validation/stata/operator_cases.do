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
display "@@IN l.cashflow"
capture noisily pyx_canon l.cashflow
display "@@RC " _rc
display "@@IN l1.cashflow"
capture noisily pyx_canon l1.cashflow
display "@@RC " _rc
display "@@IN L2.cashflow"
capture noisily pyx_canon L2.cashflow
display "@@RC " _rc
display "@@IN ll.cashflow"
capture noisily pyx_canon ll.cashflow
display "@@RC " _rc
display "@@IN l2l.cashflow"
capture noisily pyx_canon l2l.cashflow
display "@@RC " _rc
display "@@IN ld.cashflow"
capture noisily pyx_canon ld.cashflow
display "@@RC " _rc
display "@@IN l1d.cashflow"
capture noisily pyx_canon l1d.cashflow
display "@@RC " _rc
display "@@IN d1.cashflow"
capture noisily pyx_canon d1.cashflow
display "@@RC " _rc
display "@@IN d.cashflow"
capture noisily pyx_canon d.cashflow
display "@@RC " _rc
display "@@IN d2.cashflow"
capture noisily pyx_canon d2.cashflow
display "@@RC " _rc
display "@@IN f.cashflow"
capture noisily pyx_canon f.cashflow
display "@@RC " _rc
display "@@IN f1.cashflow"
capture noisily pyx_canon f1.cashflow
display "@@RC " _rc
display "@@IN f2.cashflow"
capture noisily pyx_canon f2.cashflow
display "@@RC " _rc
display "@@IN s.cashflow"
capture noisily pyx_canon s.cashflow
display "@@RC " _rc
display "@@IN s1.cashflow"
capture noisily pyx_canon s1.cashflow
display "@@RC " _rc
display "@@IN s12.cashflow"
capture noisily pyx_canon s12.cashflow
display "@@RC " _rc
display "@@IN L0.cashflow"
capture noisily pyx_canon L0.cashflow
display "@@RC " _rc
display "@@IN d0.cashflow"
capture noisily pyx_canon d0.cashflow
display "@@RC " _rc
display "@@IN l(1).cashflow"
capture noisily pyx_canon l(1).cashflow
display "@@RC " _rc
display "@@IN l(2).cashflow"
capture noisily pyx_canon l(2).cashflow
display "@@RC " _rc
display "@@IN l(0/2).cashflow"
capture noisily pyx_canon l(0/2).cashflow
display "@@RC " _rc
display "@@IN l(1/2).cashflow"
capture noisily pyx_canon l(1/2).cashflow
display "@@RC " _rc
display "@@IN l(1 3).cashflow"
capture noisily pyx_canon l(1 3).cashflow
display "@@RC " _rc
display "@@IN ld2.cashflow"
capture noisily pyx_canon ld2.cashflow
display "@@RC " _rc
display "@@IN L2D.cashflow"
capture noisily pyx_canon L2D.cashflow
display "@@RC " _rc
display "@@IN dl.cashflow"
capture noisily pyx_canon dl.cashflow
display "@@RC " _rc
display "@@IN lf.cashflow"
capture noisily pyx_canon lf.cashflow
display "@@RC " _rc
display "@@IN fl.cashflow"
capture noisily pyx_canon fl.cashflow
display "@@RC " _rc
display "@@IN l0f.cashflow"
capture noisily pyx_canon l0f.cashflow
display "@@RC " _rc
display "@@IN ls.cashflow"
capture noisily pyx_canon ls.cashflow
display "@@RC " _rc
display "@@IN ll2.cashflow"
capture noisily pyx_canon ll2.cashflow
display "@@RC " _rc
display "@@IN L3L.cashflow"
capture noisily pyx_canon L3L.cashflow
display "@@RC " _rc
display "@@IN d(1/2).cashflow"
capture noisily pyx_canon d(1/2).cashflow
display "@@RC " _rc
display "@@IN LLL.cashflow"
capture noisily pyx_canon LLL.cashflow
display "@@RC " _rc
display "@@IN FF.cashflow"
capture noisily pyx_canon FF.cashflow
display "@@RC " _rc
display "@@IN dd.cashflow"
capture noisily pyx_canon dd.cashflow
display "@@RC " _rc
display "@@IN ss.cashflow"
capture noisily pyx_canon ss.cashflow
display "@@RC " _rc
display "@@IN L(1/2)D.cashflow"
capture noisily pyx_canon L(1/2)D.cashflow
display "@@RC " _rc
display "@@IN l01.cashflow"
capture noisily pyx_canon l01.cashflow
display "@@RC " _rc
display "@@IN L10.cashflow"
capture noisily pyx_canon L10.cashflow
display "@@RC " _rc
display "@@IN cashflow"
capture noisily pyx_canon cashflow
display "@@RC " _rc
display "@@IN L.D2.cashflow"
capture noisily pyx_canon L.D2.cashflow
display "@@RC " _rc
display "@@IN S2D.cashflow"
capture noisily pyx_canon S2D.cashflow
display "@@RC " _rc
display "@@IN DS2.cashflow"
capture noisily pyx_canon DS2.cashflow
display "@@RC " _rc
display "@@IN ls2.cashflow"
capture noisily pyx_canon ls2.cashflow
display "@@RC " _rc
display "@@IN fd.cashflow"
capture noisily pyx_canon fd.cashflow
display "@@RC " _rc
display "@@IN df.cashflow"
capture noisily pyx_canon df.cashflow
display "@@RC " _rc
display "@@IN ldl.cashflow"
capture noisily pyx_canon ldl.cashflow
display "@@RC " _rc
display "@@IN l(1/2)f.cashflow"
capture noisily pyx_canon l(1/2)f.cashflow
display "@@RC " _rc
display "@@IN s2s3.cashflow"
capture noisily pyx_canon s2s3.cashflow
display "@@RC " _rc
display "@@IN F2L.cashflow"
capture noisily pyx_canon F2L.cashflow
display "@@RC " _rc
display "@@IN D(1 2).cashflow"
capture noisily pyx_canon D(1 2).cashflow
display "@@RC " _rc
use "../data/invest.dta", clear
xtset firm year
keep if firm <= 30
drop if mod(firm + 3*year, 7) == 0
sort firm year
quietly gen double pyxv1 = L.cashflow
quietly gen double pyxv2 = L2.cashflow
quietly gen double pyxv3 = F.cashflow
quietly gen double pyxv4 = F2.cashflow
quietly gen double pyxv5 = D.cashflow
quietly gen double pyxv6 = D2.cashflow
quietly gen double pyxv7 = LD.cashflow
quietly gen double pyxv8 = DL.cashflow
quietly gen double pyxv9 = L2D.cashflow
quietly gen double pyxv10 = S2.cashflow
quietly gen double pyxv11 = S3.cashflow
quietly gen double pyxv12 = LS2.cashflow
quietly gen double pyxv13 = FD.cashflow
quietly gen double pyxv14 = DF.cashflow
quietly gen double pyxv15 = L3.cashflow
quietly gen double pyxv16 = L.D2.cashflow
quietly gen double pyxv17 = SS.cashflow
quietly gen double pyxv18 = S2D.cashflow
quietly gen double pyxv19 = LF.cashflow
keep firm year cashflow pyxv*
export delimited using "../out/ts_values.csv", replace
exit, clear
