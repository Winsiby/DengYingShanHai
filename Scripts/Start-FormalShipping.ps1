param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
try {
    $dyRoot = 'D:\灯影山海'
    $dyArchive = Join-Path $dyRoot 'Builds\FormalMain-Shipping-20261023-Run167\Windows'
    $dyAudit = Join-Path $dyRoot 'Saved\Audit-2026-10-23-Performance\Package-Run167'
    $dyIdentityPath = Join-Path $dyArchive 'RELEASE-ENTRY-BUILD.json'
    $dyArtifactsPath = Join-Path $dyAudit 'ARTIFACTS.json'
    $dyMapFile = Join-Path $dyRoot 'Content\DengYingShanHai\Maps\L_DY_Main.umap'
    $dyNativeRelative = 'DengYingShanHai\Binaries\Win64\DengYingShanHai-Win64-Shipping.exe'
    $dyNative = Join-Path $dyArchive $dyNativeRelative
    if (-not (Test-Path -LiteralPath $dyIdentityPath -PathType Leaf)) { throw 'Formal Shipping identity is missing.' }
    if (-not (Test-Path -LiteralPath $dyNative -PathType Leaf)) { throw 'Formal Shipping executable is missing.' }
    $dyIdentity = Get-Content -LiteralPath $dyIdentityPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($dyIdentity.Status -ne 'PASS-BUILD-COOK-STAGE-ARCHIVE' -or
        -not $dyIdentity.Succeeded -or
        $dyIdentity.Map -ne '/Game/DengYingShanHai/Maps/L_DY_Main' -or
        $dyIdentity.Configuration -ne 'Shipping' -or
        $dyIdentity.ArchiveRoot -ine $dyArchive -or
        $dyIdentity.NativeExecutable -ne $dyNativeRelative) {
        throw 'Formal Shipping identity does not match this launcher.'
    }
    $dyNativeHash = (Get-FileHash -LiteralPath $dyNative -Algorithm SHA256).Hash
    if ($dyNativeHash -ne $dyIdentity.NativeExeSHA256) { throw 'Formal Shipping executable changed.' }
    $dyMapHash = (Get-FileHash -LiteralPath $dyMapFile -Algorithm SHA256).Hash
    if ($dyMapHash -ne $dyIdentity.SourceMapSHA256) { throw 'Formal main map no longer matches the packaged build.' }
    $dyFiles = @(Get-ChildItem -LiteralPath $dyArchive -Recurse -File |
        Where-Object { $_.FullName -ne $dyIdentityPath })
    $dyBytes = ($dyFiles | ForEach-Object { [long]$_.Length } | Measure-Object -Sum).Sum
    if ($dyIdentity.ArtifactFileCount -ne $dyFiles.Count -or $dyIdentity.ArtifactBytes -ne $dyBytes) {
        throw 'Formal Shipping package file count or size changed.'
    }
    foreach ($dyRelative in @(
        'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.pak',
        'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.utoc',
        'DengYingShanHai\Content\Paks\DengYingShanHai-Windows.ucas',
        'DengYingShanHai\Content\Paks\global.utoc',
        'DengYingShanHai\Content\Paks\global.ucas'
    )) {
        $dyFile = Join-Path $dyArchive $dyRelative
        if (-not (Test-Path -LiteralPath $dyFile -PathType Leaf) -or (Get-Item -LiteralPath $dyFile).Length -le 0) {
            throw ('Formal Shipping container is missing: ' + $dyRelative)
        }
    }
    $dyRun = Join-Path $dyRoot ('Saved\ReleaseEntryPlay-Shipping\' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff'))
    $dyArguments = @(
        '-nosplash',
        ('-abslog=' + (Join-Path $dyRun 'Session.log'))
    )
    if ($DryRun) {
        [ordered]@{
            Status = 'PASS-PREFLIGHT-ONLY'
            Executable = $dyNative
            Arguments = $dyArguments
            Configuration = 'Shipping'
            MapOverride = $false
            GameLaunched = $false
            ArtifactCount = $dyFiles.Count
            ArtifactBytes = $dyBytes
        } | ConvertTo-Json -Depth 5
        exit 0
    }
    if (@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai,DengYingShanHai-Win64-Shipping -ErrorAction SilentlyContinue).Count) {
        throw 'Please normally close existing UE/game windows first. No process was terminated.'
    }
    New-Item -ItemType Directory -Path $dyRun | Out-Null
    Write-Host 'Opening the formal Shipping package. Art is still a prototype.'
    Write-Host ('Run evidence: ' + $dyRun)
    $dyProcess = Start-Process -FilePath $dyNative -ArgumentList $dyArguments `
        -WorkingDirectory $dyArchive -PassThru -WindowStyle Normal
    $dyHandle = $dyProcess.Handle
    if ($dyHandle -eq [IntPtr]::Zero) { throw 'Actual game handle unavailable.' }
    [ordered]@{
        PID = $dyProcess.Id
        Executable = $dyNative
        Arguments = $dyArguments
        Configuration = 'Shipping'
        MapOverride = $false
        NativeHandleCaptured = $true
        FirstFrameVerified = $false
        FullGameplayVerified = $false
    } | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $dyRun 'Launch.json') -Encoding UTF8
    $dyProcess.WaitForExit()
    $dyExit = $dyProcess.ExitCode
    [ordered]@{
        PID = $dyProcess.Id
        ActualExitCode = $dyExit
        ExitWasNull = ($null -eq $dyExit)
        NativeHandleCaptured = $true
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dyRun 'Exit.json') -Encoding UTF8
    $dyProcess.Dispose()
    if ($null -eq $dyExit) { throw 'Missing actual native game exit code.' }
    exit $dyExit
} catch {
    Write-Error $_
    exit 1
}