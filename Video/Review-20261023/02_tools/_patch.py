import pathlib
p = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\02_tools\assemble.py")
s = p.read_text(encoding="utf-8")
s = s.replace('ap.add_argument("--crf", default="12")',
              'ap.add_argument("--crf", default="12")\n    ap.add_argument("--preset", default="slow")')
s = s.replace('"-c:v", "libx264", "-preset", "slow"', '"-c:v", "libx264", "-preset", a.preset')
p.write_text(s, encoding="utf-8")
print("preset arg added")
