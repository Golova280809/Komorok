#!/usr/bin/env python3
"""
clean_repo.py — полная очистка и оптимизация репозитория Komorok.

Что делает:
1. Удаляет пустую папку blog/ (если пустая).
2. Находит ВСЕ PNG/JPG/JPEG во всём репозитории (не только img/).
3. Конвертирует их в WebP и удаляет оригиналы.
4. Обновляет HTML-файлы: заменяет .png/.jpg/.jpeg на .webp в путях.
5. Логирует битые ссылки (файл не найден).
6. Раскладывает картинки из img/ по папкам статей (по правилам).
"""

import re
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent.parent
BLOG_DIR = ROOT / "blog"

CONVERT_EXTENSIONS = {".png", ".jpg", ".jpeg"}
WEBP_QUALITY = 85

# Расширения, которые заменяем в HTML
HTML_EXTENSIONS = {".html", ".htm"}

# Правила: ключевое слово в имени → куда переложить
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
    """Удалить пустую blog/."""
    if not BLOG_DIR.exists():
        print("⏭  blog/ — не найдена.")
        return
    files = [p for p in BLOG_DIR.rglob("*") if p.is_file()]
    if files:
        print(f"⚠️  blog/ — содержит {len(files)} файлов, НЕ удаляем.")
        return
    shutil.rmtree(BLOG_DIR)
    print("✅ blog/ — удалена.")


def step2_convert_all_images():
    """Найти ВСЕ картинки во всём репозитории и конвертировать в WebP."""
    converted = 0
    skipped = 0

    for file in ROOT.rglob("*"):
        # Пропускаем .git и служебные папки
        if any(part in {".git", "node_modules", ".github"} for part in file.parts):
            continue
        if not file.is_file():
            continue
        if file.suffix.lower() not in CONVERT_EXTENSIONS:
            continue

        new_file = file.with_suffix(".webp")

        # Если WebP уже есть — удаляем оригинал
        if new_file.exists():
            print(f"⏭  {file.relative_to(ROOT)} — WebP уже есть.")
            file.unlink()
            skipped += 1
            continue

        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            img.save(new_file, "WEBP", quality=WEBP_QUALITY)
            file.unlink()
            print(f"✅ {file.relative_to(ROOT)} → .webp")
            converted += 1
        except Exception as e:
            print(f"❌ {file.relative_to(ROOT)} — ошибка: {e}")

    print(f"\nКонвертация: {converted} файлов, пропущено {skipped}.")


def step3_update_html_paths():
    """Найти HTML-файлы и заменить .png/.jpg/.jpeg на .webp в путях картинок."""
    # Регулярка ищет в src="..." пути с расширениями png/jpg/jpeg
    pattern = re.compile(
        r'(src=["\'])([^"\']+)\.(png|jpg|jpeg)(["\'])',
        re.IGNORECASE
    )

    updated = 0

    for file in ROOT.rglob("*"):
        if any(part in {".git", "node_modules"} for part in file.parts):
            continue
        if not file.is_file() or file.suffix.lower() not in HTML_EXTENSIONS:
            continue

        content = file.read_text(encoding="utf-8", errors="ignore")
        new_content, count = pattern.subn(r'\1\2.webp\4', content)

        if count > 0 and new_content != content:
            file.write_text(new_content, encoding="utf-8")
            print(f"✅ {file.relative_to(ROOT)} — заменено {count} путей.")
            updated += 1

    print(f"\nОбновлено HTML-файлов: {updated}.")


def step4_check_broken_links():
    """Проверить, что все src в HTML указывают на существующие файлы."""
    broken = 0

    # Регулярка ищет все src="..." (кроме http, https, data)
    pattern = re.compile(r'src=["\']([^"\']+)["\']')

    for file in ROOT.rglob("*.html"):
        if any(part in {".git", "node_modules"} for part in file.parts):
            continue

        content = file.read_text(encoding="utf-8", errors="ignore")

        for match in pattern.finditer(content):
            src = match.group(1)

            # Пропускаем внешние ссылки и data-URI
            if src.startswith(("http://", "https://", "data:", "//", "#")):
                continue

            # Считаем путь относительно HTML-файла
            target = (file.parent / src).resolve()

            if not target.exists():
                print(f"⚠️  {file.relative_to(ROOT)} → битая ссылка: {src}")
                broken += 1

    print(f"\nБитых ссылок: {broken}.")


def step5_sort_images():
    """Разложить картинки из img/ по папкам статей."""
    img_dir = ROOT / "img"
    if not img_dir.exists():
        print("⏭  img/ — не найдена.")
        return

    moved = 0

    for file in sorted(img_dir.rglob("*")):
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
    print("=" * 60)
    print("ОЧИСТКА РЕПОЗИТОРИЯ KOMOROK")
    print("=" * 60)

    print("\nШАГ 1: blog/")
    step1_remove_blog()

    print("\nШАГ 2: Конвертация картинок в WebP")
    step2_convert_all_images()

    print("\nШАГ 3: Обновление путей в HTML")
    step3_update_html_paths()

    print("\nШАГ 4: Проверка битых ссылок")
    step4_check_broken_links()

    print("\nШАГ 5: Сортировка img/ по папкам")
    step5_sort_images()

    print("\n" + "=" * 60)
    print("ГОТОВО.")
    print("=" * 60)


if __name__ == "__main__":
    main()