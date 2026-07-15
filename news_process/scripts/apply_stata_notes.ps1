# apply_stata_notes.ps1 — Stata variable notes 实机注入编排 (WP2, 计划 §3b 执行层)
#
# 职责: 注入前快照落盘 → 按 46→40→51 顺序对三份生产 dta 跑 {key}_apply_notes_master.do
#       (master 内: use → labels.do → notes 子卷 → save, replace → exit, clear)
#       → 扫 log r(###) → NOTES_APPLIED_PARTxx 计数对账 → sidecar 逐 dta 键局部更新。
# 铁律 (CLAUDE.md): 一律 /b 批处理; Start-Process -Wait 配超时 + Stop-Process 清理护栏
#       (probe 实弹: exit, clear 后进程滞留个案); 退出码不可信 → 以 log r(###) 为准。
# 前置: stage 46 已生成 apply_notes_manifest.json + 子卷 + master (write_notes_do_file);
#       不进 pipeline 主线 (依赖本机 Stata, CI 无)。失败 dta 直接重放本脚本即可 (幂等)。

param(
    [string]$DataDir = (Join-Path $PSScriptRoot '..\data\processed'),
    [string]$RepoRoot = (Join-Path $PSScriptRoot '..\..'),
    [string]$StataExe = 'C:\Program Files\StataNow19\StataMP-64.exe',
    [string]$Python = 'F:\Anaconda3\python.exe',
    [int]$TimeoutSec = 1800
)

$ErrorActionPreference = 'Stop'
$DataDir = (Resolve-Path $DataDir).Path
$RepoRoot = (Resolve-Path $RepoRoot).Path
$Helper = 'news_process.scripts.apply_stata_notes_helper'

function Invoke-Helper {
    param([string[]]$HelperArgs)
    Push-Location $RepoRoot
    try {
        $out = & $Python -m $Helper @HelperArgs
        if ($LASTEXITCODE -ne 0) { throw "helper failed (exit=$LASTEXITCODE): $($HelperArgs -join ' ')" }
        return $out
    } finally { Pop-Location }
}

function Invoke-StataBatch {
    # /b 批处理; 完成判定 = 轮询 log 行首 NOTES_MASTER_DONE= 标记, 超时护栏保留为失败路径。
    # K7 (2026-07-16 实弹 3/3): exit, clear 后 Stata 进程可系统性滞留为僵尸 — 旧实现
    # Wait-Process 等进程退出, 会把已成功的注入 (save+display 均完成) 误判为超时失败并
    # 连坐删 sidecar 键 (假阴性)。改为: 见 DONE → 数据已安全 → 60s 干净退出宽限 →
    # 仍滞留按僵尸击杀 (07-15 shareholderw / 07-16 三 master 同款先例), 判成功。
    param([string]$DoFile)
    $logPath = Join-Path $DataDir ([System.IO.Path]::GetFileNameWithoutExtension($DoFile) + '.log')
    if (Test-Path $logPath) { Remove-Item $logPath -Force -Confirm:$false }
    $p = Start-Process -FilePath $StataExe -ArgumentList '/b', 'do', ('"' + $DoFile + '"') `
        -WorkingDirectory $DataDir -PassThru
    $null = $p.Handle   # 先取 Handle, 防 HasExited/ExitCode 不可用 (07-14 教训)
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $sawDone = $false
    while ((Get-Date) -lt $deadline) {
        if (Test-Path $logPath) {
            # -Tail 50: DONE 现居倒数第 3 行, 加宽窗口防未来 master 收尾输出增行把标记挤出
            # 窗口 (RR2 NIT-1); 即便挤出, 进程退出分支仍有全文 doneMark 补判兜底 (fail-safe)。
            $tail = Get-Content $logPath -Tail 50 -ErrorAction SilentlyContinue
            if ($tail -match '^NOTES_MASTER_DONE=') { $sawDone = $true; break }
        }
        if ($p.HasExited) { Start-Sleep -Seconds 2; break }
        Start-Sleep -Seconds 10
    }
    if ($sawDone -and -not $p.HasExited) {
        $null = $p.WaitForExit(60000)
        if (-not $p.HasExited) {
            Write-Warning "DONE 已见但进程滞留 — 按僵尸击杀 (数据已安全): $DoFile"
            Stop-Process -Id $p.Id -Force -Confirm:$false
        }
    } elseif ((-not $sawDone) -and (-not $p.HasExited)) {
        Write-Warning "TIMEOUT (${TimeoutSec}s, 无 DONE 标记): $DoFile — Stop-Process 清理, 视为失败"
        Stop-Process -Id $p.Id -Force -Confirm:$false
        return $null
    }
    if (-not (Test-Path $logPath)) {
        Write-Warning "log 缺失: $logPath — Stata 未产出日志, 视为失败"
        return $null
    }
    $log = Get-Content $logPath -Raw -Encoding UTF8
    # 退出码不可信 → 扫 r(###) (行首, 形如 r(601);)
    $rErrs = ($log -split "`r?`n") | Where-Object { $_ -match '^r\(\d+\)' }
    if ($rErrs) {
        Write-Warning ("Stata r(###) 错误: " + (($rErrs | Select-Object -First 5) -join ' | '))
        return $null
    }
    return $log
}

Write-Host "=== apply_stata_notes: DataDir=$DataDir TimeoutSec=$TimeoutSec ==="

# 0. 前置检查
$manifestPath = Join-Path $DataDir 'apply_notes_manifest.json'
if (-not (Test-Path $manifestPath)) {
    Write-Warning "manifest 不存在: $manifestPath — 先跑 stage 46 生成 notes .do 族"; exit 1
}
if (-not (Test-Path $StataExe)) { Write-Warning "Stata 不存在: $StataExe"; exit 1 }
$manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

# 1. 注入前快照 (§3b: 开头自动落盘; 供 WP5 列数/dtype/var labels 读回全等断言)
Write-Host "[1] 注入前快照 → _notes_preinject_snapshot.json"
Invoke-Helper @('snapshot', '--data-dir', $DataDir, '--out', '_notes_preinject_snapshot.json') | Write-Host

# 2. 注入 46→40→51 (计划 §3b 执行顺序; 逐 dta 独立, 失败不阻断后续但记失败)
$order = @('46', '40', '51')
$failed = @()
foreach ($key in $order) {
    $dtaName = $manifest.dta_targets.$key
    $masterDo = $manifest.masters.$key
    $dtaPath = Join-Path $DataDir $dtaName
    Write-Host "[2] dta=$key ($dtaName): master=$masterDo"
    if (-not (Test-Path $dtaPath)) {
        Write-Warning "  dta 不存在, 跳过并记失败: $dtaPath"
        $failed += $key
        Invoke-Helper @('sidecar-remove', '--data-dir', $DataDir, '--key', $key) | Write-Host
        continue
    }
    if (-not (Test-Path (Join-Path $DataDir $masterDo))) {
        Write-Warning "  master .do 不存在, 跳过并记失败: $masterDo"
        $failed += $key
        Invoke-Helper @('sidecar-remove', '--data-dir', $DataDir, '--key', $key) | Write-Host
        continue
    }
    $log = Invoke-StataBatch -DoFile $masterDo
    $ok = $false
    if ($null -ne $log) {
        # 对账: sum(NOTES_APPLIED_PARTxx) == 期望数 (= dta 实际列 ∩ manifest 短名集)
        # P2 整改 (2026-07-11): (?m)^ 行首锚定 — display 输出恒在行首, 命令回显
        # '. ' 前缀 / 折行 '> ' 续行不在行首; 与生成端 _stata_notes_text 的 marker
        # 全角中和 (正文 '='→＝) 构成双保险 (镜像 stata_export._NOTES_APPLIED_LOG_RE)。
        $counts = @{}
        foreach ($m in [regex]::Matches($log, '(?m)^NOTES_APPLIED_PART(\d+)=(\d+)\s*$')) {
            $counts[[int]$m.Groups[1].Value] = [int]$m.Groups[2].Value  # 后写覆盖 (取最新)
        }
        $applied = 0; foreach ($v in $counts.Values) { $applied += $v }
        $expected = [int]((Invoke-Helper @('expected', '--data-dir', $DataDir, '--dta', $dtaName)) | Select-Object -Last 1)
        $doneMark = $log -match ('(?m)^NOTES_MASTER_DONE=' + $key + '\s*$')
        Write-Host "  对账: applied=$applied expected=$expected parts=$($counts.Count) master_done=$doneMark"
        if ($doneMark -and $counts.Count -gt 0 -and $applied -eq $expected) { $ok = $true }
        else { Write-Warning "  对账不等或 master 未走到收尾 display — 视为失败" }
    }
    if ($ok) {
        Invoke-Helper @('sidecar-update', '--data-dir', $DataDir, '--key', $key, '--n-applied', "$applied") | Write-Host
        Write-Host "  [OK] dta=$key notes 注入 + sidecar 更新完成"
    } else {
        $failed += $key
        Invoke-Helper @('sidecar-remove', '--data-dir', $DataDir, '--key', $key) | Write-Host
        Write-Warning "  [FAIL] dta=$key — sidecar 键已移除 (doctor [7/7] 将 loud WARN); 修复后重放本脚本即可 (幂等)"
    }
}

# 3. 注入后快照 (供 WP5 对比便利; 40/51 var labels 会被 labels.do 统一, 属预期变更)
Write-Host "[3] 注入后快照 → _notes_postinject_snapshot.json"
Invoke-Helper @('snapshot', '--data-dir', $DataDir, '--out', '_notes_postinject_snapshot.json') | Write-Host

if ($failed.Count -gt 0) {
    Write-Warning ("注入失败 dta: " + ($failed -join ', '))
    exit 1
}
Write-Host "=== 全部三 dta notes 注入 + 对账 + sidecar 完成 ==="
exit 0
