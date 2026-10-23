
from PIL import Image
import numpy as np, pathlib
out = pathlib.Path(r"D:\灯影山海\Video\Review-20261023\04_assets\band_mul.png")
h, w = 1080, 1920
y = np.arange(h)[:, None].repeat(w, axis=1).astype(np.float32)
start, end = 640, 1080
t = np.clip((y - start) / (end - start), 0, 1)
gain = 1.0 - (t ** 1.35) * 0.78
img = np.repeat((gain * 255).astype(np.uint8)[..., None], 3, axis=2)
Image.fromarray(img, "RGB").save(out)
print("band_mul updated", img[0, 0], img[-1, 0])
