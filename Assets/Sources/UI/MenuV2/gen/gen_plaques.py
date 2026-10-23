
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S, PAD, W, H, R = 3, 14, 360, 72, 16

def grad(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array([top, bottom], np.float32)
    return np.repeat(arr[0] + (arr[1]-arr[0]) * t, w, axis=1)

def fnoise(w, h, sigma, blur, seed):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, sigma, (h, w)).astype(np.float32)
    return np.asarray(Image.fromarray(np.clip(n+128,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))).astype(np.float32) - 128

def vignette(w, h, strength, inset):
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, yy, w-1-xx, h-1-yy]).astype(np.float32)
    f = np.clip(1.0 - edge / inset, 0, 1) ** 2
    return (1 - strength * f)[:, :, None]

def make(name, top, bottom, gold_dark, gold_light, ink_shadow=0.0):
    w, h = (W+PAD*2)*S, (H+PAD*2)*S
    base = grad(w, h, np.array(top, np.float32), np.array(bottom, np.float32))
    base = np.repeat(np.repeat(base, 1, 0), 1, 1)
    base += fnoise(w, h, 11, 0.8, 3)[:, :, None]
    base += fnoise(w, h, 5, 2.4, 11)[:, :, None] * 0.6
    base *= np.linspace(1.06, 0.94, h)[:, None, None]
    base *= vignette(w, h, 0.22, 26*S)
    img = Image.fromarray(np.clip(base,0,255).astype(np.uint8)).convert("RGBA")

    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    box = [PAD*S, PAD*S, (PAD+W)*S-1, (PAD+H)*S-1]
    d.rounded_rectangle(box, radius=R*S, fill=255)

    sh = mask.filter(ImageFilter.GaussianBlur(6*S)).point(lambda v: int(v*0.6))
    shadow = Image.new("RGBA", (w,h), (26,14,8,0)); shadow.putalpha(sh)
    canvas = Image.new("RGBA", (w,h), (0,0,0,0))
    canvas.alpha_composite(shadow, (0, 4*S))
    canvas.paste(img, (0,0), mask)

    d2 = ImageDraw.Draw(canvas)
    d2.rounded_rectangle(box, radius=R*S, outline=gold_dark+(255,), width=int(2.6*S))
    inset = int(4.5*S)
    box2 = [box[0]+inset, box[1]+inset, box[2]-inset, box[3]-inset]
    d2.rounded_rectangle(box2, radius=(R-4)*S, outline=gold_light+(255,), width=max(1,int(1.2*S)))
    inset3 = int(8.5*S)
    box3 = [box[0]+inset3, box[1]+inset3, box[2]-inset3, box[3]-inset3]
    d2.rounded_rectangle(box3, radius=max(2,(R-7)*S), outline=gold_dark+(150,), width=max(1,int(0.8*S)))

    # 四角云纹角饰
    for (cx, cy, sx, sy) in [(box2[0]+2, box2[1]+2, 1, 1), (box2[2]-2, box2[1]+2, -1, 1),
                             (box2[0]+2, box2[3]-2, 1, -1), (box2[2]-2, box2[3]-2, -1, -1)]:
        d2.line([(cx, cy), (cx+sx*16*S, cy)], fill=gold_light+(255,), width=max(1,int(1.6*S)))
        d2.line([(cx, cy), (cx, cy+sy*8*S)], fill=gold_light+(255,), width=max(1,int(1.6*S)))
        d2.ellipse([cx+sx*4*S-1.6*S, cy+sy*3*S-1.6*S, cx+sx*4*S+1.6*S, cy+sy*3*S+1.6*S], fill=gold_light+(255,))

    hl = Image.new("RGBA", (w,h), (255,248,232,0))
    dh = ImageDraw.Draw(hl)
    dh.rounded_rectangle([box3[0], box3[1], box3[2], box3[1]+int(9*S)], radius=(R-6)*S, fill=(255,248,232,30))
    canvas = Image.alpha_composite(canvas, hl.filter(ImageFilter.GaussianBlur(1.6*S)))
    out = canvas.resize((W+PAD*2, H+PAD*2), Image.LANCZOS)
    out.save(rf"D:\灯影山海\Assets\Sources\UI\MenuV2\{name}.png")

make("PLQ_Normal",  (247,233,206), (224,201,164), (146,104,46), (214,170,96))
make("PLQ_Hover",   (183,56,42),   (126,28,22),   (238,190,100), (255,230,164))
make("PLQ_Pressed", (152,42,31),   (104,22,18),   (222,174,92), (255,216,142))
make("PLQ_Disabled",(122,110,96),  (96,86,74),    (134,120,102),(158,142,120))
print("ok")
