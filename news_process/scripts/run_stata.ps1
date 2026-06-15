<#
.SYNOPSIS
  Run Stata .do file(s) in TRUE batch mode (/b) so the "Completed" dialog never pops.

.DESCRIPTION
  On Windows, StataMP-64.exe /e and bare GUI / double-click show a modal
  "(do-file) completed. Output saved in ... .log" dialog that BLOCKS, waiting for
  a manual click on OK. /b (true batch) does NOT: it runs headless, writes the
  .log, and exits with a return code.

  This wrapper hard-codes /b + Start-Process -Wait, so there is no flag to get
  wrong and the dialog can never be triggered. It is the recommended entry point
  for running any .do in this project (same behavior as
  papers/_common/stata_runner.py::run_do). Rationale in Chinese: see CLAUDE.md
  section "Stata Environment".

  NOTE: keep this script ASCII-only. Windows PowerShell 5.1 reads .ps1 without a
  BOM as the system ANSI codepage (GBK here); non-ASCII text would be mojibaked
  and break parsing.

.PARAMETER Path
  A .do file, a directory (runs all *.do in it), or a glob. One or more.

.PARAMETER StataBin
  Stata executable. Defaults to $env:NEWS_PROCESS_STATA_BIN, then common install
  dirs, then PATH.

.PARAMETER TimeoutSec
  Per-.do timeout in seconds (default 1800 = 30 min). On timeout the process is
  force-killed and counted as a failure.

.EXAMPLE
  .\scripts\run_stata.ps1 build\robustness_smoke\bank_news_clarity\15_table6_structural_subsamples_dvtest.do

.EXAMPLE
  # run every *.do in a directory, no dialogs
  .\scripts\run_stata.ps1 build\robustness_smoke\bank_news_clarity
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Path,

    [string]$StataBin = $env:NEWS_PROCESS_STATA_BIN,

    [int]$TimeoutSec = 1800
)

$ErrorActionPreference = 'Stop'

# ---- 1. Locate the Stata executable -----------------------------------------
if (-not $StataBin -or -not (Test-Path $StataBin)) {
    $candidates = @(
        'C:\Program Files\StataNow19\StataMP-64.exe',
        'C:\Program Files\Stata19\StataMP-64.exe',
        'C:\Program Files\StataNow19\StataSE-64.exe',
        'C:\Program Files\Stata19\StataSE-64.exe',
        'C:\Program Files\StataNow19\StataIC-64.exe'
    )
    $StataBin = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $StataBin) {
        $cmd = Get-Command 'StataMP-64.exe' -ErrorAction SilentlyContinue
        if ($cmd) { $StataBin = $cmd.Source }
    }
}
if (-not $StataBin -or -not (Test-Path $StataBin)) {
    Write-Error "Stata executable not found. Set `$env:NEWS_PROCESS_STATA_BIN or pass -StataBin."
    exit 2
}

# ---- 2. Expand inputs into a list of .do files ------------------------------
$doFiles = New-Object System.Collections.Generic.List[System.IO.FileInfo]
foreach ($p in $Path) {
    if (Test-Path $p -PathType Container) {
        Get-ChildItem -Path $p -Filter '*.do' -File | Sort-Object Name | ForEach-Object { $doFiles.Add($_) }
    }
    elseif (Test-Path $p -PathType Leaf) {
        $doFiles.Add((Get-Item $p))
    }
    else {
        Get-ChildItem -Path $p -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -eq '.do' } | ForEach-Object { $doFiles.Add($_) }
    }
}
if ($doFiles.Count -eq 0) {
    Write-Error ("No .do files matched: " + ($Path -join ', '))
    exit 2
}

# ---- 3. Run each with /b ----------------------------------------------------
# Launch via .NET Process (UseShellExecute=$false) instead of Start-Process:
# Start-Process can hand back a forwarder/bootstrap process for a GUI-subsystem
# exe, so WaitForExit/ExitCode track the wrong thing (wrong timing + exit code).
# CreateProcess gives a handle to the real StataMP-64.exe process.
#
# Verdict comes from the LOG, not the raw exit code: StataMP /b exit codes are
# unreliable on this machine (observed: -1 on a clean run, 0 on a real error) --
# likely because several instances contend on one lab license. A real uncaught
# error (bad command / missing file / missing var) writes "r(###);" to the log,
# so scanning for it is the reliable signal; `capture`d errors do not write it.
# Edge case: a bare `error N` command can abort before the line is flushed -- rare
# in real do-files. When in doubt, read the .log.
Write-Host ("Stata bin : " + $StataBin)
Write-Host "Batch flag: /b  (true batch, no 'Completed' dialog)"
Write-Host ('=' * 72)
$fail = 0
foreach ($do in $doFiles) {
    $logPath = Join-Path $do.DirectoryName ($do.BaseName + '.log')
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $StataBin
    $psi.Arguments = '/b do "' + $do.FullName + '"'
    $psi.WorkingDirectory = $do.DirectoryName
    $psi.UseShellExecute = $false
    $p = [System.Diagnostics.Process]::Start($psi)
    $exited = $p.WaitForExit($TimeoutSec * 1000)
    $sw.Stop()
    $secs = [int]$sw.Elapsed.TotalSeconds
    if (-not $exited) {
        try { $p.Kill() } catch {}
        $fail++
        Write-Host ("[TIMEOUT] >" + $TimeoutSec + "s  " + $do.Name + "  (killed)")
        continue
    }
    $rc = $p.ExitCode
    $errLines = @()
    if (Test-Path $logPath) {
        $errLines = @(Select-String -Path $logPath -Pattern '^r\(\d+\);' -ErrorAction SilentlyContinue)
    }
    if ($errLines.Count -gt 0) {
        $fail++
        $first = ($errLines | Select-Object -First 1).Line
        Write-Host ("[ERR] " + $secs + "s  " + $do.Name + "  (" + $first + "  exit=" + $rc + ")")
    }
    elseif (-not (Test-Path $logPath)) {
        if ($rc -eq 0) {
            Write-Host ("[OK ] " + $secs + "s  " + $do.Name + "  (no log; exit=0)")
        }
        else {
            $fail++
            Write-Host ("[ERR] " + $secs + "s  " + $do.Name + "  (no log; exit=" + $rc + ")")
        }
    }
    else {
        Write-Host ("[OK ] " + $secs + "s  " + $do.Name + "  (log clean; exit=" + $rc + ")")
    }
}
Write-Host ('=' * 72)
Write-Host ("Done: " + $doFiles.Count + " .do, " + $fail + " failed (by log scan). Log: <do-name>.log next to each .do.")
exit ([int]($fail -gt 0))
