
"""旁白与音乐混音：按时间码摆放每句人声，压住音乐，做两遍 loudnorm。"""
import argparse, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
FF = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
FP = r"D:\灯影山海\Tools\ffmpeg\ffprobe.exe"


def secs(t):
    parts = [float(x) for x in str(t).split(":")] if ":" in str(t) else [float(t)]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--picture", default=str(ROOT / "03_final" / "master_silent.mp4"))
    ap.add_argument("--music", default="")
    ap.add_argument("--voice", default=str(ROOT / "01_raw" / "voice"))
    ap.add_argument("--out", default=str(ROOT / "03_final" / "DY_Review_1080p60.mp4"))
    a = ap.parse_args()

    script = json.loads((ROOT / "00_script" / "script.json").read_text(encoding="utf-8"))
    lines = [s for s in script["segments"] if s["style"] == "narration"]
    voice_dir = pathlib.Path(a.voice)
    found = []
    for item in lines:
        for ext in (".wav", ".m4a", ".mp3", ".flac"):
            p = voice_dir / (item["id"] + ext)
            if p.exists():
                found.append((item, p)); break
    if not found:
        raise SystemExit("没有找到旁白文件：请按 %s/N01.wav 命名放入" % voice_dir)

    inputs, chains, mixes = [], [], []
    for i, (item, path) in enumerate(found):
        inputs += ["-i", str(path)]
        delay = int(secs(item["t_in"]) * 1000)
        chains.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,"
                      "highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=8:release=180,"
                      "adelay=%d|%d,volume=1.0[v%d]" % (i, delay, delay, i))
        mixes.append("[v%d]" % i)
    base = "amix=inputs=%d:normalize=0:dropout_transition=0" % len(found)
    chains.append("%s%s[voice]" % ("".join(mixes), base))

    if a.music and pathlib.Path(a.music).exists():
        inputs += ["-i", a.music]
        mi = len(found)
        chains.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.55[mus]" % mi)
        chains.append("[mus][voice]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=400[duck]")
        chains.append("[duck]anull[aout]")
    else:
        chains.append("[voice]anull[aout]")

    inter = ROOT / "03_final" / "mix_intermediate.m4a"
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y"] + inputs + [
        "-filter_complex", ";".join(chains), "-map", "[aout]",
        "-c:a", "aac", "-b:a", "256k", str(inter)]
    subprocess.run(cmd, check=True, cwd=str(ROOT / "03_final"))

    measure = subprocess.run([FF, "-hide_banner", "-nostats", "-i", str(inter),
                              "-af", "loudnorm=I=-16:TP=-1.5:print_format=json",
                              "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", measure.stderr, re.S)
    stats = json.loads(m.group(0)) if m else {}
    gain = ""
    if stats:
        gain = "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s" % (
            stats["input_i"], stats["input_tp"], stats["input_lra"], stats["input_thresh"], stats["target_offset"])

    final = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", a.picture, "-i", str(inter),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
             "-shortest", "-movflags", "+faststart", a.out]
    if gain:
        final = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", a.picture, "-i", str(inter),
                 "-map", "0:v", "-map", "1:a", "-af", gain, "-c:v", "copy", "-c:a", "aac",
                 "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out]
    subprocess.run(final, check=True)
    inter.unlink(missing_ok=True)
    print("混音完成", a.out, "已放置旁白 %d 句" % len(found))


main()
