import os
from PIL import Image

IMG_DIR = 'img'
SUPPORTED = ('.png', '.jpg', '.jpeg')

for filename in os.listdir(IMG_DIR):
    if filename.lower().endswith(SUPPORTED):
        base = os.path.splitext(filename)[0]
        src_path = os.path.join(IMG_DIR, filename)
        dest_path = os.path.join(IMG_DIR, f"{base}.webp")
        img = Image.open(src_path)
        img.save(dest_path, 'webp')
        print(f'{filename} -> {base}.webp')