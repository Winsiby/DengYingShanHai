[CmdletBinding()]
param(
    [ValidateSet('Auto', 'Package', 'EditorGame')][string]$Mode = 'Auto',
    [ValidatePattern('^Run[1-9][0-9]*$')][string]$Run,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$taskAlias = 'C:\UEProjects\DengYingShanHai'
$taskActual = 'D:\灯影山海'
$taskMap = '/Game/DengYingShanHai/Dev/ThreeAct/Maps/LV_ThreeActDev'
$taskPackageRoot = Join-Path $taskActual 'Builds\ThreeActDev-20261009-Run3\Windows'
$taskBuildIdentity = Join-Path $taskPackageRoot 'THREE-ACT-DEV-BUILD.json'
$taskInnerExe = Join-Path $taskPackageRoot 'DengYingShanHai\Binaries\Win64\DengYingShanHai.exe'
$taskEditor = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskAudit = Join-Path $taskAlias 'Saved\Audit-2026-10-09-ThreeActPlay'
$taskReportPath = $null
$taskReport = $null
$taskProcess = $null

try {
    $taskJunction = Get-Item -LiteralPath $taskAlias
    if ($taskJunction.LinkType -ne 'Junction' -or [string](@($taskJunction.Target)[0]) -ne $taskActual) {
        throw '工程快捷路径不是当前 D 盘工程。请检查 C:\UEProjects\DengYingShanHai 的指向。'
    }
    $taskInvocationRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    if ($taskInvocationRoot -ne $taskActual -and $taskInvocationRoot -ne $taskAlias) {
        throw '请从 D:\灯影山海 中打开本入口；不要运行其他位置的副本。'
    }

    # A build identity is written only after the dedicated three-act cook/archive succeeds.
    # An old M3 package, an arbitrary newest directory, or bootstrap alone is never selected.
    $taskPackageReason = '独立三幕 Development 包尚未准备完成。'
    $taskPackageReady = $false
    if (Test-Path -LiteralPath $taskBuildIdentity -PathType Leaf) {
        try {
            $taskIdentity = Get-Content -LiteralPath $taskBuildIdentity -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($taskIdentity.Succeeded -ne $true -or $taskIdentity.Map -ne $taskMap -or
                $taskIdentity.ArchiveRoot -ne $taskPackageRoot -or $taskIdentity.Configuration -ne 'Development' -or
                $taskIdentity.Platform -ne 'Win64') {
                throw '独立包的身份记录与当前三幕地图或 Development/Win64 目标不符。'
            }
            $taskRequiredPackage = @(
                (Join-Path $taskPackageRoot 'DengYingShanHai.exe'),
                $taskInnerExe,
                (Join-Path $taskPackageRoot 'Manifest_UFSFiles_Win64.txt'),
                (Join-Path $taskPackageRoot 'Manifest_NonUFSFiles_Win64.txt'),
                (Join-Path $taskPackageRoot 'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.pak'),
                (Join-Path $taskPackageRoot 'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.utoc'),
                (Join-Path $taskPackageRoot 'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.ucas'),
                (Join-Path $taskPackageRoot 'DengYingShanHai\Content\Paks\global.utoc'),
                (Join-Path $taskPackageRoot 'DengYingShanHai\Content\Paks\global.ucas')
            )
            foreach ($taskPath in $taskRequiredPackage) {
                if (-not (Test-Path -LiteralPath $taskPath -PathType Leaf) -or (Get-Item -LiteralPath $taskPath).Length -le 0) {
                    throw ('独立三幕包缺少文件：' + $taskPath)
                }
            }
            if ($taskIdentity.NativeExeSHA256 -and
                (Get-FileHash -Algorithm SHA256 -LiteralPath $taskInnerExe).Hash -ne $taskIdentity.NativeExeSHA256) {
                throw '独立三幕包的运行文件与打包身份记录不一致。'
            }
            $taskPackageReady = $true
        } catch {
            $taskPackageReason = $_.Exception.Message
        }
    }
    if ($Mode -eq 'Package' -and -not $taskPackageReady) { throw $taskPackageReason }
    $taskSelectedMode = if ($Mode -eq 'EditorGame' -or ($Mode -eq 'Auto' -and -not $taskPackageReady)) { 'EditorGame' } else { 'Package' }
    $taskProject = Join-Path $taskAlias 'DengYingShanHai.uproject'
    if ($taskSelectedMode -eq 'EditorGame') {
        foreach ($taskPath in @($taskEditor, $taskProject,
            (Join-Path $taskAlias 'Binaries\Win64\UnrealEditor-DengYingShanHai.dll'),
            (Join-Path $taskAlias 'Content\DengYingShanHai\Dev\ThreeAct\Maps\LV_ThreeActDev.umap'))) {
            if (-not (Test-Path -LiteralPath $taskPath -PathType Leaf)) {
                throw ('三幕测试入口尚未准备完成，缺少：' + $taskPath)
            }
        }
    }

    if (-not $Run) {
        $taskNumber = 1
        while ((Test-Path -LiteralPath (Join-Path $taskAudit ('Launch-Run' + $taskNumber + '.json'))) -or
            (Test-Path -LiteralPath (Join-Path $taskAudit ('Session-Run' + $taskNumber + '.log')))) { $taskNumber++ }
        $Run = 'Run' + $taskNumber
    }
    $taskReportPath = Join-Path $taskAudit ('Launch-' + $Run + '.json')
    $taskLog = Join-Path $taskAudit ('Session-' + $Run + '.log')
    if ((Test-Path -LiteralPath $taskReportPath) -or (Test-Path -LiteralPath $taskLog)) {
        throw '这个运行编号已有记录，已保留原记录。请省略 -Run 参数或选择新编号。'
    }
    $taskExecutable = if ($taskSelectedMode -eq 'Package') { $taskInnerExe } else { $taskEditor }
    $taskArguments = @($taskMap, '-windowed', '-ResX=1280', '-ResY=800', '-nosplash',
        ('-abslog="' + $taskLog + '"'), '-ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"')
    if ($taskSelectedMode -eq 'EditorGame') {
        $taskArguments = @(('"' + $taskProject + '"'), $taskMap, '-game') + @($taskArguments | Select-Object -Skip 1)
    }
    $taskReport = [ordered]@{
        RequestedMode = $Mode; SelectedMode = $taskSelectedMode; Run = $Run
        Map = $taskMap; Executable = $taskExecutable; Arguments = $taskArguments
        PackageRoot = $taskPackageRoot; BuildIdentity = $taskBuildIdentity
        AutoFallbackReason = $(if ($Mode -eq 'Auto' -and -not $taskPackageReady) { $taskPackageReason } else { $null })
        WindowStyle = 'Normal'; WindowWidth = 1280; WindowHeight = 800
        ProcessId = $null; ActualProcessExitCode = $null; Status = 'PreflightOnly'
        StartedUtc = $null; ExitedUtc = $null; Log = $taskLog
        FirstFrameVerified = $false; GameplayVerified = $false; PythonExecuted = $false
        ProductDataChanged = $false; OtherProcessesTerminated = $false
    }
    if ($DryRun) { $taskReport | ConvertTo-Json -Depth 5; exit 0 }

    $taskLiveUE = @(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai -ErrorAction SilentlyContinue)
    if ($taskLiveUE.Count -gt 0) {
        throw '检测到已打开的 UE 或灯影山海窗口。请先正常关闭它们再打开本入口；没有终止任何进程。'
    }
    New-Item -ItemType Directory -Path $taskAudit -Force | Out-Null
    if ($taskSelectedMode -eq 'EditorGame') {
        if ($Mode -eq 'Auto') { Write-Host ($taskPackageReason + ' 本次明确使用本机 UE 的独立游戏窗口。') -ForegroundColor Yellow }
        else { Write-Host '本次使用本机 UE 的独立游戏窗口；不是打包版本验收。' }
    } else { Write-Host '本次打开独立三幕 Development 打包版本。' }
    Write-Host '正在打开游戏，请等待实际画面出现。若没有取得焦点，请点击游戏窗口。'
    Write-Host '沿用 E 操纵/放开、A/D 调整、R 复位；整段重演暂请正常关闭后重新打开本入口。'
    Write-Host ('本次记录：' + $taskReportPath)
    $taskProcess = Start-Process -FilePath $taskExecutable -ArgumentList $taskArguments -WindowStyle Normal -PassThru
    $taskReport.ProcessId = $taskProcess.Id
    $taskReport.StartedUtc = [DateTime]::UtcNow.ToString('o')
    $taskReport.Status = 'ProcessStarted'
    $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8
    Write-Host '已创建游戏进程；这不代表首帧或三幕玩法已经通过验收。请正常关闭游戏结束本次运行。'
    $taskProcess.WaitForExit()
    $taskProcess.Refresh()
    $taskReport.ActualProcessExitCode = $taskProcess.ExitCode
    $taskReport.ExitedUtc = [DateTime]::UtcNow.ToString('o')
    $taskReport.Status = 'ProcessExited'
    $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8
    if ($taskProcess.ExitCode -ne 0) { Write-Host ('游戏异常退出，请保留本次记录与日志：' + $taskLog) -ForegroundColor Red }
    else { Write-Host '游戏已正常退出，本次启动记录已保留。' }
    exit $taskProcess.ExitCode
} catch {
    Write-Host ('无法完成本次启动：' + $_.Exception.Message) -ForegroundColor Red
    if ($null -ne $taskProcess) { Write-Host '本轮已创建的游戏进程保留，请正常关闭；没有强行终止任何窗口。' }
    else { Write-Host '没有启动游戏。' }
    if ($null -ne $taskReport) {
        $taskReport.Status = 'LauncherError'
        $taskReport.Error = $_.Exception.Message
        if (Test-Path -LiteralPath $taskAudit -PathType Container) {
            try { $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8 }
            catch { Write-Host '启动记录无法保存，请保留窗口中的错误信息。' }
        }
    }
    exit 1
}
