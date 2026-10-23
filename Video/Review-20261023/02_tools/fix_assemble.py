import pathlib, sys
p = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\02_tools\assemble.py")
s = p.read_text(encoding="utf-8")
if "[caty][band]blend" not in s:
    s = s.replace('chains.append("[cat]format=yuv420p[caty]")',
                  'chains.append("[cat]format=yuv420p[caty]")\n    chains.append("[caty][band]blend=all_mode=multiply:all_opacity=1[lit]")')
    p.write_text(s, encoding="utf-8")
print("has_blend:", "[caty][band]blend" in p.read_text(encoding="utf-8"))
