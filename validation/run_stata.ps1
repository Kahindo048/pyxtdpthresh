# Usage: .\run_stata.ps1 -Do path\to\file.do  (Stata 17 MP in batch; always exits; prints the log of the wrapper)
param([Parameter(Mandatory=$true)][string]$Do, [int]$TimeoutSec = 900, [switch]$Quiet)
$stata = "C:\Program Files\Stata17\StataMP-64.exe"
$Do = (Resolve-Path $Do).Path
$dir = Split-Path $Do -Parent
$name = [IO.Path]::GetFileNameWithoutExtension($Do)
$wrap = Join-Path $dir ("_run_" + $name + ".do")
$log  = Join-Path $dir ("_run_" + $name + ".log")
[IO.File]::WriteAllText($wrap, "capture noisily do `"$Do`"`r`nlocal rc = _rc`r`nexit, clear`r`n", [Text.Encoding]::ASCII)
if (Test-Path $log) { Remove-Item $log -Force }
$p = Start-Process -FilePath $stata -ArgumentList "/e","do","`"$wrap`"" -WorkingDirectory $dir -PassThru
if (-not $p.WaitForExit($TimeoutSec * 1000)) { $p.Kill(); Write-Error "Stata timeout"; exit 2 }
Start-Sleep -Milliseconds 300
if (-not (Test-Path $log)) { Write-Error "no log produced"; exit 1 }
if (-not $Quiet) { Get-Content $log -Encoding UTF8 | Select-Object -Skip 19 }
