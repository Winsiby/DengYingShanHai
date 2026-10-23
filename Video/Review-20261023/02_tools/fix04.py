
import subprocess, os, glob
from PIL import Image, ImageDraw, ImageFont
root = r"D:\灯影山海\Video\Review-20261023"
src = os.path.join(root, r"01_raw\shots\run_20261024.mp4")
out = r"D:\灯影山海\Screenshots\Gameplay-Run167"
ff = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
font = ImageFont.truetype(r"D:\灯影山海\Video\Review-20261023\04_assets\fonts\NotoSansSC-Bold.otf", 30)
subprocess.run([ff,"-y","-loglevel","error","-ss","24.0","-i",src,"-frames:v","1","-vf","scale=1920:1080:flags=lanczos",os.path.join(out,"04_第一幕_夸父逐日.png")],check=True)
names = sorted([os.path.basename(p) for p in glob.glob(os.path.join(out,"*.png")) if not os.path.basename(p).startswith("00_")])
cols=3; tw,th=640,360
rows=(len(names)+cols-1)//cols
sheet=Image.new("RGB",(cols*tw, rows*(th+46)),(9,9,9)); d=ImageDraw.Draw(sheet)
for i,n in enumerate(names):
    sheet.paste(Image.open(os.path.join(out,n)).convert("RGB").resize((tw,th)),((i%cols)*tw,(i//cols)*(th+46)))
    d.text(((i%cols)*tw+10,(i//cols)*(th+46)+th+8), n[:-4], fill=(238,228,208), font=font)
sheet.save(os.path.join(out,"00_总览.png"))
print(len(names))
