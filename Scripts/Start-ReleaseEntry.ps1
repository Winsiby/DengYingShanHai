param([ValidateSet('Development','Shipping')][string]$Configuration='Development',[switch]$DryRun)
$ErrorActionPreference='Stop'
try {
 $projectRoot=Split-Path $PSScriptRoot -Parent
 $buildName='ReleaseEntry-'+$Configuration+'-20261014-Run1'
 $archive=Join-Path $projectRoot ('Builds\'+$buildName+'\Windows')
 $audit=Join-Path $projectRoot ('Saved\Audit-2026-10-14-ReleaseEntry\Package-'+$Configuration+'-Run1')
 function Json([string]$path){$value=Get-Content -LiteralPath $path -Raw -Encoding UTF8|ConvertFrom-Json;return $value}
 function Sha([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash}
 $identity=Json (Join-Path $archive 'RELEASE-ENTRY-BUILD.json')
 $result=Json (Join-Path $audit 'RESULT.json')
 if($result.Status -ceq 'FAIL'){
  $review=Json (Join-Path $audit 'COMPLETION-REVIEW.json')
  if($review.OriginalFailureMetadataOnly -ne $true -or $review.OriginalResultSHA256 -cne (Sha (Join-Path $audit 'RESULT.json'))){throw 'Unreviewed failed package build.'}
  $result=$review
 }
 $rows=@(Json (Join-Path $audit 'ARTIFACTS.json'))
 $nativeName=if($Configuration -ceq 'Shipping'){'DengYingShanHai-Win64-Shipping.exe'}else{'DengYingShanHai.exe'}
 $relative='DengYingShanHai\Binaries\Win64\'+$nativeName
 if($identity.Status -cne 'PASS-BUILD-COOK-STAGE-ARCHIVE-AND-CONTAINERS' -or -not $identity.Succeeded -or $identity.Configuration -cne $Configuration -or $identity.Map -cne '/Game/DengYingShanHai/Maps/L_DY_Main' -or $identity.NativeExecutable -cne $relative -or $identity.ArchiveRoot -ine $archive -or $identity.BuildAudit -ine $audit -or $result.Status -cne $identity.Status -or $result.ActualUATExit -ne 0 -or -not $result.ActualIoStorePayloadHashVerified -or $result.ArtifactFileCount -ne $rows.Count -or $rows.Count -lt 10){throw 'No verified exact release-entry package for this configuration.'}
 if(@($rows.Relative|Sort-Object -Unique).Count -ne $rows.Count){throw 'Duplicate sealed artifact path.'}
 foreach($r in $rows){
  if([string]::IsNullOrWhiteSpace($r.Relative) -or [IO.Path]::IsPathRooted($r.Relative) -or ($r.Relative -split '[\\/]') -contains '..' -or $r.Relative.Replace('/','\') -ieq 'Docs\LICENSES.md'){throw 'Unsafe artifact path.'}
  $p=Join-Path $archive $r.Relative
  if((Get-Item -LiteralPath $p).Length -ne $r.Bytes -or (Sha $p) -cne $r.SHA256){throw ('Sealed package changed: '+$r.Relative)}
 }
 $actual=@(Get-ChildItem -LiteralPath $archive -File -Recurse|ForEach-Object {$_.FullName.Substring($archive.Length+1)})
 if($actual.Count -ne $rows.Count -or @(Compare-Object -CaseSensitive @($actual|Sort-Object) @($rows.Relative|Sort-Object)).Count){throw 'Sealed artifact file set changed.'}
 $native=Join-Path $archive $relative
 if((Sha $native) -cne $identity.NativeExeSHA256){throw 'Native executable identity changed.'}
 $runName='Run-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff')
 $out=Join-Path $projectRoot ('Saved\ReleaseEntryPlay-'+$Configuration+'\'+$runName)
 $arguments='-windowed -ResX=1280 -ResY=800 -nosplash -nowrite "-abslog='+(Join-Path $out 'Session.log')+'" -ForceDPCVars="r.Shadow.Virtual.OnePassProjection=0"'
 # No map override: the packaged GameDefaultMap must supply the formal entry.
 if($DryRun){[ordered]@{Status='PASS-PREFLIGHT-ONLY';Configuration=$Configuration;Executable=$native;Arguments=$arguments;MapOverride=$false;GameLaunched=$false;ArtifactCount=$rows.Count}|ConvertTo-Json -Depth 4;exit 0}
 if(@(Get-Process -Name UnrealEditor,UnrealEditor-Cmd,DengYingShanHai,DengYingShanHai-Win64-Shipping -ErrorAction SilentlyContinue).Count){throw 'Please normally close existing UE/game windows first. No process was terminated.'}
 New-Item -ItemType Directory -Path $out|Out-Null
 Write-Host ('Opening '+$Configuration+' release-entry technical candidate. Art is still a prototype.')
 Write-Host ('Run evidence: '+$out)
 $process=Start-Process -FilePath $native -ArgumentList $arguments -WorkingDirectory $archive -PassThru -WindowStyle Normal
 $handle=$process.Handle;if($handle -eq [IntPtr]::Zero){throw 'Actual game handle unavailable.'}
 [ordered]@{PID=$process.Id;Executable=$native;Arguments=$arguments;Configuration=$Configuration;MapOverride=$false;NativeHandleCaptured=$true;FirstFrameVerified=$false;FullGameplayVerified=$false}|ConvertTo-Json -Depth 4|Set-Content -LiteralPath (Join-Path $out 'Launch.json') -Encoding UTF8
 $process.WaitForExit();$code=$process.ExitCode
 [ordered]@{PID=$process.Id;ActualExitCode=$code;ExitWasNull=($null -eq $code);NativeHandleCaptured=$true}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'Exit.json') -Encoding UTF8
 $process.Dispose();if($null -eq $code){throw 'Missing actual native game exit code.'};exit $code
}catch{Write-Error $_;exit 1}
