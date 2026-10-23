from PIL import Image
import subprocess, pathlib, sys
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
tmp = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\05_qa")
tmp.mkdir(parents=True, exist_ok=True)
jobs = [("chunk_01", 40), ("chunk_02", 10), ("chunk_02", 30), ("chunk_03", 20)]
run = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\01_raw\run")
for name, t in jobs:
    src = run / (name + ".mp4")
    p = tmp / ("st_%s_%d.png" % (name, t))
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", str(p)], check=True)
    im = Image.open(p).convert("RGB").resize((480, 270))
    px = list(im.getdata())
    mean = tuple(round(sum(c[i] for c in px) / len(px)) for i in range(3))
    bright = sum(1 for c in px if max(c) > 90) / len(px)
    uniq = len(set(px))
    print("%s t=%ds mean=%s bright=%.3f uniq=%d" % (name, t, mean, bright, uniq))
ref = pathlib.Path(r"D:\灯影山海\Saved\Audit-2026-10-23-OverallReview\s146-in2.png")
if ref.exists():
    im = Image.open(ref).convert("RGB").resize((480, 270))
    px = list(im.getdata())
    print("ref s146-in2 mean=%s bright=%.3f" % (tuple(round(sum(c[i] for c in px) / len(px)) for i in range(3)), sum(1 for c in px if max(c) > 90) / len(px)))
