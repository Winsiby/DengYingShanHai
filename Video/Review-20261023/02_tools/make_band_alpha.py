from PIL import Image
import pathlib
root = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\04_assets")
src = Image.open(root / "band_mul.png").convert("L")
w, h = src.size
out = Image.new("RGBA", (w, h))
out.putalpha(src.point(lambda v: 255 - v))
out.putdata([(0, 0, 0, a) for a in src.point(lambda v: 255 - v).getdata()])
out.save(root / "band_alpha.png")
print("size", w, h, "alpha_top", out.getpixel((0, 0))[3], "alpha_bottom", out.getpixel((0, h - 1))[3])
