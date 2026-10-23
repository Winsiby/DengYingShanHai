from PIL import Image, ImageDraw
import subprocess, pathlib, sys
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
film = root / "03_final" / "DY_Review_Silent_1080p60.mp4"
qa = root / "05_qa"
dur = 172.5
step = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
cols = 6
tiles = []
t = 2.0
while t < dur - 1:
    p = qa / ("vf_%05.1f.png" % t)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % t, "-i", str(film), "-frames:v", "1", "-vf", "scale=340:-1", str(p)], check=True)
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
    d.text((x + 3, y + th + 2), "%04.1fs" % tt, fill=(235, 235, 235))
path = qa / "sheet_final.png"
sheet.save(path)
print(path, sheet.size, len(tiles))
