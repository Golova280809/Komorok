import os
from PIL import Image

IMG_DIR = 'Komorium/bazanovo/album/img/bazanovo2013/'
SUPPORTED = ('.png', '.jpg', '.jpeg')

for filename in os.listdir(IMG_DIR):
    if filename.lower().endswith(SUPPORTED):
        base = os.path.splitext(filename)[0]
        src_path = os.path.join(IMG_DIR, filename)
        dest_path = os.path.join(IMG_DIR, f"{base}.webp")

        # Конвертируем
        img = Image.open(src_path)
        img.save(dest_path, 'webp', quality=85)

        # Проверяем, что WebP создался и не пустой
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            os.remove(src_path)
            print(f'{filename} -> {base}.webp (png удалён)')
        else:
            print(f'{filename} -> {base}.webp НЕ УДАЛЁН (ошибка конвертации)')