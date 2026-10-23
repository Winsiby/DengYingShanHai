param(
    [int]$Seconds = 60,
    [string]$Out = "",
    [int]$Fps = 60,
    [string]$ProcessName = "DengYingShanHai-Win64-Shipping"
)
$ErrorActionPreference = "Stop"
$root = "D:\灯影山海\Video\Review-20261023"
if (-not $Out) { $Out = Join-Path $root ("01_raw\capture-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".mp4") }
$ff = "D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
Add-Type -Namespace Win -Name Native -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT r);
[DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT p);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
[StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
[StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
'@
[Win.Native]::SetProcessDPIAware() | Out-Null
$proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $proc) { throw "Game window not found: $ProcessName" }
$hwnd = $proc.MainWindowHandle
[Win.Native]::ShowWindow($hwnd, 3) | Out-Null
Start-Sleep -Milliseconds 1200
[Win.Native]::SetForegroundWindow($hwnd) | Out-Null
Start-Sleep -Milliseconds 800
$rect = New-Object Win.Native+RECT
[Win.Native]::GetClientRect($hwnd, [ref]$rect) | Out-Null
$pt = New-Object Win.Native+POINT
$pt.X = 0
$pt.Y = 0
[Win.Native]::ClientToScreen($hwnd, [ref]$pt) | Out-Null
$w = $rect.Right - $rect.Left
$h = $rect.Bottom - $rect.Top
if ($w -le 0 -or $h -le 0) { throw "Cannot read client rect" }
$cx = $pt.X - ($pt.X % 2)
$cy = $pt.Y - ($pt.Y % 2)
$cw = $w - ($w % 2)
$ch = $h - ($h % 2)
Write-Host ("window {0} client {1}x{2} at ({3},{4}), record {5}s @ {6}fps" -f $proc.ProcessName, $w, $h, $cx, $cy, $Seconds, $Fps)
$graph = "ddagrab=output_idx=0:framerate=" + $Fps + ",hwdownload,format=bgra,crop=" + $cw + ":" + $ch + ":" + $cx + ":" + $cy + ",scale=1920:1080:flags=lanczos,format=yuv420p"
& $ff -hide_banner -loglevel error -nostats -y -filter_complex $graph -t $Seconds -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p -r $Fps $Out
if ($LASTEXITCODE -ne 0) { throw "ffmpeg capture failed: $LASTEXITCODE" }
Write-Host "captured $Out"
& "D:\灯影山海\Tools\ffmpeg\ffprobe.exe" -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of csv=p=0 $Out
