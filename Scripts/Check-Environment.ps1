[CmdletBinding()]
param(
    [string]$EngineRoot = "",
    [string]$ProjectRoot = "",
    [switch]$Json
)

$ErrorActionPreference = "SilentlyContinue"
$PreferredEngineVersion = "5.8"
$checks = [System.Collections.Generic.List[object]]::new()

function Add-Check {
    param(
        [string]$Name,
        [ValidateSet("PASS", "WARN", "FAIL")]
        [string]$Status,
        [string]$Details,
        [bool]$Required = $false
    )

    $checks.Add([pscustomobject]@{
        Name = $Name
        Status = $Status
        Required = $Required
        Details = $Details
    })
}

function Find-UnrealEngineRoot {
    param([string]$RequestedRoot)

    $candidates = [System.Collections.Generic.List[string]]::new()
    if ($RequestedRoot) { $candidates.Add($RequestedRoot) }
    if ($env:DY_UE_ROOT) { $candidates.Add($env:DY_UE_ROOT) }
    $persistedEngineRoot = [Environment]::GetEnvironmentVariable("DY_UE_ROOT", "User")
    if ($persistedEngineRoot) { $candidates.Add($persistedEngineRoot) }
    if ($env:UE_ROOT) { $candidates.Add($env:UE_ROOT) }

    foreach ($candidate in @(
        "D:\Epic Games\UE_$PreferredEngineVersion",
        "C:\Program Files\Epic Games\UE_$PreferredEngineVersion",
        "C:\Epic Games\UE_$PreferredEngineVersion"
    )) {
        $candidates.Add($candidate)
    }

    $manifestRoot = "C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests"
    if (Test-Path -LiteralPath $manifestRoot) {
        foreach ($manifest in Get-ChildItem -LiteralPath $manifestRoot -Filter "*.item" -File) {
            try {
                $item = Get-Content -LiteralPath $manifest.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($item.InstallLocation -and (($item.AppName -like "UE_$PreferredEngineVersion*") -or ($item.DisplayName -like "Unreal Engine $PreferredEngineVersion*"))) {
                    $candidates.Add([string]$item.InstallLocation)
                }
            } catch {
                continue
            }
        }
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (-not $candidate) { continue }
        $editor = Join-Path $candidate "Engine\Binaries\Win64\UnrealEditor.exe"
        if (Test-Path -LiteralPath $editor -PathType Leaf) {
            return [System.IO.Path]::GetFullPath($candidate)
        }
    }

    return $null
}

$os = Get-CimInstance Win32_OperatingSystem
if ($os -and [int]$os.BuildNumber -ge 19045) {
    Add-Check "Windows" "PASS" "$($os.Caption), build $($os.BuildNumber)" $true
} else {
    Add-Check "Windows" "FAIL" "Windows 10 22H2 or Windows 11 is required." $true
}

$ramGB = if ($os) { [math]::Round($os.TotalVisibleMemorySize / 1MB, 1) } else { 0 }
if ($ramGB -ge 31) {
    Add-Check "Memory" "PASS" "$ramGB GB RAM" $true
} elseif ($ramGB -ge 16) {
    Add-Check "Memory" "WARN" "$ramGB GB RAM; 32 GB is recommended for UE5." $true
} else {
    Add-Check "Memory" "FAIL" "$ramGB GB RAM; at least 16 GB is required for this project." $true
}

$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
if ($cpu) {
    Add-Check "CPU" "PASS" "$($cpu.Name.Trim()); $($cpu.NumberOfCores) cores / $($cpu.NumberOfLogicalProcessors) logical processors"
}

$nvidiaSmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if (-not $nvidiaSmi -and (Test-Path -LiteralPath "C:\Windows\System32\nvidia-smi.exe")) {
    $nvidiaSmi = Get-Item -LiteralPath "C:\Windows\System32\nvidia-smi.exe"
}
if ($nvidiaSmi) {
    $gpu = & $nvidiaSmi.Source --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>$null | Select-Object -First 1
    Add-Check "GPU" "PASS" $gpu $true
} else {
    $gpu = Get-CimInstance Win32_VideoController | Sort-Object AdapterRAM -Descending | Select-Object -First 1
    if ($gpu) {
        Add-Check "GPU" "WARN" "$($gpu.Name); verify DirectX 12 support and current drivers manually." $true
    } else {
        Add-Check "GPU" "FAIL" "No graphics adapter was detected." $true
    }
}

$projectDrive = (Get-Item -LiteralPath $PSScriptRoot).PSDrive
if ($projectDrive -and $projectDrive.Free -ge 40GB) {
    Add-Check "Project disk" "PASS" "$($projectDrive.Name): $([math]::Round($projectDrive.Free / 1GB, 1)) GB free"
} elseif ($projectDrive) {
    Add-Check "Project disk" "WARN" "$($projectDrive.Name): only $([math]::Round($projectDrive.Free / 1GB, 1)) GB free"
}

$repositoryRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$preferredProjectRoot = "C:\UEProjects\DengYingShanHai"
if (-not $ProjectRoot) {
    $persistedProjectRoot = [Environment]::GetEnvironmentVariable("DY_PROJECT_ROOT", "User")
    if ($env:DY_PROJECT_ROOT -and (Test-Path -LiteralPath $env:DY_PROJECT_ROOT -PathType Container)) {
        $ProjectRoot = $env:DY_PROJECT_ROOT
    } elseif ($persistedProjectRoot -and (Test-Path -LiteralPath $persistedProjectRoot -PathType Container)) {
        $ProjectRoot = $persistedProjectRoot
    } elseif (Test-Path -LiteralPath $preferredProjectRoot -PathType Container) {
        $ProjectRoot = $preferredProjectRoot
    } else {
        $ProjectRoot = $repositoryRoot
    }
}
$resolvedProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$pathHasSpace = $resolvedProjectRoot.Contains(" ")
$pathHasNonAscii = $resolvedProjectRoot -match "[^\x00-\x7F]"
if (-not $pathHasSpace -and -not $pathHasNonAscii -and (Test-Path -LiteralPath $resolvedProjectRoot -PathType Container)) {
    $projectPathDetails = $resolvedProjectRoot
    $projectPathItem = Get-Item -LiteralPath $resolvedProjectRoot -Force
    if ($projectPathItem.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        $projectPathDetails += " -> $($projectPathItem.Target -join ';')"
    }
    Add-Check "ASCII project path" "PASS" $projectPathDetails $true
} else {
    Add-Check "ASCII project path" "FAIL" "Use C:\UEProjects\DengYingShanHai. UE/MSVC compilation failed when invoked through the repository's Chinese path." $true
}

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    $gitVersion = (& git --version 2>$null)
    Add-Check "Git" "PASS" $gitVersion $true
} else {
    Add-Check "Git" "FAIL" "Git is not available on PATH." $true
}

$lfsOutput = & git lfs version 2>$null
if ($LASTEXITCODE -eq 0) {
    Add-Check "Git LFS" "PASS" $lfsOutput $true
} else {
    Add-Check "Git LFS" "FAIL" "Git LFS is required for .uasset and .umap files." $true
}

$vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path -LiteralPath $vswhere) {
    $vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if ($vsPath) {
        $vsVersion = & $vswhere -latest -products * -property catalog_productDisplayVersion
        Add-Check "Visual Studio" "PASS" "Visual Studio $vsVersion at $vsPath" $true

        $msvcRoot = Join-Path $vsPath "VC\Tools\MSVC"
        $msvcToolset = Get-ChildItem -LiteralPath $msvcRoot -Directory |
            Sort-Object { [version]$_.Name } -Descending |
            Select-Object -First 1
        if ($msvcToolset) {
            $msvcVersion = [version]$msvcToolset.Name
            if ($msvcVersion.Major -eq 14 -and $msvcVersion.Minor -eq 50) {
                Add-Check "MSVC toolset" "PASS" "$($msvcToolset.Name) at $($msvcToolset.FullName) (UE 5.8 preferred family)"
            } elseif ($msvcVersion -gt [version]"14.50") {
                Add-Check "MSVC toolset" "WARN" "$($msvcToolset.Name) at $($msvcToolset.FullName); UE 5.8.3 currently builds successfully but UnrealBuildTool prefers 14.50.35717."
            } else {
                Add-Check "MSVC toolset" "FAIL" "$($msvcToolset.Name) is older than the UE 5.8 project baseline." $true
            }
        } else {
            Add-Check "MSVC toolset" "FAIL" "No MSVC toolset directory was found under $msvcRoot." $true
        }
    } else {
        Add-Check "Visual Studio" "FAIL" "Visual Studio C++ tools were not found." $true
    }

    foreach ($component in @(
        "Microsoft.VisualStudio.Workload.NativeGame",
        "Microsoft.VisualStudio.Component.Windows11SDK.26100",
        "Component.Unreal.Debugger",
        "Component.Unreal.Ide",
        "Microsoft.VisualStudio.Component.Unreal.TestAdapter"
    )) {
        $found = & $vswhere -latest -products * -requires $component -property installationPath
        if ($found) {
            Add-Check $component "PASS" "Installed"
        } else {
            Add-Check $component "FAIL" "Missing Visual Studio component" $true
        }
    }
} else {
    Add-Check "Visual Studio" "FAIL" "Visual Studio Installer / vswhere was not found." $true
}

$launcher = @(
    "C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe",
    "C:\Program Files\Epic Games\Launcher\Portal\Binaries\Win64\EpicGamesLauncher.exe"
) | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1
if ($launcher) {
    Add-Check "Epic Games Launcher" "PASS" $launcher $true
} else {
    Add-Check "Epic Games Launcher" "FAIL" "Epic Games Launcher is not installed." $true
}

$resolvedEngineRoot = Find-UnrealEngineRoot -RequestedRoot $EngineRoot
if ($resolvedEngineRoot) {
    $editor = Join-Path $resolvedEngineRoot "Engine\Binaries\Win64\UnrealEditor.exe"
    $uat = Join-Path $resolvedEngineRoot "Engine\Build\BatchFiles\RunUAT.bat"
    $build = Join-Path $resolvedEngineRoot "Engine\Build\BatchFiles\Build.bat"
    if ((Test-Path -LiteralPath $editor) -and (Test-Path -LiteralPath $uat) -and (Test-Path -LiteralPath $build)) {
        $buildVersionFile = Join-Path $resolvedEngineRoot "Engine\Build\Build.version"
        $versionText = $PreferredEngineVersion
        if (Test-Path -LiteralPath $buildVersionFile) {
            try {
                $buildVersion = Get-Content -LiteralPath $buildVersionFile -Raw -Encoding UTF8 | ConvertFrom-Json
                $versionText = "$($buildVersion.MajorVersion).$($buildVersion.MinorVersion).$($buildVersion.PatchVersion) CL $($buildVersion.Changelist)"
            } catch {
                $versionText = "$PreferredEngineVersion (Build.version unreadable)"
            }
        }
        Add-Check "Unreal Engine $PreferredEngineVersion" "PASS" "$versionText at $resolvedEngineRoot" $true
    } else {
        Add-Check "Unreal Engine $PreferredEngineVersion" "FAIL" "Engine root is incomplete: $resolvedEngineRoot" $true
    }
} else {
    Add-Check "Unreal Engine $PreferredEngineVersion" "FAIL" "Install the stable binary build through Epic Games Launcher, preferably at D:\Epic Games\UE_$PreferredEngineVersion." $true
}

if ($Json) {
    $checks | ConvertTo-Json -Depth 4
} else {
    $checks | Format-Table Status, Required, Name, Details -AutoSize -Wrap
    $requiredFailures = @($checks | Where-Object { $_.Required -and $_.Status -eq "FAIL" })
    $warnings = @($checks | Where-Object { $_.Status -eq "WARN" })
    ""
    "Required failures: $($requiredFailures.Count); warnings: $($warnings.Count)"
}

$requiredFailureCount = @($checks | Where-Object { $_.Required -and $_.Status -eq "FAIL" }).Count
if ($requiredFailureCount -gt 0) { exit 1 }
exit 0
