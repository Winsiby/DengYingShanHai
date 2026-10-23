from PIL import Image, ImageDraw
import subprocess, pathlib, sys
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
run = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\01_raw\run")
qa = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\05_qa")
name, step, cols, out = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
src = run / (name + ".mp4")
tiles = []
t = 0.0
while t < 57.5:
    p = qa / ("th2_%s_%05.1f.png" % (name, t))
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % t, "-i", str(src), "-frames:v", "1", "-vf", "scale=384:-1", str(p)], check=True)
    tiles.append((t, Image.open(p).convert("RGB")))
    t += step
tw, th = tiles[0][1].size
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 16)), (16, 16, 16))
d = ImageDraw.Draw(sheet)
for i, (tt, im) in enumerate(tiles):
    x = (i % cols) * tw
    y = (i // cols) * (th + 16)
    sheet.paste(im, (x, y))
    d.text((x + 3, y + th + 2), "%ss" % ("%04.1f" % tt), fill=(230, 230, 230))
path = qa / out
sheet.save(path)
print(path, sheet.size, len(tiles))
