
import subprocess, os
from PIL import Image, ImageDraw, ImageFont
root = r"D:\灯影山海\Video\Review-20261023"
src = os.path.join(root, r"01_raw\shots\run_20261024.mp4")
tmp = os.path.join(root, r"05_qa\probe_frames"); os.makedirs(tmp, exist_ok=True)
ff = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
font = ImageFont.truetype(r"D:\灯影山海\Video\Review-20261023\04_assets\fonts\NotoSansSC-Regular.otf", 22)
times = list(range(44, 92, 4))
imgs=[]
for t in times:
    p=os.path.join(tmp,f"p{t}.png")
    subprocess.run([ff,"-y","-loglevel","error","-ss",str(t),"-i",src,"-frames:v","1","-vf","scale=640:360",p],check=True)
    imgs.append((t,p))
cols=4; w,h=640,360
rows=(len(imgs)+cols-1)//cols
sheet=Image.new("RGB",(cols*w,rows*(h+26)),(10,10,10)); d=ImageDraw.Draw(sheet)
for i,(t,p) in enumerate(imgs):
    im=Image.open(p).convert("RGB"); x=(i%cols)*w; y=(i//cols)*(h+26)
    sheet.paste(im,(x,y)); d.text((x+8,y+h+2), f"t={t}s", fill=(240,230,210), font=font)
sheet.save(os.path.join(root,r"05_qa\probe_mid.png")); print(sheet.size)
