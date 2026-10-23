from PIL import Image, ImageDraw
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
qa = root / "05_qa"
film = root / "03_final" / "DY_Review_Silent_1080p60.mp4"
times = [20, 50, 82, 150]
tiles = []
for t in times:
    p = qa / ("cc_%d.png" % t)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(film), "-frames:v", "1", "-vf", "scale=960:-1", str(p)], check=True)
    tiles.append((t, Image.open(p).convert("RGB")))
tw, th = tiles[0][1].size
sheet = Image.new("RGB", (tw * 2, (th + 20) * 2), (16, 16, 16))
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(tiles):
    x, y = (i % 2) * tw, (i // 2) * (th + 20)
    sheet.paste(im, (x, y))
    d.text((x + 4, y + th + 2), "%ds" % t, fill=(240, 240, 240))
sheet.save(qa / "cap_sheet.png")
print(qa / "cap_sheet.png", sheet.size)
