version 17
set more off
mata:
real scalar inv11(real scalar x)
{
    real matrix B
    B = invsym(x)
    return(B[1,1])
}
real scalar b11_2x2(real scalar s)
{
    real matrix B
    B = invsym(s * (2,1 \ 1,2))
    return(B[1,1])
}
real scalar b22_diag(real scalar a, real scalar b)
{
    real matrix B
    B = invsym(diag((a, b)))
    return(B[2,2])
}
real scalar b11_diag(real scalar a, real scalar b)
{
    real matrix B
    B = invsym(diag((a, b)))
    return(B[1,1])
}
"1x1"
for (k=8; k<=22; k=k+2) printf("k=%g inv=%g\n", k, inv11(10^(-k)))
"2x2"
for (k=8; k<=22; k=k+2) printf("k=%g B11=%g\n", k, b11_2x2(10^(-k)))
"diag second"
for (k=10; k<=22; k=k+4) printf("k=%g B22=%g\n", k, b22_diag(1, 10^(-k)))
"diag first"
for (k=10; k<=22; k=k+4) printf("k=%g B11=%g\n", k, b11_diag(10^(-k), 1))
end
