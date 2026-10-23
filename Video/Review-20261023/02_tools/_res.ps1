Add-Type -AssemblyName System.Windows.Forms
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
Write-Output ("screen " + $b.Width + "x" + $b.Height)
Add-Type -Namespace W -Name S -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);'
$p = Get-Process DengYingShanHai-Win64-Shipping -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if ($p) { [W.S]::ShowWindow($p.MainWindowHandle, 3) | Out-Null; Write-Output "maximized" }
