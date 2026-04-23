# update_stats.py
# Обновляет счётчик дней с момента рождения проекта Komorok (01.01.2026)

import datetime
import re

# 1. Дата рождения проекта
birthday = datetime.date(2025, 2, 25)
today = datetime.date.today()
days_since_birth = (today - birthday).days

# 2. Путь к главной странице
html_file = "index.html"

# 3. Читаем текущий index.html
with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

# 4. Ищем и заменяем строчку со счётчиком
#    Комментарий должен быть: <!-- project-age-counter -->
pattern = r"(<!-- project-age-counter -->\s*<p>С момента рождения проекта прошло: )\d+( дней</p>)"
replacement = rf"\g<1>{days_since_birth}\g<2>"

new_content = re.sub(pattern, replacement, content)

# 5. Если изменений нет — выходим
if new_content == content:
    print("Изменений нет.")
    exit(0)

# 6. Сохраняем
with open(html_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Обновлено! Проекту уже {days_since_birth} дней.")