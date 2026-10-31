<#
.SYNOPSIS
    显式启动《灯影山海》M2 Dev 切片地图，不修改全局默认地图。

.DESCRIPTION
    本脚本以 -game 独立运行方式启动 M2 地图（不是编辑器 PIE）：
    /Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab

    它不会修改 Config/DefaultEngine.ini 的GameDefaultMap 或 EditorStartupMap，
    也不会修改任何 .uasset、出生朝向或交互半径。项目的全局默认地图保持为 M1 的
    LV_InteractionLab，由监督者决定何时切换。

    启动方式为 -game 独立运行（不是编辑器 PIE）。画面中心即为瞄准点：
    准星变绿表示当前可交互，按 E 进入操纵，A / D 调整，E 释放，R 复位。

.PARAMETER Debug
    传入时附加 -DYDebug，启用聚焦诊断日志（Development-only）。
    诊断只在 HitActor / RejectReason / FocusedActor 变化时输出，不会每帧刷屏。

.PARAMETER Map
    可选。覆盖要打开的地图；默认打开 M2 地图。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\Scripts\Start-M2Lab.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\Scripts\Start-M2Lab.ps1 -Debug
#>
# 注意：此处刻意不使用 [CmdletBinding()]。它会自动注入一个公共参数 -Debug，
# 与本脚本自己的 -Debug 冲突并导致参数元数据错误。
param(
    [switch]$Debug,
    [string]$Map = '/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab',
    [string]$AbsLog = '',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# 必须走英文 junction 路径：中文物理路径会让 MSVC/UHT 错误转码。
$ProjectPath = 'C:\UEProjects\DengYingShanHai\DengYingShanHai.uproject'
$EditorPath = 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'

if ($DryRun) {
    $DryArgs = @("`"$ProjectPath`"", $Map, '-game', '-windowed', '-ResX=1280', '-ResY=720', '-log')
    if ($Debug) { $DryArgs += '-DYDebug' }
    if ($AbsLog) { $DryArgs += "-abslog=`"$AbsLog`"" }
    'DRY RUN - would execute:'
    "`"$EditorPath`" $($DryArgs -join ' ')"
    return
}

if (-not (Test-Path -LiteralPath $ProjectPath)) {
    throw "找不到工程入口：$ProjectPath`n请确认英文 junction C:\UEProjects\DengYingShanHai 仍然有效。"
}

if (-not (Test-Path -LiteralPath $EditorPath)) {
    throw "找不到 UE 5.8 编辑器：$EditorPath`n请先按 Docs/ENVIRONMENT_SETUP.md 安装并验证 UE 5.8。"
}

$Arguments = @(
    "`"$ProjectPath`""
    $Map
    '-game'
    '-windowed'
    '-ResX=1280'
    '-ResY=720'
    '-log'
)

if ($Debug) {
    $Arguments += '-DYDebug'
}

if ($AbsLog) {
    $LogDirectory = Split-Path -Parent $AbsLog
    if ($LogDirectory -and -not (Test-Path -LiteralPath $LogDirectory)) {
        New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null
    }
    $Arguments += "-abslog=`"$AbsLog`""
}

Write-Host '=== 《灯影山海》M2 Dev 切片启动 ===' -ForegroundColor Cyan
Write-Host "工程入口 : $ProjectPath"
Write-Host "地图     : $Map"
Write-Host '运行模式 : -game 独立运行，1280x720 windowed'
Write-Host "调试日志 : $(if ($Debug) { '开启 (-DYDebug)' } else { '关闭' })"
Write-Host "日志文件 : $(if ($AbsLog) { $AbsLog } else { '默认 Saved/Logs/DengYingShanHai.log' })"
Write-Host ''
Write-Host '准星在画面中心：白色=未聚焦，绿色=可交互，按 E 进入操纵。' -ForegroundColor Yellow
Write-Host '若没有反应，请把日志中的 FocusDebug 行交给监督者。'
Write-Host ''

# -WindowStyle 作用于本脚本启动的进程窗口；UE 主窗口已实测正常显示与交互。
Start-Process -FilePath $EditorPath -ArgumentList $Arguments -WindowStyle Hidden
