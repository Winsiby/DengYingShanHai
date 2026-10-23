
import subprocess, os, glob
from PIL import Image, ImageDraw
root = r"D:\灯影山海\Video\Review-20261023"
src = os.path.join(root, r"01_raw\shots\run_20261024.mp4")
tmp = os.path.join(root, r"05_qa\frames_tmp")
os.makedirs(tmp, exist_ok=True)
for f in glob.glob(os.path.join(tmp, "*.png")): os.remove(f)
ff = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
subprocess.run([ff,"-y","-loglevel","error","-i",src,"-vf","fps=1/4,scale=480:-1",os.path.join(tmp,"f_%03d.png")],check=True)
files = sorted(glob.glob(os.path.join(tmp,"f_*.png")))
cols=6; w,h=480,270
rows=(len(files)+cols-1)//cols
sheet=Image.new("RGB",(cols*w,rows*(h+18)),(12,12,12))
d=ImageDraw.Draw(sheet)
for i,f in enumerate(files):
    im=Image.open(f).convert("RGB").resize((w,h))
    x=(i%cols)*w; y=(i//cols)*(h+18)
    sheet.paste(im,(x,y))
    d.text((x+6,y+h+3), f"t={i*4}s", fill=(230,220,200))
sheet.save(os.path.join(root,r"05_qa\sheet_run.png"))
print(len(files), sheet.size)
