
import subprocess, os, glob
from PIL import Image, ImageDraw, ImageFont
root = r"D:\灯影山海\Video\Review-20261023"
src = os.path.join(root, r"01_raw\shots\run_20261024.mp4")
out = r"D:\灯影山海\Screenshots\Gameplay-Run167"
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, "*.png")): os.remove(f)
ff = r"D:\灯影山海\Tools\ffmpeg\ffmpeg.exe"
label_font = ImageFont.truetype(r"D:\灯影山海\Video\Review-20261023\04_assets\fonts\NotoSansSC-Bold.otf", 30)
shots = [
 ("01_主菜单", 3.0),
 ("02_入场灯径", 13.0),
 ("03_入戏台", 21.0),
 ("04_第一幕_夸父逐日", 26.0),
 ("05_第一幕完成_杖落成林", 38.0),
 ("06_第二幕_精卫填海", 76.0),
 ("07_第三幕_刑天舞干戚", 120.0),
 ("08_第四幕_烛龙昼夜", 134.0),
 ("09_复演图鉴_复演已成", 149.0),
]
made=[]
for name,t in shots:
    p=os.path.join(out,name+".png")
    subprocess.run([ff,"-y","-loglevel","error","-ss",f"{t:.2f}","-i",src,"-frames:v","1","-vf","scale=1920:1080:flags=lanczos",p],check=True)
    made.append((name,p))
cols=3; tw,th=640,360
rows=(len(made)+cols-1)//cols
sheet=Image.new("RGB",(cols*tw, rows*(th+46)),(9,9,9)); d=ImageDraw.Draw(sheet)
for i,(name,p) in enumerate(made):
    im=Image.open(p).convert("RGB").resize((tw,th))
    x=(i%cols)*tw; y=(i//cols)*(th+46)
    sheet.paste(im,(x,y)); d.text((x+10,y+th+8), name, fill=(238,228,208), font=label_font)
sheet.save(os.path.join(out,"00_总览.png"))
print("count", len(made))
