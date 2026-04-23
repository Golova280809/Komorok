# update_stats.py
# Этот скрипт обновляет статистику на главной странице Komorok.
# GitHub Actions будет запускать его автоматически.

import datetime
import re
import os

# 1. Вычисляем, сколько дней прошло с начала 2026 года
today = datetime.date.today()
start_of_year = datetime.date(2026, 1, 1)
days_passed = (today - start_of_year).days

# 2. Путь к главной странице сайта
html_file = "index.html"

# 3. Читаем текущее содержимое index.html
with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

# 4. Ищем и заменяем строчку со счётчиком дней
#    Мы будем искать специальный комментарий <!-- days-counter --> и менять число рядом с ним.
pattern = r"(<!-- days-counter -->\s*<p>С начала года прошло: )\d+( дней</p>)"
replacement = rf"\g<1>{days_passed}\g<2>"

new_content = re.sub(pattern, replacement, content)

# 5. Если ничего не изменилось (например, счётчик уже правильный), не делаем коммит
if new_content == content:
    print("Изменений нет, выходим.")
    exit(0)

# 6. Записываем обновлённый HTML обратно
with open(html_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Обновлено! Дней с начала года: {days_passed}")