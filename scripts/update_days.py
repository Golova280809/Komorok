# update_days.py
# Обновляет счётчик дней с момента рождения проекта Komorok.
# С отладкой — показывает, что видит в index.html.

import datetime
import re
from pathlib import Path

# Дата рождения проекта (первый коммит — 29 марта 2026)
BIRTHDAY = datetime.date(2026, 3, 29)
TODAY = datetime.date.today()
DAYS = (TODAY - BIRTHDAY).days

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


def debug_print(content: str):
    """Печатает, что видно в файле — для отладки."""
    print("=" * 60)
    print("ОТЛАДКА")
    print("=" * 60)
    print(f"Размер файла: {len(content)} символов")
    print(f"Файл существует: {HTML_FILE.exists()}")

    # Ищем все строки с нужными маркерами
    lines = content.split("\n")
    print(f"\nВсего строк: {len(lines)}")
    print("\nСтроки с 'project-age-counter' или 'прошло':")

    found_any = False
    for i, line in enumerate(lines, 1):
        if "project-age-counter" in line or "прошло" in line:
            found_any = True
            print(f"  Строка {i}: {repr(line)}")

    if not found_any:
        print("  ❌ НИЧЕГО НЕ НАЙДЕНО")

    # Проверяем отдельные подстроки
    print("\nПроверка подстрок:")
    print(f"  'project-age-counter': {'project-age-counter' in content}")
    print(f"  '<!-- project-age-counter -->': {'<!-- project-age-counter -->' in content}")
    print(f"  'С момента запуска': {'С момента запуска' in content}")
    print(f"  'прошло': {'прошло' in content}")
    print(f"  'дней': {'дней' in content}")
    print(f"  'день': {'день' in content}")
    print(f"  'дня': {'дня' in content}")

    # Ищем невидимые символы
    print("\nПроверка невидимых символов в файле:")
    invisible_found = False
    for ch, name in [
        ("\u00a0", "NBSP (неразрывный пробел)"),
        ("\u2009", "THIN SPACE (тонкий пробел)"),
        ("\u202f", "NARROW NBSP (узкий неразрывный)"),
        ("\ufeff", "BOM (byte order mark)"),
        ("\u200b", "ZERO WIDTH SPACE (нулевой ширины)"),
        ("\u2013", "EN DASH (среднее тире)"),
        ("\u2014", "EM DASH (длинное тире)"),
    ]:
        count = content.count(ch)
        if count > 0:
            invisible_found = True
            print(f"  ⚠️ {name}: {count} шт.")
    if not invisible_found:
        print("  ✅ Невидимых символов не найдено")

    print("=" * 60)


def main():
    if not HTML_FILE.exists():
        print(f"⚠️ Файл {HTML_FILE} не найден.")
        print(f"   Текущая директория: {Path.cwd()}")
        return

    # Читаем с utf-8-sig (снимает BOM в начале)
    content = HTML_FILE.read_text(encoding="utf-8-sig")

    # === ОТЛАДКА ===
    debug_print(content)

    # Нормализуем все возможные невидимые символы
    invisible_chars = [
        "\u00a0", "\u2007", "\u2008", "\u2009", "\u200a",
        "\u202f", "\u205f", "\u3000", "\ufeff",
        "\u200b", "\u200c", "\u200d", "\u2060"
    ]
    for ch in invisible_chars:
        content = content.replace(ch, " ")

    # === ПОИСК БЛОКА ПО КОММЕНТАРИЮ ===
    start_marker = "<!-- project-age-counter -->"
    start_idx = content.find(start_marker)

    if start_idx == -1:
        print("\n❌ Комментарий <!-- project-age-counter --> НЕ НАЙДЕН.")
        print("   Возможно, он есть, но с невидимыми символами.")
        print("   Проверьте отладочный вывод выше.")
        return

    # Ищем <p> после комментария (в пределах 500 символов)
    p_start = content.find("<p>", start_idx)
    if p_start == -1 or p_start - start_idx > 500:
        print("\n❌ Тег <p> после комментария НЕ НАЙДЕН.")
        print(f"   Комментарий на позиции {start_idx}")
        print(f"   Ближайший <p> на позиции {p_start}")
        return

    # Ищем </p> после <p>
    p_end = content.find("</p>", p_start)
    if p_end == -1:
        print("\n❌ Закрывающий тег </p> НЕ НАЙДЕН.")
        return

    # Формируем новую строку
    word = days_word(DAYS)
    new_text = f"<p>С момента запуска сайта прошло: {DAYS} {word}</p>"

    old_text = content[p_start:p_end + 4]

    print(f"\n📝 БЫЛО:  {repr(old_text)}")
    print(f"📝 СТАЛО: {repr(new_text)}")

    if old_text == new_text:
        print(f"\nℹ️ Изменений нет — уже {DAYS} {word}.")
        return

    # Заменяем
    new_content = content[:p_start] + new_text + content[p_end + 4:]

    HTML_FILE.write_text(new_content, encoding="utf-8")
    print(f"\n✅ ОБНОВЛЕНО! Проекту уже {DAYS} {word}.")


if __name__ == "__main__":
    main()