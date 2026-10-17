# update_days.py
# Обновляет счётчик дней с момента рождения проекта Komorok.

import datetime
import re
from pathlib import Path

# Дата рождения проекта (первый коммит — 29 марта 2026)
BIRTHDAY = datetime.date(2026, 3, 29)
TODAY = datetime.date.today()
DAYS = (TODAY - BIRTHDAY).days

# Путь к главной странице (относительно корня репозитория)
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

    # utf-8-sig автоматически снимает BOM, если он есть
    content = HTML_FILE.read_text(encoding="utf-8-sig")

    # Заменяем невидимые пробелы на обычные
    for invisible in ("\u00a0", "\u2009", "\u202f", "\u2007", "\u2008"):
        content = content.replace(invisible, " ")

    word = days_word(DAYS)

    # Гибкая регулярка:
    # — комментарий с любыми пробелами
    # — <p> с любым содержимым до слова «прошло»
    # — «прошло», необязательное двоеточие, любые пробелы
    # — число (заменяем)
    # — слово «день/дня/дней» (тоже заменяем)
    pattern = re.compile(
        r"(<!--\s*project-age-counter\s*-->\s*<p>[^<]*?прошло\s*:?\s*)\d+(\s*дн\w*)",
        re.UNICODE
    )

    new_content, count = pattern.subn(rf"\g<1>{DAYS} {word}", content)

    if count == 0:
        print("⚠️ Строка со счётчиком дней не найдена в index.html.")
        print("   Проверьте кодировку и скрытые символы.")
        return

    if new_content == content:
        print(f"ℹ️ Изменений нет — уже {DAYS} {word}.")
        return

    HTML_FILE.write_text(new_content, encoding="utf-8")
    print(f"✅ Обновлено! Проекту уже {DAYS} {word}.")


if __name__ == "__main__":
    main()