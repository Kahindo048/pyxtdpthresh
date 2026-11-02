version 17
set more off
mata:
real scalar inv11(real scalar x)
{
    real matrix B
    B = invsym(x)
    return(B[1,1])
}
for (k=18; k<=20.01; k=k+0.125) printf("k=%g inv=%g\n", k, inv11(10^(-k)))
end
