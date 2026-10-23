from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
film = root / "03_final" / "DY_Review_Silent_1080p60.mp4"
qa = root / "05_qa"
raw = qa / "poster_raw.png"
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "19.6", "-i", str(film), "-frames:v", "1", str(raw)], check=True)
im = Image.open(raw).convert("RGB")
im = im.filter(ImageFilter.GaussianBlur(0.4))
ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)
for y in range(im.size[1]):
    a = int(150 * max(0.0, (y / im.size[1] - 0.55)) / 0.45)
    d.line([(0, y), (im.size[0], y)], fill=(8, 7, 6, a))
im = Image.alpha_composite(im.convert("RGBA"), ov)
d = ImageDraw.Draw(im)
serif = ImageFont.truetype(str(root / "04_assets" / "fonts" / "NotoSerifSC-VF.ttf"), 96)
sans = ImageFont.truetype(str(root / "04_assets" / "fonts" / "NotoSansSC-Regular.otf"), 34)
d.text((96, 830), "灯影山海", font=serif, fill=(240, 234, 222))
d.text((100, 946), "光影神话解谜之旅  ·  UE5 实机录屏", font=sans, fill=(206, 196, 180))
d.line([(100, 930), (300, 930)], fill=(168, 136, 88), width=2)
im.convert("RGB").save(root / "03_final" / "DY_Review_Poster.png")
print("poster ok")
