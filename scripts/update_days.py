# update_days.py
# Обновляет счётчик дней с момента рождения проекта Komorok.

import datetime
import re
from pathlib import Path

# 1. Дата рождения проекта (первый коммит — 29 марта 2026)
BIRTHDAY = datetime.date(2026, 3, 29)
TODAY = datetime.date.today()
DAYS = (TODAY - BIRTHDAY).days

# 2. Путь к главной странице (относительно корня репозитория)
HTML_FILE = Path("index.html")


def days_word(n: int) -> str:
    """Правильное склонение слова 'день'."""
    n10 = n % 10
    n100 = n % 100
    if n100 in (11, 12, 13, 14):
        return "дней"
    if n10 == 1:
        return "день"
    if n10 in (2, 3, 4):
        return "дня"
    return "дней"


def main():
    if not HTML_FILE.exists():
        print(f"⚠️ Файл {HTML_FILE} не найден.")
        return

    content = HTML_FILE.read_text(encoding="utf-8")

    word = days_word(DAYS)
    pattern = re.compile(
        r"(<!-- project-age-counter -->\s*<p>С момента запуска сайта прошло:\s*)\d+(\s*дн\w*)",
        re.UNICODE
    )

    new_content, count = pattern.subn(rf"\g<1>{DAYS} {word}", content)

    if count == 0:
        print("⚠️ Строка со счётчиком дней не найдена в index.html.")
        print("   Проверьте, что над <p> есть комментарий <!-- project-age-counter -->.")
        return

    if new_content == content:
        print(f"ℹ️ Изменений нет — уже {DAYS} {word}.")
        return

    HTML_FILE.write_text(new_content, encoding="utf-8")
    print(f"✅ Обновлено! Проекту уже {DAYS} {word}.")


if __name__ == "__main__":
    main()