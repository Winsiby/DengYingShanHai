import pathlib
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\02_tools")
cap = root / "capture.ps1"
s = cap.read_text(encoding="utf-8-sig")
s = s.replace('-loglevel warning -stats -y', '-loglevel error -nostats -y')
cap.write_text(s, encoding="utf-8-sig")

rec = root / "record_chunks.ps1"
t = rec.read_text(encoding="utf-8-sig")
t = t.replace('$ErrorActionPreference = "Stop"', '$ErrorActionPreference = "Continue"')
t = t.replace('& powershell -NoProfile -ExecutionPolicy Bypass -File "D:\\灯影山海\\Video\\Review-20261023\\02_tools\\capture.ps1" -Seconds $Seconds -Out $out 2>&1 | Select-Object -Last 1',
              '& powershell -NoProfile -ExecutionPolicy Bypass -File "D:\\灯影山海\\Video\\Review-20261023\\02_tools\\capture.ps1" -Seconds $Seconds -Out $out *> $null')
rec.write_text(t, encoding="utf-8-sig")
print("cap nostats:", "-nostats" in cap.read_text(encoding="utf-8-sig"))
print("rec continue:", 'Continue' in rec.read_text(encoding="utf-8-sig"), "null redirect:", "*> $null" in rec.read_text(encoding="utf-8-sig"))
