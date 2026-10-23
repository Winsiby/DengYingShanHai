from PIL import Image, ImageDraw
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
run = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\01_raw\run")
qa = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\05_qa")
tiles = []
step = 3
for idx, name in enumerate(("chunk_01", "chunk_02", "chunk_03", "chunk_04")):
    src = run / (name + ".mp4")
    if not src.exists():
        continue
    for t in range(0, 58, step):
        p = qa / ("th_%s_%02d.png" % (name, t))
        subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-vf", "scale=320:-1", str(p)], check=True)
        tiles.append((idx, t, Image.open(p).convert("RGB")))
cols = 10
tw, th = tiles[0][2].size
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (20, 20, 20))
d = ImageDraw.Draw(sheet)
for i, (idx, t, im) in enumerate(tiles):
    x = (i % cols) * tw
    y = (i // cols) * (th + 18)
    sheet.paste(im, (x, y))
    d.text((x + 4, y + th + 3), "C%d %02ds" % (idx + 1, t), fill=(220, 220, 220))
out = qa / "contact_sheet.png"
sheet.save(out)
print(out, sheet.size, len(tiles))
