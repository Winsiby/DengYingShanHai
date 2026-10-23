
"""成片验收：规格、全片解码、抽帧故事板、响度。任一项不过即非零退出。"""
import json, pathlib, re, subprocess, sys

FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
FP = r"D:\灯影山海\Tools\ffmpeg\ffprobe.exe"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def probe(path):
    r = run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    if r.returncode != 0:
        raise SystemExit("ffprobe 失败: " + r.stderr[:400])
    return json.loads(r.stdout)


def main(movie):
    path = pathlib.Path(movie)
    info = probe(path)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"]
    dur = float(info["format"]["duration"])
    report = {
        "file": str(path),
        "bytes": path.stat().st_size,
        "duration_s": round(dur, 3),
        "video": {"codec": v["codec_name"], "size": "%sx%s" % (v["width"], v["height"]),
                  "fps": v["r_frame_rate"], "pix_fmt": v.get("pix_fmt"), "bitrate": v.get("bit_rate")},
        "audio": {"codec": a[0]["codec_name"], "sample_rate": a[0]["sample_rate"],
                  "channels": a[0]["channels"], "bitrate": a[0].get("bit_rate")} if a else None,
    }
    checks = []
    checks.append(("1080p60", v["width"] == 1920 and v["height"] == 1080 and v["r_frame_rate"] == "60/1"))
    checks.append(("时长在 4:20–5:20", 260 <= dur <= 320))
    checks.append(("存在音轨", bool(a)))
    decode = run([FF, "-v", "error", "-i", str(path), "-f", "null", "-"])
    checks.append(("全片解码无错误", decode.returncode == 0 and not decode.stderr.strip()))
    report["decode_stderr"] = decode.stderr.strip()[:800]

    loud = run([FF, "-hide_banner", "-nostats", "-i", str(path), "-af", "loudnorm=I=-16:TP=-1.5:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr, re.S)
    if m:
        data = json.loads(m.group(0))
        report["loudness"] = {k: data[k] for k in ("input_i", "input_tp", "input_lra", "input_thresh")}
        checks.append(("整体响度 -18 ~ -14 LUFS", -18 <= float(data["input_i"]) <= -14))
        checks.append(("真峰值 <= -1.0 dBTP", float(data["input_tp"]) <= -1.0))
    else:
        report["loudness"] = None
        checks.append(("响度可测", False))

    board = path.parent / (path.stem + "_storyboard.jpg")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
         "-vf", "fps=1/12,scale=480:-1,tile=6x4", "-frames:v", "1", str(board)])
    report["storyboard"] = str(board) if board.exists() else None
    report["checks"] = [{"name": n, "pass": bool(ok)} for n, ok in checks]
    report["ok"] = all(ok for _, ok in checks)
    out = path.parent / (path.stem + "_QA.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2)[:1800])
    sys.exit(0 if report["ok"] else 1)


main(sys.argv[1])
