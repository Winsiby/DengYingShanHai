import pathlib
p = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\02_tools\capture.ps1")
s = p.read_text(encoding="utf-8-sig")
# ASCII-only messages avoid PS 5.1 ANSI misreads
s = s.replace('throw "找不到游戏窗口进程: $ProcessName"', 'throw "Game window not found: $ProcessName"')
s = s.replace('throw "无法读取客户区尺寸"', 'throw "Cannot read client rect"')
s = s.replace('throw "ffmpeg 录制失败: $LASTEXITCODE"', 'throw "ffmpeg capture failed: $LASTEXITCODE"')
s = s.replace('Write-Host ("窗口 {0} 客户区 {1}x{2} @ ({3},{4})，录制 {5}s @ {6}fps" -f $proc.ProcessName, $w, $h, $cx, $cy, $Seconds, $Fps)',
              'Write-Host ("window {0} client {1}x{2} at ({3},{4}), record {5}s @ {6}fps" -f $proc.ProcessName, $w, $h, $cx, $cy, $Seconds, $Fps)')
s = s.replace('Write-Host "已录制 $Out"', 'Write-Host "captured $Out"')
p.write_text(s, encoding="utf-8-sig")
print("bytes", p.stat().st_size, "bom", p.read_bytes()[:3] == b"\xef\xbb\xbf", "cjk", any(ord(c) > 127 for c in p.read_text(encoding="utf-8-sig")))
