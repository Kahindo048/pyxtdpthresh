version 17
set more off
mata:
x = (3\1\4\1\5\9\2\6\5\3)
mm_quantile(x,1,0.2)
mm_quantile(x,1,0.8)
mm_quantile(x,1,0.25,0)
mm_quantile(x,1,0.25,1)
mm_quantile(x,1,0.25,2)
mm_quantile(x,1,0.25,3)
mm_quantile(x,1,0.15,2)
mm_quantile(x,1,0.35,2)
end
