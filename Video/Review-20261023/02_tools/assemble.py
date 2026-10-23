
"""把分镜片段拼成带字幕的母版：统一规格 → 拼接 → 压暗带 → 烧字幕。"""
import argparse, json, pathlib, subprocess, sys

ROOT = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
BAND = "band_alpha.png"


def secs(t):
    parts = [float(x) for x in str(t).split(":")] if ":" in str(t) else [float(t)]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", default=str(ROOT / "02_cut" / "segments.json"))
    ap.add_argument("--out", default=str(ROOT / "03_final" / "master_silent.mp4"))
    ap.add_argument("--crf", default="12")
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--fps", default="60")
    a = ap.parse_args()

    segs = json.loads(pathlib.Path(a.list).read_text(encoding="utf-8"))["segments"]
    inputs, chains, labels = [], [], []
    for i, s in enumerate(segs):
        p = pathlib.Path(s["file"])
        if not p.is_absolute():
            p = ROOT / "01_raw" / p
        if not p.exists():
            raise SystemExit("缺少素材: %s" % p)
        inputs += ["-i", str(p)]
        chains.append(
            "[%d:v]trim=start=%s:end=%s,setpts=PTS-STARTPTS,fps=%s,"
            "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=gbrp[v%d]"
            % (i, s["start"], s["end"], a.fps, i))
        labels.append("[v%d]" % i)
    chains.append("%sconcat=n=%d:v=1:a=0[cat]" % ("".join(labels), len(segs)))

    out_path = pathlib.Path(a.out).resolve()
    work = out_path.parent
    work.mkdir(parents=True, exist_ok=True)
    for src, name in ((ROOT / "00_script" / "subtitles.ass", "subtitles.ass"),
                      (ROOT / "04_assets" / "fonts", "fonts"),
                      (ROOT / "04_assets" / BAND, BAND)):
        dst = work / name
        if not dst.exists():
            if src.is_dir():
                subprocess.run(["powershell", "-NoProfile", "-Command",
                                "Copy-Item -Recurse -Force '%s' '%s'" % (src, dst)], check=True)
            else:
                subprocess.run(["powershell", "-NoProfile", "-Command",
                                "Copy-Item -Force '%s' '%s'" % (src, dst)], check=True)

    inputs += ["-loop", "1", "-framerate", a.fps, "-i", str(ROOT / "04_assets" / BAND)]
    chains.append("[%d:v]format=yuva420p[band]" % len(segs))
    chains.append("[cat]format=yuv420p[caty]")
    chains.append("[caty][band]overlay=0:0:format=yuv420:shortest=1[lit]")
    chains.append("[lit]ass=filename=subtitles.ass:fontsdir=fonts,format=yuv420p[v]")

    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y"] + inputs + [
        "-filter_complex", ";".join(chains), "-map", "[v]",
        "-c:v", "libx264", "-preset", a.preset, "-crf", a.crf, "-pix_fmt", "yuv420p",
        "-r", a.fps, "-movflags", "+faststart", str(out_path)]
    print("拼接 %d 段 → %s" % (len(segs), out_path))
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(work))
    if r.returncode != 0:
        print("FFMPEG 失败，stderr 末尾：")
        print(r.stderr.strip()[-1600:])
        raise SystemExit(1)
    print("ok %s %.1f MB" % (out_path, out_path.stat().st_size / 1e6))


main()
