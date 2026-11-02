version 17
set more off
set rng mt64
foreach s in 123 12345 1 {
    set seed `s'
    mata: u = uniform(1, 6)'
    mata: st_local("line", invtokens(strofreal(u', "%21.17g")))
    display "SEED `s': `line'"
    set seed `s'
    mata: z = invnormal(uniform(1, 4))'
    mata: st_local("line", invtokens(strofreal(z', "%21.17g")))
    display "NORM `s': `line'"
}
display c(rng)
display c(rngstate)
