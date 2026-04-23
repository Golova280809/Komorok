# count_articles.py
# Автоматически подсчитывает все статьи в энциклопедии и обновляет счётчик.

import os
import re

# 1. Корневая папка энциклопедии
articles_root = "Komorium"

# 2. Рекурсивно находим все index.html, исключая главную страницу энциклопедии
count = 0
for root, dirs, files in os.walk(articles_root):
    for file in files:
        if file == "index.html":
            # Пропускаем саму главную страницу Komorium/index.html
            if root == articles_root:
                continue
            count += 1

print(f"Найдено статей: {count}")

# 3. Обновляем index.html (главную страницу сайта)
html_file = "index.html"
with open(html_file, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"(<!-- articles-count -->\s*<p>В энциклопедии уже )\d+( статей</p>)"
replacement = rf"\g<1>{count}\g<2>"

new_content = re.sub(pattern, replacement, content)

if new_content == content:
    print("Количество статей не изменилось.")
    exit(0)

with open(html_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Главная страница обновлена! Статей: {count}")