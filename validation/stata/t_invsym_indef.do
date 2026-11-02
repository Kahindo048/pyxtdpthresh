version 17
set more off
mata:
void show(string scalar nm, real matrix A)
{
    real matrix B
    B = invsym(A)
    printf("%s: ", nm)
    printf("%g %g %g %g\n", B[1,1], B[1,cols(B)], B[rows(B),1], B[rows(B),cols(B)])
}
show("diag(1,-1)", (1,0\0,-1))
show("[1 2;2 1]", (1,2\2,1))
show("[-1]", (-1))
show("[0 1;1 0]", (0,1\1,0))
show("[-2 1;1 -2]", (-2,1\1,-2))
show("[1 1;1 1]", (1,1\1,1))
show("[2 1;1 -1]", (2,1\1,-1))
end
