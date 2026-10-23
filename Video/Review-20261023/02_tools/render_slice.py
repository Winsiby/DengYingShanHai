
"""Render one timeline slice: darken bottom band, burn shifted subtitles, encode 1080p."""
import argparse, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
ASS = ROOT / "00_script" / "subtitles.ass"
FONTS = ROOT / "04_assets" / "fonts"
BAND = ROOT / "04_assets" / "band_alpha.png"


def ts(sec):
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def parse(t):
    parts = [float(x) for x in str(t).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def slice_ass(start, end, out):
    """剪出时间窗内的字幕，并整体平移到 0，避免依赖 itsoffset。"""
    text = ASS.read_text(encoding="utf-8")
    head, _, body = text.partition("[Events]")
    head = head + "[Events]\n"
    body = body.split("\n", 1)[1]  # 丢 Format 行后再补回
    fmt = "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    rows = []
    for line in body.splitlines():
        if not line.startswith("Dialogue:"):
            continue
        parts = line.split(",", 9)
        t0, t1 = parse(parts[1]), parse(parts[2])
        if t1 <= start or t0 >= end:
            continue
        rows.append("Dialogue: %s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            parts[0].split(":")[1].strip(), ts(max(t0, start) - start), ts(min(t1, end) - start),
            parts[3], parts[4], parts[5], parts[6], parts[7], parts[8], parts[9]))
    out.write_text(head + fmt + "\n".join(rows) + "\n", encoding="utf-8")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--still", action="store_true")
    ap.add_argument("--crf", default="18")
    ap.add_argument("--fps", default="60")
    ap.add_argument("--band", default="1")
    a = ap.parse_args()

    start, end = parse(a.start), parse(a.end)
    dur = end - start
    tmp_ass = pathlib.Path(a.out).with_suffix(".slice.ass")
    n = slice_ass(start, end, tmp_ass)
    print("slice %s-%s (%.1fs), 字幕 %d 条" % (a.start, a.end, dur, n))

    bg = pathlib.Path(a.bg)
    inputs = ["-i", str(bg)]
    graph = "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=gbrp[bg]"
    if a.band == "1":
        inputs += ["-loop", "1", "-i", str(BAND)]
        graph += ";[1:v]format=yuva420p[band];[bg][band]overlay=0:0:format=yuv420:shortest=1[o]"
    else:
        graph += ";[bg]null[o]"
    graph += ";[o]ass=filename=%s:fontsdir=%s,format=yuv420p[v]" % (tmp_ass.name, FONTS.name)

    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y"]
    if a.still:
        cmd += ["-loop", "1", "-framerate", a.fps]
    cmd += inputs
    cmd += ["-t", "%.3f" % dur, "-filter_complex", graph, "-map", "[v]",
            "-c:v", "libx264", "-preset", "medium", "-crf", a.crf,
            "-pix_fmt", "yuv420p", "-r", a.fps, a.out]
    # 在切片目录内执行，相对路径交给 libass，避免 Windows 盘符冒号被 filter 语法截断
    subprocess.run(cmd, check=True, cwd=str(pathlib.Path(a.out).parent))
    print("ok", a.out)


main()
