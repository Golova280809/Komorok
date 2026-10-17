#!/usr/bin/env python3
"""
clean_repo.py — очистка и оптимизация репозитория Komorok.

Что делает:
1. Удаляет пустую папку blog/ (если она пустая).
2. Конвертирует все PNG/JPG/JPEG в WebP (качество 85) и удаляет оригиналы.
3. Раскладывает картинки из img/ по папкам статей (по правилам).
4. Непонятные картинки оставляет в img/.
"""

import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent.parent
IMG_DIR = ROOT / "img"
BLOG_DIR = ROOT / "blog"

CONVERT_EXTENSIONS = {".png", ".jpg", ".jpeg"}
WEBP_QUALITY = 85

RULES = {
    "zina":       "Komorium/vov/people/pionery-geroi/zina-portnova/img",
    "портнова":   "Komorium/vov/people/pionery-geroi/zina-portnova/img",
    "portnova":   "Komorium/vov/people/pionery-geroi/zina-portnova/img",
    "marat":      "Komorium/vov/people/pionery-geroi/marat-kazey/img",
    "казей":      "Komorium/vov/people/pionery-geroi/marat-kazey/img",
    "kazey":      "Komorium/vov/people/pionery-geroi/marat-kazey/img",
    "valya":      "Komorium/vov/people/pionery-geroi/valya-kotik/img",
    "валя":       "Komorium/vov/people/pionery-geroi/valya-kotik/img",
    "kotik":      "Komorium/vov/people/pionery-geroi/valya-kotik/img",
    "котик":      "Komorium/vov/people/pionery-geroi/valya-kotik/img",
    "sasha":      "Komorium/vov/people/pionery-geroi/sasha-chekalin/img",
    "чекалин":    "Komorium/vov/people/pionery-geroi/sasha-chekalin/img",
    "chekalin":   "Komorium/vov/people/pionery-geroi/sasha-chekalin/img",
    "lenya":      "Komorium/vov/people/pionery-geroi/lenya-golikov/img",
    "лёня":       "Komorium/vov/people/pionery-geroi/lenya-golikov/img",
    "golikov":    "Komorium/vov/people/pionery-geroi/lenya-golikov/img",
    "голиков":    "Komorium/vov/people/pionery-geroi/lenya-golikov/img",
    "bazanovo":       "Komorium/bazanovo/img",
    "базаново":       "Komorium/bazanovo/img",
    "semenov":        "Komorium/bazanovo/civil-war/semenov-biography/img",
    "семёнов":        "Komorium/bazanovo/civil-war/semenov-biography/img",
    "рыбкина":        "Komorium/bazanovo/people/Valentina-Rybkina/img",
    "rybkina":        "Komorium/bazanovo/people/Valentina-Rybkina/img",
    "krasnokamensk":  "Komorium/krasnokamensk/img",
    "краснокаменск":  "Komorium/krasnokamensk/img",
    "slavsky":        "Komorium/krasnokamensk/people/slavsky/img",
    "славский":       "Komorium/krasnokamensk/people/slavsky/img",
    "pokrovsky":      "Komorium/krasnokamensk/people/pokrovsky/img",
    "покровский":     "Komorium/krasnokamensk/people/pokrovsky/img",
    "shcherbina":     "Komorium/krasnokamensk/people/shcherbina/img",
    "щербина":        "Komorium/krasnokamensk/people/shcherbina/img",
    "kiselev":        "Komorium/krasnokamensk/people/kiselev/img",
    "киселев":        "Komorium/krasnokamensk/people/kiselev/img",
    "zverev":         "Komorium/krasnokamensk/people/zverev/img",
    "зверев":         "Komorium/krasnokamensk/people/zverev/img",
    "verhovtsev":     "Komorium/krasnokamensk/people/verhovtsev/img",
    "верховцев":      "Komorium/krasnokamensk/people/verhovtsev/img",
    "lossky":         "Komorium/krasnokamensk/people/lossky/img",
    "лосский":        "Komorium/krasnokamensk/people/lossky/img",
    "zlydneva":       "Komorium/krasnokamensk/people/zlydneva/img",
    "злыднева":       "Komorium/krasnokamensk/people/zlydneva/img",
}


def step1_remove_blog():
    if not BLOG_DIR.exists():
        print("⏭  blog/ — не найдена.")
        return
    files = [p for p in BLOG_DIR.rglob("*") if p.is_file()]
    if files:
        print(f"⚠️  blog/ — содержит {len(files)} файлов, НЕ удаляем.")
        return
    shutil.rmtree(BLOG_DIR)
    print("✅ blog/ — удалена.")


def step2_convert_images():
    if not IMG_DIR.exists():
        print("⏭  img/ — не найдена.")
        return
    converted = 0
    for file in IMG_DIR.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in CONVERT_EXTENSIONS:
            continue
        new_file = file.with_suffix(".webp")
        if new_file.exists():
            print(f"⏭  {file.name} — WebP уже есть.")
            file.unlink()
            continue
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            img.save(new_file, "WEBP", quality=WEBP_QUALITY)
            file.unlink()
            print(f"✅ {file.name} → {new_file.name}")
            converted += 1
        except Exception as e:
            print(f"❌ {file.name} — ошибка: {e}")
    print(f"\nКонвертация: {converted} файлов.")


def step3_sort_images():
    if not IMG_DIR.exists():
        return
    moved = 0
    for file in sorted(IMG_DIR.rglob("*")):
        if not file.is_file() or file.suffix.lower() != ".webp":
            continue
        name_lower = file.name.lower()
        target_dir = None
        for keyword, target in RULES.items():
            if name_lower.startswith(keyword.lower()):
                target_dir = ROOT / target
                break
        if target_dir is None:
            print(f"⏭  {file.name} — оставлен.")
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / file.name
        if target_file.exists():
            print(f"⚠️  {file.name} — уже есть.")
            continue
        shutil.move(str(file), str(target_file))
        print(f"✅ {file.name} → {target_dir.relative_to(ROOT)}")
        moved += 1
    print(f"\nПеремещено: {moved}.")


def main():
    print("ОЧИСТКА РЕПОЗИТОРИЯ")
    print("ШАГ 1:"); step1_remove_blog()
    print("\nШАГ 2:"); step2_convert_images()
    print("\nШАГ 3:"); step3_sort_images()
    print("\nГОТОВО.")


if __name__ == "__main__":
    main()