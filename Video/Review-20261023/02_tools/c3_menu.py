from PIL import Image, ImageDraw
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
qa = root / "05_qa"
src = root / "01_raw" / "run" / "chunk_03.mp4"
times = [28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56]
tiles = []
for t in times:
    p = qa / ("c3m_%02d.png" % t)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-vf", "scale=420:-1", str(p)], check=True)
    tiles.append((t, Image.open(p).convert("RGB")))
tw, th = tiles[0][1].size
cols = 5
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (16, 16, 16))
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(tiles):
    x, y = (i % cols) * tw, (i // cols) * (th + 18)
    sheet.paste(im, (x, y))
    d.text((x + 3, y + th + 2), "c3 %ds" % t, fill=(235, 235, 235))
sheet.save(qa / "c3_menu.png")
print(qa / "c3_menu.png", sheet.size)
