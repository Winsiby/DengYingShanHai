from PIL import Image
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
out = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\06_pilot")
src = out / "master_test.mp4"
rows = []
for t in (2, 8, 20):
    p = out / ("band_t%d.png" % t)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", str(p)], check=True)
    im = Image.open(p).convert("RGB")
    w, h = im.size
    def mean(y0, y1):
        crop = im.crop((0, y0, w, y1))
        data = list(crop.getdata())
        n = len(data)
        return tuple(round(sum(c[i] for c in data) / n, 1) for i in range(3))
    rows.append((t, mean(0, 300), mean(700, 780), mean(960, 1080)))
for r in rows:
    print("t=%ss top=%s lower=%s bottom=%s" % r)
