from PIL import Image, ImageDraw
import subprocess, pathlib, sys
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
film = root / "03_final" / "DY_Review_Silent_1080p60.mp4"
qa = root / "05_qa"
a, b, step, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
tiles = []
t = a
while t <= b:
    p = qa / ("sr_%05.1f.png" % t)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % t, "-i", str(film), "-frames:v", "1", "-vf", "scale=380:-1", str(p)], check=True)
    tiles.append((t, Image.open(p).convert("RGB")))
    t += step
cols = 6
tw, th = tiles[0][1].size
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 16)), (16, 16, 16))
d = ImageDraw.Draw(sheet)
for i, (tt, im) in enumerate(tiles):
    x, y = (i % cols) * tw, (i // cols) * (th + 16)
    sheet.paste(im, (x, y))
    d.text((x + 3, y + th + 2), "%05.1f" % tt, fill=(240, 240, 240))
sheet.save(qa / out)
print(qa / out, sheet.size, len(tiles))
