# -*- coding: utf-8 -*-
"""Assemble the silent review film from the recorded campaign run.

Segments are re-timed (slow motion keeps 60 fps), lightly punched in, then
concatenated, darkened by the band and finally captioned with burned ASS.
"""
import json
import pathlib
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
ROOT = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
RUN = ROOT / "01_raw" / "run"
CUT = ROOT / "02_cut"
ASSETS = ROOT / "04_assets"
QA = ROOT / "05_qa"
FINAL = ROOT / "03_final"
FONTS = ASSETS / "fonts"
SERIF = str(FONTS / "NotoSerifSC-VF.ttf")
SANS = str(FONTS / "NotoSansSC-Regular.otf")
SANS_B = str(FONTS / "NotoSansSC-Bold.otf")
W, H, FPS = 1920, 1080, 60

for d in (CUT, QA, FINAL):
    d.mkdir(parents=True, exist_ok=True)


def spaced(draw, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def card(name, kicker, title, lines, footer=""):
    im = Image.new("RGB", (W, H), (9, 8, 7))
    d = ImageDraw.Draw(im)
    for y in range(H):
        v = int(6 + 10 * (1 - abs(y - H * 0.45) / (H * 0.55)))
        d.line([(0, y), (W, y)], fill=(v, int(v * 0.86), int(v * 0.72)))
    f_kick = ImageFont.truetype(SANS, 30)
    f_title = ImageFont.truetype(SERIF, 132 if len(title) <= 4 else 104)
    f_line = ImageFont.truetype(SANS, 40)
    f_foot = ImageFont.truetype(SANS, 26)
    gold = (214, 178, 118)
    dim = (186, 176, 160)
    if kicker:
        kw = sum(d.textlength(c, font=f_kick) + 6 for c in kicker)
        spaced(d, ((W - kw) / 2, H * 0.34), kicker, f_kick, gold, 6)
    tw = sum(d.textlength(c, font=f_title) for c in title)
    spaced(d, ((W - tw) / 2, H * 0.42 - f_title.size * 0.5), title, f_title, (238, 232, 220), 10)
    d.line([(W / 2 - 90, H * 0.585), (W / 2 + 90, H * 0.585)], fill=(120, 100, 74), width=2)
    y = H * 0.635
    for line in lines:
        lw = d.textlength(line, font=f_line)
        d.text(((W - lw) / 2, y), line, font=f_line, fill=dim)
        y += 64
    if footer:
        fw = d.textlength(footer, font=f_foot)
        d.text(((W - fw) / 2, H * 0.885), footer, font=f_foot, fill=(126, 118, 108))
    p = ASSETS / ("card_%s.png" % name)
    im.save(p)
    return p


# ---------------------------------------------------------------- edit decision
CARDS = [
    ("title", "U E 5   ·   实 时 光 影 解 谜", "灯影山海",
     ["一座久未开演的戏台，等一个人重新点灯。"], "光影神话解谜之旅", 7.0),
    ("act1", "第 一 幕", "夸父逐日",
     ["操纵灯，把影子送回浅色的缺口。"], "", 4.5),
    ("act2", "第 二 幕", "精卫填海",
     ["灯和偶一起动，影子才会从残缺走向完整。"], "", 4.5),
    ("act3", "第 三 幕", "刑天舞干戚",
     ["换一种握法，仍只靠这一盏灯。"], "", 4.5),
    ("act4", "第 四 幕", "烛龙昼夜",
     ["睁眼为昼，闭眼为夜。"], "", 4.5),
    ("end", "四 幕 演 尽", "杖落成林",
     ["夸父、精卫、刑天与烛龙的影子都已落定。"], "《灯影山海》· 实机录屏", 7.0),
]

SEGS = [
    # (source, start, end, speed, zoom, fade_in, fade_out)
    ("chunk_01.mp4", 0.6, 4.5, 0.75, 1.0, 1.2, 0.6),
    ("chunk_01.mp4", 6.0, 20.0, 0.85, 1.0, 0.8, 0.8),
    ("chunk_01.mp4", 20.0, 24.2, 0.80, 1.0, 0.8, 0.8),
    ("chunk_01.mp4", 26.0, 44.0, 0.66, 1.0, 0.8, 0.8),
    ("chunk_02.mp4", 0.0, 2.6, 0.70, 1.0, 0.6, 0.8),
    ("chunk_02.mp4", 3.0, 20.5, 0.66, 1.0, 0.8, 0.8),
    ("chunk_02.mp4", 21.0, 46.0, 0.68, 1.0, 0.8, 0.8),
    ("chunk_02.mp4", 46.2, 55.5, 0.70, 1.0, 0.8, 0.8),
    ("chunk_02.mp4", 56.6, 58.0, 0.60, 1.0, 0.4, 0.5),
    ("chunk_03.mp4", 0.2, 9.6, 0.70, 1.0, 0.5, 0.8),
    ("chunk_03.mp4", 27.6, 38.6, 0.80, 1.0, 1.0, 1.2),
]

# Captions are (segment index, offset in seconds inside that segment, duration, text)
CAPTIONS = []


def run(cmd, tag):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.stderr.write("[%s] %s\n%s\n%s\n" % (tag, " ".join(cmd), p.stdout[-1500:], p.stderr[-3000:]))
        raise SystemExit(1)


def render_card(name, dur, fade_in, fade_out):
    out = CUT / ("seg_card_%s.mp4" % name)
    src = ASSETS / ("card_%s.png" % name)
    if out.exists() and out.stat().st_size > 10000:
        return out
    vf = ("fps=%d,format=yuv420p,"
          "fade=t=in:st=0:d=%.2f,fade=t=out:st=%.2f:d=%.2f") % (FPS, fade_in, max(0, dur - fade_out), fade_out)
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-t", "%.3f" % dur, "-i", str(src),
         "-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         "-pix_fmt", "yuv420p", str(out)], "card " + name)
    return out


def render_seg(i, src, ss, to, speed, zoom, fi, fo):
    dur = (to - ss) / speed
    out = CUT / ("seg_%02d.mp4" % i)
    if out.exists() and out.stat().st_size > 10000:
        return out, (to - ss) / speed
    if zoom <= 1.001:
        scale = "scale=%d:%d:flags=lanczos" % (W, H)
    else:
        scale = "scale=%d:%d:flags=lanczos,crop=%d:%d" % (int(W * zoom) // 2 * 2, int(H * zoom) // 2 * 2, W, H)
    vf = "setpts=(PTS-STARTPTS)/%.4f,%s,fps=%d,format=yuv420p,fade=t=in:st=0:d=%.2f,fade=t=out:st=%.2f:d=%.2f" % (
        speed, scale, FPS, fi, max(0, dur - fo), fo)
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % ss, "-to", "%.2f" % to,
         "-i", str(RUN / src), "-vf", vf, "-r", str(FPS), "-an",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", str(out)], "seg %d" % i)
    return out, dur


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Noto Sans SC,50,&H00F0ECE2,&H00F0ECE2,&H00120E0A,&H7A000000,0,0,0,0,100,100,1,0,1,1.6,0.8,2,180,180,104,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main():
    timeline = []
    t = 0.0
    for name, kicker, title, lines, footer, dur in CARDS:
        card(name, kicker, title, lines, footer)
    order = []
    names = [c[0] for c in CARDS]
    order.append(("card", "title"))
    for i in range(len(SEGS)):
        order.append(("seg", i))
        if i in (2, 4, 5, 6):
            order.append(("card", ["act1", "act2", "act3", "act4"][(2, 4, 5, 6).index(i)]))
    order.append(("card", "end"))
    starts = {}
    files = []
    for kind, key in order:
        if kind == "card":
            dur = dict((c[0], c[5]) for c in CARDS)[key]
            fi = 1.2
            fo = 1.0
            p = render_card(key, dur, fi, fo)
            starts[("card", key)] = t
            timeline.append(("card", key, t, dur))
            t += dur
        else:
            src, ss, to, speed, zoom, fi, fo = SEGS[key]
            p, dur = render_seg(key, src, ss, to, speed, zoom, fi, fo)
            starts[("seg", key)] = t
            timeline.append(("seg", key, t, dur))
            t += dur
        files.append(p)
    total = t
    lst = QA / "concat.txt"
    lst.write_text("".join("file '%s'\n" % str(p).replace("\\", "/") for p in files), encoding="utf-8")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(CUT / "film_plain.mp4")], "concat")

    ass = [ASS_HEAD]
    for idx, off, dur, text in CAPTIONS:
        st = starts[("seg", idx)] + off
        ass.append("Dialogue: 0,%s,%s,Cap,,0,0,0,,{\\fad(300,300)}%s\n" % (ass_time(st), ass_time(st + dur), text))
    ass_path = ROOT / "captions.ass"
    ass_path.write_text("".join(ass), encoding="utf-8")

    final = FINAL / "DY_Review_Silent_1080p60.mp4"
    vf = ("[0:v]format=yuv420p[base];[1:v]format=yuva420p[band];"
          "[base][band]overlay=0:0:format=yuv420:shortest=1,ass=%s[lit]") % "captions.ass"
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", str(CUT / "film_plain.mp4"),
         "-loop", "1", "-i", str(ASSETS / "band_alpha.png"), "-filter_complex", vf.replace("ass=captions.ass", "ass=captions.ass:fontsdir=04_assets/fonts"),
         "-map", "[lit]",
         "-t", "%.3f" % total,
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-an", "-movflags", "+faststart", str(final)], "final")
    report = dict(total_seconds=round(total, 2), frames=int(total * FPS),
                  timeline=[dict(kind=k, key=key, start=round(st, 2), dur=round(d, 2)) for k, key, st, d in timeline],
                  captions=len(CAPTIONS), final=str(final))
    (QA / "film_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dict(total=round(total, 2), segments=len(files), final=str(final)), ensure_ascii=False))


if __name__ == "__main__":
    main()
