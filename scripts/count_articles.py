# count_articles.py
# Автоматически подсчитывает все статьи в энциклопедии и обновляет счётчик.

import os
import re
from pathlib import Path

# 1. Корневая папка энциклопедии (относительно корня репозитория)
ARTICLES_ROOT = "Komorium"
HTML_FILE = Path("index.html")


def count_articles() -> int:
    """Рекурсивно считает index.html внутри Komorium, кроме самого Komorium/index.html."""
    count = 0
    for root, dirs, files in os.walk(ARTICLES_ROOT):
        for file in files:
            if file == "index.html" and root != ARTICLES_ROOT:
                count += 1
    return count


def articles_word(n: int) -> str:
    """Правильное склонение слова 'статья'."""
    n10 = n % 10
    n100 = n % 100
    if n100 in (11, 12, 13, 14):
        return "статей"
    if n10 == 1:
        return "статья"
    if n10 in (2, 3, 4):
        return "статьи"
    return "статей"


def main():
    count = count_articles()
    word = articles_word(count)
    print(f"Найдено статей: {count}")

    if not HTML_FILE.exists():
        print(f"⚠️ Файл {HTML_FILE} не найден.")
        return

    content = HTML_FILE.read_text(encoding="utf-8")

    # Регулярка ищет: <!-- articles-count --> ... <p>В энциклопедии N статей</p>
    pattern = re.compile(
        r"(<!-- articles-count -->\s*<p>В энциклопедии\s*)\d+(\s*стат\w*)",
        re.UNICODE
    )

    new_content, subs = pattern.subn(rf"\g<1>{count} {word}", content)

    if subs == 0:
        print("⚠️ Строка со счётчиком статей не найдена в index.html.")
        print("   Проверьте, что над <p>В энциклопедии N статей есть <!-- articles-count -->.")
        return

    if new_content == content:
        print(f"ℹ️ Изменений нет — уже {count} {word}.")
        return

    HTML_FILE.write_text(new_content, encoding="utf-8")
    print(f"✅ Главная обновлена! Статей: {count} ({word}).")


if __name__ == "__main__":
    main()