[CmdletBinding()]
param(
    [ValidateSet('Auto', 'Package', 'EditorGame')][string]$Mode = 'Auto',
    [ValidatePattern('^Run[1-9][0-9]*$')][string]$Run,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$taskAlias = 'C:\UEProjects\DengYingShanHai'
$taskActual = 'D:\灯影山海'
$taskMap = '/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab'
$taskPackageRoot = Join-Path $taskActual 'Builds\AudioDev-20261010-Run3\Windows'
$taskBuildIdentity = Join-Path $taskPackageRoot 'AUDIO-DEV-BUILD.json'
$taskInnerExe = Join-Path $taskPackageRoot 'DengYingShanHai\Binaries\Win64\DengYingShanHai.exe'
$taskEditor = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$taskAudit = Join-Path $taskAlias 'Saved\Audit-2026-10-10-FootstepSyncPlay'
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
    # Select one immutable entry-loop build; never select an arbitrary newest/older build.
    $taskPackageReason = '人物脚步与空剧院混响 Development 包尚未准备完成。'
    $taskPackageReady = $false
    if (Test-Path -LiteralPath $taskBuildIdentity -PathType Leaf) {
        try {
            $taskIdentity = Get-Content -LiteralPath $taskBuildIdentity -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($taskIdentity.Succeeded -ne $true -or $taskIdentity.Map -ne $taskMap -or
                $taskIdentity.ArchiveRoot -ne $taskPackageRoot -or $taskIdentity.Configuration -ne 'Development' -or
                $taskIdentity.Platform -ne 'Win64' -or $taskIdentity.NativeExeSHA256 -notmatch '^[A-Fa-f0-9]{64}$') {
                throw '独立包身份与当前闭环地图、目标或文件校验记录不符。'
            }
            foreach ($taskRelative in @('DengYingShanHai.exe', 'DengYingShanHai\Binaries\Win64\DengYingShanHai.exe',
                'Manifest_UFSFiles_Win64.txt', 'Manifest_NonUFSFiles_Win64.txt',
                'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.pak',
                'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.utoc',
                'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.ucas',
                'DengYingShanHai\Content\Paks\global.utoc', 'DengYingShanHai\Content\Paks\global.ucas')) {
                $taskPath = Join-Path $taskPackageRoot $taskRelative
                if (-not (Test-Path -LiteralPath $taskPath -PathType Leaf) -or (Get-Item -LiteralPath $taskPath).Length -le 0) {
                    throw ('独立闭环包缺少文件：'+$taskPath)
                }
            }
            if ((Get-FileHash -Algorithm SHA256 -LiteralPath $taskInnerExe).Hash -ne $taskIdentity.NativeExeSHA256) {
                throw '独立闭环包的运行文件与打包记录不一致。'
            }
            $taskPackageReady = $true
        } catch { $taskPackageReason = $_.Exception.Message }
    }
    if ($Mode -eq 'Package' -and -not $taskPackageReady) { throw $taskPackageReason }
    $taskSelectedMode = if ($Mode -eq 'EditorGame' -or ($Mode -eq 'Auto' -and -not $taskPackageReady)) { 'EditorGame' } else { 'Package' }
    $taskProject = Join-Path $taskAlias 'DengYingShanHai.uproject'
    if ($taskSelectedMode -eq 'EditorGame') {
        foreach ($taskPath in @($taskEditor, $taskProject,
            (Join-Path $taskAlias 'Binaries\Win64\UnrealEditor-DengYingShanHai.dll'),
            (Join-Path $taskAlias 'Content\DengYingShanHai\Dev\AlignmentFeedback\Maps\LV_AlignmentFeedbackLab.umap'))) {
            if (-not (Test-Path -LiteralPath $taskPath -PathType Leaf)) { throw ('闭环测试入口缺少：'+$taskPath) }
        }
    }
    if (-not $Run) {
        $taskNumber = 1
        while ((Test-Path -LiteralPath (Join-Path $taskAudit ('Launch-Run'+$taskNumber+'.json'))) -or
            (Test-Path -LiteralPath (Join-Path $taskAudit ('Session-Run'+$taskNumber+'.log')))) { $taskNumber++ }
        $Run = 'Run'+$taskNumber
    }
    $taskReportPath = Join-Path $taskAudit ('Launch-'+$Run+'.json')
    $taskLog = Join-Path $taskAudit ('Session-'+$Run+'.log')
    if ((Test-Path -LiteralPath $taskReportPath) -or (Test-Path -LiteralPath $taskLog)) {
        throw '运行编号已有记录，已保留。请省略 -Run 或选择新编号。'
    }
    $taskExecutable = if ($taskSelectedMode -eq 'Package') { $taskInnerExe } else { $taskEditor }
    $taskArguments = @($taskMap, '-windowed', '-ResX=1280', '-ResY=800', '-nosplash',
        ('-abslog="'+$taskLog+'"'), '-ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"')
    if ($taskSelectedMode -eq 'EditorGame') {
        $taskArguments = @(('"'+$taskProject+'"'), $taskMap, '-game')+@($taskArguments | Select-Object -Skip 1)
    }
    $taskReport = [ordered]@{
        RequestedMode=$Mode; SelectedMode=$taskSelectedMode; Run=$Run; Map=$taskMap
        Executable=$taskExecutable; Arguments=$taskArguments; PackageRoot=$taskPackageRoot; BuildIdentity=$taskBuildIdentity
        AutoFallbackReason=$(if ($Mode -eq 'Auto' -and -not $taskPackageReady) { $taskPackageReason } else { $null })
        WindowStyle='Normal'; WindowWidth=1280; WindowHeight=800
        ProcessId=$null; ActualProcessExitCode=$null; Status='PreflightOnly'; StartedUtc=$null; ExitedUtc=$null; Log=$taskLog
        FirstFrameVerified=$false; GameplayVerified=$false; PythonExecuted=$false
        ProductDataChanged=$false; OtherProcessesTerminated=$false
    }
    if ($DryRun) { $taskReport | ConvertTo-Json -Depth 5; exit 0 }
    if (@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai -ErrorAction SilentlyContinue).Count -gt 0) {
        throw '已有 UE 或灯影山海窗口。请先正常关闭再打开本入口；没有终止任何进程。'
    }
    New-Item -ItemType Directory -Path $taskAudit -Force | Out-Null
    if ($taskSelectedMode -eq 'EditorGame') { Write-Host ($taskPackageReason+' 本次明确使用本机 UE 独立游戏窗口，不是打包验收。') }
    else { Write-Host '正在打开脚步与空剧院混响 Dev 版（AudioDev Run3，脚步同步修复）；第二幕身形角标、灯速 75% 和灯偶就位反馈保持不变。' }
    Write-Host '请等待开始界面，点击“开始复演”；之后沿用 E 操纵/放开、A/D 调整、R 复位。'
    Write-Host '真实成林后可点击“重新复演”，重载本场回到开始界面。请正常关闭游戏结束本次运行。'
    Write-Host '开始复演后，W/A/S/D 真实起步与停步同步，后续按位移交替脚步并保留大厅尾音；站住、挡墙、操纵灯偶不连续发脚步。'
    Write-Host '风声、保持节奏、成功木击、杖尖接触和成林枝叶均有声；不是正式锣鼓或吟唱。'
    Write-Host '若无任何声音，请先确认 Windows 扬声器没有静音、主音量不是 0。此入口不修改系统音量。'
    Write-Host ('本次记录：'+$taskReportPath)
    $taskProcess = Start-Process -FilePath $taskExecutable -ArgumentList $taskArguments -WindowStyle Normal -PassThru
    $taskReport.ProcessId = $taskProcess.Id
    $taskReport.StartedUtc = [DateTime]::UtcNow.ToString('o')
    $taskReport.Status = 'ProcessStarted'
    $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8
    $taskProcess.WaitForExit()
    $taskProcess.Refresh()
    $taskReport.ActualProcessExitCode = $taskProcess.ExitCode
    $taskReport.ExitedUtc = [DateTime]::UtcNow.ToString('o')
    $taskReport.Status = 'ProcessExited'
    $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8
    if ($taskProcess.ExitCode -ne 0) { Write-Host ('游戏异常退出，请保留记录与日志：'+$taskLog) -ForegroundColor Red }
    else { Write-Host '游戏已正常退出，本次记录已保留。' }
    exit $taskProcess.ExitCode
} catch {
    Write-Host ('无法启动：'+$_.Exception.Message) -ForegroundColor Red
    if ($null -ne $taskProcess) { Write-Host '已创建的游戏进程保留，请正常关闭；没有强行终止窗口。' }
    else { Write-Host '没有启动游戏。' }
    if ($null -ne $taskReport -and (Test-Path -LiteralPath $taskAudit -PathType Container)) {
        $taskReport.Status = 'LauncherError'
        $taskReport.Error = $_.Exception.Message
        try { $taskReport | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $taskReportPath -Encoding UTF8 }
        catch { Write-Host '记录无法保存，请保留窗口错误信息。' }
    }
    exit 1
}
