
from PIL import Image, ImageDraw, ImageFont
bg = Image.open(r"D:\灯影山海\Assets\Sources\UI\MenuV2\main-menu-reference.png").convert("RGBA")
items = [("PLQ_Normal","开始游戏",(48,32,20)),("PLQ_Normal","继续游戏",(48,32,20)),
         ("PLQ_Normal","章节选择",(48,32,20)),("PLQ_Normal","游戏说明",(48,32,20)),
         ("PLQ_Normal","设置",(48,32,20)),("PLQ_Disabled","退出游戏",(126,114,100))]
f = ImageFont.truetype(r"C:\Windows\Fonts\NotoSansSC-Medium.otf", 34)
X, WID = 61, 352
tops = [206, 282, 358, 438, 518, 598]
for i,(n,txt,col) in enumerate(items):
    p = Image.open(rf"D:\灯影山海\Assets\Sources\UI\MenuV2\{n}.png").convert("RGBA").resize((WID, round(WID*100/352)), Image.LANCZOS)
    bg.alpha_composite(p, (X, tops[i]-14))
    d = ImageDraw.Draw(bg)
    bb = d.textbbox((0,0), txt, font=f)
    d.text((X+WID/2-(bb[2]-bb[0])/2, tops[i]+28-(bb[3]-bb[1])/2-bb[1]), txt, font=f, fill=col)
bg.crop((20,110,540,790)).save(r"C:\Users\lenovo\AppData\Local\Temp\preview_plaque2.png")
print("preview")
