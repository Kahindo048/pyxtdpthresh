# Alternate one Stata fit and one Python fit, so both see the same state of the machine (J.3.1).
# Usage: powershell tools/paired_bench.ps1   (from the project root); writes validation/stata/perf_pairs.csv
param([int]$Reps = 3, [string[]]$Sizes = @("hansen", "2000", "10000"))
$root = Split-Path $PSScriptRoot -Parent
$python = Join-Path $root ".venv\Scripts\python.exe"
$csv = Join-Path $root "validation\stata\perf_pairs.csv"
$env:PYTHONPATH = "$root;$root\src"
Set-Location $root
"who,size,seconds" | Out-File $csv -Encoding ascii
for ($r = 1; $r -le $Reps; $r++) {
    foreach ($size in $Sizes) {
        & (Join-Path $root "validation\run_stata.ps1") -Do "validation\stata\perf_pair_$size.do" -TimeoutSec 900 -Quiet
        & $python "tools\bench_vs_stata.py" pair-python $size
    }
}
