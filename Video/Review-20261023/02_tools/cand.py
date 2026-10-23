
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
root = r"D:\灯影山海\Video\Review-20261023"
src = os.path.join(root, r"01_raw\shots\run_20261024.mp4")
tmp = os.path.join(root, r"05_qa\cand"); os.makedirs(tmp, exist_ok=True)
ff = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
font = ImageFont.truetype(r"D:\灯影山海\Video\Review-20261023\04_assets\fonts\NotoSansSC-Bold.otf", 26)
cands=[38,76,120]
imgs=[]
for t in cands:
    p=os.path.join(tmp,f"c{t}.png")
    subprocess.run([ff,"-y","-loglevel","error","-ss",str(t),"-i",src,"-frames:v","1","-vf","scale=960:540",p],check=True)
    imgs.append((t,p))
sheet=Image.new("RGB",(960*3, 540+40),(9,9,9)); d=ImageDraw.Draw(sheet)
for i,(t,p) in enumerate(imgs):
    sheet.paste(Image.open(p).convert("RGB"),(i*960,0)); d.text((i*960+10,548), f"t={t}s", fill=(240,230,210), font=font)
sheet.save(os.path.join(root,r"05_qa\cand.png")); print("ok")
