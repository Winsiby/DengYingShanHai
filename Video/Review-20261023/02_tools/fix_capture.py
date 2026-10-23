import pathlib
p = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\02_tools\capture.ps1")
s = p.read_text(encoding="utf-8")
if "ShowWindow" not in s:
    s = s.replace('[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);',
                  '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);\n[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);')
    s = s.replace('[Win.Native]::SetForegroundWindow($hwnd) | Out-Null',
                  '[Win.Native]::ShowWindow($hwnd, 3) | Out-Null\nStart-Sleep -Milliseconds 1200\n[Win.Native]::SetForegroundWindow($hwnd) | Out-Null')
    p.write_text(s, encoding="utf-8")
print("ShowWindow" in p.read_text(encoding="utf-8"))
