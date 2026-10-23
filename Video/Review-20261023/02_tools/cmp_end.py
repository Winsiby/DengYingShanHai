from PIL import Image, ImageDraw
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
qa = root / "05_qa"
items = [("chunk_02.mp4", t) for t in (55.5, 56.5, 57.5)] + [("chunk_03.mp4", t) for t in (0.5, 1.5, 2.5, 4.0, 6.0, 9.0)]
tiles = []
for name, t in items:
    p = qa / ("ce_%s_%05.1f.png" % (name[:8], t))
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % t, "-i", str(root / "01_raw" / "run" / name), "-frames:v", "1", "-vf", "scale=420:-1", str(p)], check=True)
    tiles.append((name[:8] + " " + ("%04.1f" % t), Image.open(p).convert("RGB")))
tw, th = tiles[0][1].size
cols = 5
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (16, 16, 16))
d = ImageDraw.Draw(sheet)
for i, (label, im) in enumerate(tiles):
    x, y = (i % cols) * tw, (i // cols) * (th + 18)
    sheet.paste(im, (x, y))
    d.text((x + 3, y + th + 2), label, fill=(235, 235, 235))
sheet.save(qa / "cmp_end.png")
print(qa / "cmp_end.png", sheet.size)
