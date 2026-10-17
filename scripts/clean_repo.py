#!/usr/bin/env python3
"""
clean_repo.py — полная очистка и оптимизация репозитория Komorok.

Что делает:
1. Удаляет пустую папку blog/ (если пустая).
2. Находит ВСЕ PNG/JPG/JPEG во всём репозитории.
3. Конвертирует их в WebP и удаляет оригиналы.
4. Во ВСЕХ текстовых файлах (HTML, CSS, JS, JSON) заменяет
   ссылки на .png/.jpg/.jpeg → .webp.
5. Логирует битые ссылки в HTML/CSS.
6. Раскладывает картинки из img/ по папкам статей.
"""

import re
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).parent.parent
BLOG_DIR = ROOT / "blog"
IMG_DIR = ROOT / "img"

CONVERT_EXTENSIONS = {".png", ".jpg", ".jpeg"}
WEBP_QUALITY = 85

# Файлы, где надо менять пути
TEXT_EXTENSIONS = {".html", ".htm", ".css", ".js", ".json", ".md", ".txt", ".xml"}

# Папки, которые пропускаем
SKIP_DIRS = {".git", "node_modules", ".github", "app"}

# Правила сортировки
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


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


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


def step2_convert_all_images():
    """Найти все картинки и конвертировать в WebP."""
    converted = 0
    for file in ROOT.rglob("*"):
        if is_skipped(file) or not file.is_file():
            continue
        if file.suffix.lower() not in CONVERT_EXTENSIONS:
            continue

        new_file = file.with_suffix(".webp")
        if new_file.exists():
            print(f"⏭  {file.relative_to(ROOT)} — WebP уже есть.")
            file.unlink()
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
    print(f"\nКонвертация: {converted} файлов.")


def step3_replace_everywhere():
    """
    Заменить ссылки на .png/.jpg/.jpeg на .webp во ВСЕХ текстовых файлах.

    Ловит:
    - src="...png"
    - href="...jpg"
    - url(...png)
    - srcset="...png 1x, ...jpg 2x"
    - любые строки вида "путь/файл.png"
    """
    # Регулярка: любое слово с расширением .png/.jpg/.jpeg,
    # но только если перед ним есть / или начало строки (чтобы не трогать "hello.png.txt")
    # Используем границу слова перед точкой.
    pattern = re.compile(
        r"([\w\-./\\]+?)\.(png|jpg|jpeg)(\b)",
        re.IGNORECASE
    )

    updated_files = 0
    total_replacements = 0

    for file in ROOT.rglob("*"):
        if is_skipped(file) or not file.is_file():
            continue
        if file.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"❌ {file.relative_to(ROOT)} — ошибка чтения: {e}")
            continue

        new_content, count = pattern.subn(r"\1.webp\3", content)

        if count > 0 and new_content != content:
            try:
                file.write_text(new_content, encoding="utf-8")
                print(f"✅ {file.relative_to(ROOT)} — заменено {count}.")
                updated_files += 1
                total_replacements += count
            except Exception as e:
                print(f"❌ {file.relative_to(ROOT)} — ошибка записи: {e}")

    print(f"\nОбновлено файлов: {updated_files}, заменено путей: {total_replacements}.")


def step4_check_broken_links():
    """Проверить битые ссылки в HTML и CSS."""
    # В HTML: src="..." и href="..." (только для картинок/локальных файлов)
    # В CSS: url(...)
    html_pattern = re.compile(r'(?:src|href)=["\']([^"\']+)["\']')
    css_pattern = re.compile(r"url\(["\']?([^"\')]+)["\']?\)")

    broken = 0

    for file in ROOT.rglob("*"):
        if is_skipped(file) or not file.is_file():
            continue

        suffix = file.suffix.lower()
        if suffix not in {".html", ".htm", ".css"}:
            continue

        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if suffix in {".html", ".htm"}:
            matches = html_pattern.findall(content)
        else:
            matches = css_pattern.findall(content)

        for src in matches:
            if src.startswith(("http://", "https://", "data:", "//", "#", "mailto:", "tel:")):
                continue
            if src.endswith((".html", ".htm")):
                continue  # ссылки на страницы, не картинки

            target = (file.parent / src).resolve()
            if not target.exists():
                print(f"⚠️  {file.relative_to(ROOT)} → {src}")
                broken += 1

    print(f"\nБитых ссылок: {broken}.")


def step5_sort_images():
    """Разложить картинки из img/ по папкам статей."""
    if not IMG_DIR.exists():
        print("⏭  img/ — не найдена.")
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
    print("=" * 60)
    print("ОЧИСТКА РЕПОЗИТОРИЯ KOMOROK")
    print("=" * 60)

    print("\nШАГ 1: blog/")
    step1_remove_blog()

    print("\nШАГ 2: Конвертация картинок в WebP")
    step2_convert_all_images()

    print("\nШАГ 3: Замена путей везде (HTML, CSS, JS, JSON)")
    step3_replace_everywhere()

    print("\nШАГ 4: Проверка битых ссылок")
    step4_check_broken_links()

    print("\nШАГ 5: Сортировка img/")
    step5_sort_images()

    print("\n" + "=" * 60)
    print("ГОТОВО.")
    print("=" * 60)


if __name__ == "__main__":
    main()