from PIL import Image, ImageDraw
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
film = root / "03_final" / "DY_Review_Silent_1080p60.mp4"
c2 = root / "01_raw" / "run" / "chunk_02.mp4"
qa = root / "05_qa"
rows = []
for tag, src, times in (("FILM", film, [148, 151, 154, 157, 160, 163]), ("C2", c2, [47, 49, 51, 53, 55, 57])):
    tiles = []
    for t in times:
        p = qa / ("cmp_%s_%d.png" % (tag, t))
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-vf", "scale=420:-1", str(p)], check=True)
        tiles.append((tag, t, Image.open(p).convert("RGB")))
    rows.append(tiles)
tw, th = rows[0][0][2].size
sheet = Image.new("RGB", (6 * tw, 2 * (th + 18)), (16, 16, 16))
d = ImageDraw.Draw(sheet)
for r, tiles in enumerate(rows):
    for c, (tag, t, im) in enumerate(tiles):
        x, y = c * tw, r * (th + 18)
        sheet.paste(im, (x, y))
        d.text((x + 3, y + th + 2), "%s %ds" % (tag, t), fill=(235, 235, 235))
sheet.save(qa / "cmp_tail.png")
print(qa / "cmp_tail.png", sheet.size)
