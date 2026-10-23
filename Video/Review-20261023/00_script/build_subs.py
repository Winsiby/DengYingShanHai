
import json, pathlib, re

ROOT = pathlib.Path(r"D:\灯影山海\Video\Review-20261023")
SCRIPT = ROOT / "00_script" / "script.json"

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Noto Serif SC,116,&H00E8EFF7,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,8,0,1,0,0,5,120,120,0,1
Style: Subtitle,Noto Serif SC,52,&H00F4EEE4,&H00FFFFFF,&H00120F0D,&H96000000,0,0,0,0,100,100,2,0,1,2,1,2,200,200,104,1
Style: Chapter,Noto Serif SC,42,&H00C9A25E,&H00FFFFFF,&H00120F0D,&H96000000,0,0,0,0,100,100,14,0,1,0,0,7,132,132,96,1
Style: Card,Noto Sans SC,40,&H00DCD4C8,&H00FFFFFF,&H00120F0D,&H96000000,0,0,0,0,100,100,6,0,1,0,0,9,132,132,96,1
Style: Body,Noto Sans SC,46,&H00F2F2F2,&H00FFFFFF,&H0012100E,&H96000000,0,0,0,0,100,100,2,0,1,2,1,2,180,180,78,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ts(sec):
    sec = max(sec, 0)
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
    return "%d:%02d:%05.2f" % (h, m, s)

def wrap(text, limit=17):
    pieces = re.split(r"(?<=[，。；：、！？])", text)
    lines, cur = [], ""
    for p in pieces:
        if len(cur) + len(p) <= limit or not cur:
            cur += p
        else:
            lines.append(cur); cur = p
    if cur: lines.append(cur)
    if len(lines) > 2:
        mid = len(lines) // 2
        lines = ["".join(lines[:mid]), "".join(lines[mid:])]
    return r"\N".join(lines)

def main():
    data = json.loads(SCRIPT.read_text(encoding="utf-8"))
    events, warnings = [], []
    for item in data["segments"]:
        style = item["style"]; text = item["text"]
        dur = item["t_out"] - item["t_in"]
        if style == "narration":
            rate = len(re.sub(r"[，。；：、！？“”]", "", text)) / max(dur, .1) * 60
            if rate > 168:
                warnings.append("%s: %.0f 字/分，超过舒适语速 168，需要延长或删字" % (item["id"], rate))
            ass_style, payload = "Subtitle", wrap(text)
        elif style == "chapter":
            ass_style, payload = "Chapter", text
        elif style == "title":
            ass_style, payload = "Title", text
        else:
            ass_style, payload = "Card", text
        effects = r"{\fad(320,320)}" if style in ("chapter", "card") else r"{\fad(240,240)}"
        if style == "title":
            effects = r"{\fad(700,500)}"
        events.append("Dialogue: 0,%s,%s,%s,,0,0,0,,%s%s" % (ts(item["t_in"]), ts(item["t_out"]), ass_style, effects, payload))

    (ROOT / "00_script" / "subtitles.ass").write_text(HEADER + "\n".join(events) + "\n", encoding="utf-8")

    sheet = ["# 配音台本 / Narration Sheet", "",
             "每行独立录制，一句一条文件；文件名用行号，例如 L03.wav。手机录音即可，安静房间、离嘴 15–20 cm。",
             "录音后把文件放进 01_raw/voice/，我负责降噪、对齐与混音。", "",
             "| 行号 | 入点 | 出点 | 时长 | 字数 | 语速 | 台词 |",
             "|---|---|---|---|---|---|---|"]
    for item in data["segments"]:
        if item["style"] != "narration": continue
        body = item["text"]
        chars = len(re.sub(r"[，。；：、！？“”]", "", body))
        dur = item["t_out"] - item["t_in"]
        sheet.append("| %s | %s | %s | %.1fs | %d | %.0f/分 | %s |" % (item["id"], ts(item["t_in"])[1:], ts(item["t_out"])[1:], dur, chars, chars/dur*60, body))
    total = sum(s["t_out"]-s["t_in"] for s in data["segments"] if s["style"]=="narration")
    sheet += ["", "## 总览", "", "- 正片总长：%.1fs" % data["duration"],
              "- 旁白行数：%d" % sum(1 for s in data["segments"] if s["style"]=="narration"),
              "- 旁白占时：%.1fs" % total]
    (ROOT / "00_script" / "narration.md").write_text("\n".join(sheet) + "\n", encoding="utf-8")
    print("subtitles.ass: %d 条" % len(events))
    for w in warnings: print("WARN", w)

main()
