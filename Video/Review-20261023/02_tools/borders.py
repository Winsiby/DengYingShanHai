from PIL import Image
import subprocess, pathlib
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
run = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\01_raw\run")
qa = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\05_qa")
for name, t in (("chunk_01", 45), ("chunk_02", 20), ("chunk_03", 20), ("chunk_04", 20)):
    p = qa / ("bd_%s_%d.png" % (name, t))
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(run / (name + ".mp4")), "-frames:v", "1", str(p)], check=True)
    im = Image.open(p).convert("L")
    w, h = im.size
    def band(box):
        c = im.crop(box)
        d = list(c.getdata())
        return round(sum(d) / len(d), 1)
    print("%s t=%d %dx%d top=%.1f bottom=%.1f left=%.1f right=%.1f center=%.1f" % (
        name, t, w, h, band((0, 0, w, 8)), band((0, h - 8, w, h)), band((0, 0, 8, h)), band((w - 8, 0, w, h)), band((w // 4, h // 4, w * 3 // 4, h * 3 // 4))))
