import pathlib
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\02_tools")

a = root / "assemble.py"
s = a.read_text(encoding="utf-8")
s = s.replace('BAND = "band_mul.png"', 'BAND = "band_alpha.png"')
s = s.replace('chains.append("[%d:v]format=yuv420p[band]" % len(segs))',
              'chains.append("[%d:v]format=yuva420p[band]" % len(segs))')
s = s.replace('chains.append("[cat]format=yuv420p[caty]")',
              'chains.append("[cat]format=yuv420p[caty]")')
s = s.replace('chains.append("[caty][band]blend=all_mode=multiply:all_opacity=1[lit]")',
              'chains.append("[caty][band]overlay=0:0:format=yuv420:shortest=1[lit]")')
a.write_text(s, encoding="utf-8")

r = root / "render_slice.py"
t = r.read_text(encoding="utf-8")
t = t.replace('BAND = ROOT / "04_assets" / "band_mul.png"', 'BAND = ROOT / "04_assets" / "band_alpha.png"')
t = t.replace('graph += ";[1:v]format=gbrp[band];[bg][band]blend=all_mode=multiply:all_opacity=1[o]"',
              'graph += ";[1:v]format=yuva420p[band];[bg][band]overlay=0:0:format=yuv420:shortest=1[o]"')
r.write_text(t, encoding="utf-8")

print("assemble overlay:", "overlay=0:0:format=yuv420" in a.read_text(encoding="utf-8"))
print("slice overlay:", "overlay=0:0:format=yuv420" in r.read_text(encoding="utf-8"))
