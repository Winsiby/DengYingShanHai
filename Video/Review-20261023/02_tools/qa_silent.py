# -*- coding: utf-8 -*-
"""Silent-film acceptance: specs, full decode, storyboard, optional audio check."""
import json
import pathlib
import re
import subprocess
import sys

FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
FP = r"D:\灯影山海\Tools\ffmpeg\ffprobe.exe"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main(movie):
    path = pathlib.Path(movie)
    info = json.loads(run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]).stdout)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"]
    dur = float(info["format"]["duration"])
    report = {
        "file": str(path),
        "bytes": path.stat().st_size,
        "duration_s": round(dur, 3),
        "video": {"codec": v["codec_name"], "size": "%sx%s" % (v["width"], v["height"]),
                  "fps": v["r_frame_rate"], "frames": v.get("nb_frames"),
                  "pix_fmt": v.get("pix_fmt"), "bitrate": v.get("bit_rate")},
        "audio": None,
    }
    checks = [
        ("1080p60", v["width"] == 1920 and v["height"] == 1080 and v["r_frame_rate"] == "60/1"),
        ("时长 2:30–4:00", 150 <= dur <= 240),
    ]
    decode = run([FF, "-v", "error", "-i", str(path), "-f", "null", "-"])
    checks.append(("全片解码无错误", decode.returncode == 0 and not decode.stderr.strip()))
    report["decode_stderr"] = decode.stderr.strip()[:800]
    if a:
        loud = run([FF, "-hide_banner", "-nostats", "-i", str(path), "-af",
                    "loudnorm=I=-16:TP=-1.5:print_format=json", "-f", "null", "-"])
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr, re.S)
        if m:
            data = json.loads(m.group(0))
            report["audio"] = {k: data[k] for k in ("input_i", "input_tp", "input_lra")}
            checks.append(("整体响度 -18 ~ -14 LUFS", -18 <= float(data["input_i"]) <= -14))
    else:
        report["audio_check"] = "silent master; no audio stream by design"
    board = path.parent / (path.stem + "_storyboard.jpg")
    run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
         "-vf", "fps=1/9,scale=384:-1,tile=6x4", "-frames:v", "1", str(board)])
    report["storyboard"] = str(board) if board.exists() else None
    report["checks"] = [{"name": n, "pass": bool(ok)} for n, ok in checks]
    report["ok"] = all(ok for _, ok in checks)
    out = path.parent / (path.stem + "_QA.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("duration_s", "video", "checks", "ok")}, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


sys.exit(main(sys.argv[1]))
