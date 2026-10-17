#!/usr/bin/env python3
"""
add_common_js.py — подключает common.js во все HTML-файлы сайта.

Правила:
- Если <script src="common.js"> уже есть — пропускаем.
- Вставляет <script src="common.js"></script> в <head>, перед </head>.
- Путь к common.js рассчитывается от HTML-файла до корня сайта.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Регулярка для <head>...</head>
HEAD_PATTERN = re.compile(r"(<head\b[^>]*>)(.*?)(</head>)", re.IGNORECASE | re.DOTALL)

# Регулярка для проверки, есть ли уже подключение common.js
HAS_COMMON_JS = re.compile(
    r'<script\b[^>]*\bsrc=["\'][^"\']*common\.js["\'][^>]*>',
    re.IGNORECASE
)

# Папки, которые пропускаем
SKIP_DIRS = {".git", "node_modules", ".github", "app"}


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def rel_path_to_common_js(html_file: Path) -> str:
    """Возвращает относительный путь от HTML-файла до common.js в корне."""
    rel = html_file.parent.relative_to(ROOT)
    depth = len(rel.parts)
    if depth == 0:
        return "common.js"
    return "../" * depth + "common.js"


def process_html(file: Path) -> bool:
    """Добавляет <script src="common.js"> в <head>. Возвращает True, если изменил."""
    try:
        content = file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ {file.relative_to(ROOT)} — ошибка чтения: {e}")
        return False

    # Уже подключён — пропускаем
    if HAS_COMMON_JS.search(content):
        return False

    # Нет <head> — пропускаем
    head_match = HEAD_PATTERN.search(content)
    if not head_match:
        print(f"⚠️  {file.relative_to(ROOT)} — нет <head>, пропускаем.")
        return False

    # Собираем путь к common.js
    script_src = rel_path_to_common_js(file)
    script_tag = f'    <script src="{script_src}"></script>\n'

    # Вставляем перед </head>
    head_open = head_match.group(1)
    head_content = head_match.group(2)
    head_close = head_match.group(3)

    new_head = head_open + head_content + script_tag + head_close

    # Заменяем в контенте
    new_content = content[:head_match.start()] + new_head + content[head_match.end():]

    if new_content != content:
        file.write_text(new_content, encoding="utf-8")
        print(f"✅ {file.relative_to(ROOT)} — подключён {script_src}")
        return True

    return False


def main():
    print("=" * 60)
    print("ПОДКЛЮЧЕНИЕ common.js ВО ВСЕ HTML")
    print("=" * 60)

    updated = 0
    skipped = 0

    for file in ROOT.rglob("*.html"):
        if is_skipped(file):
            continue

        if process_html(file):
            updated += 1
        else:
            skipped += 1

    print()
    print("=" * 60)
    print(f"Обновлено: {updated}")
    print(f"Пропущено: {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    main()