from PIL import Image
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
out = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\06_pilot")
src = out / "master_test.mp4"
for t in (1, 8, 14, 25):
    p = out / ("txt_t%d.png" % t)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", str(p)], check=True)
    im = Image.open(p).convert("RGB")
    reg = im.crop((0, 880, 1920, 1030))
    px = reg.load()
    white = sum(1 for y in range(reg.height) for x in range(reg.width) if px[x, y][0] > 200 and px[x, y][1] > 200 and px[x, y][2] > 200)
    print("t=%2ds white_px_bottom=%d" % (t, white))
