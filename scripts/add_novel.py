#!/usr/bin/env python3
"""
Универсальный скрипт для создания HTML-страницы рассказа с nukadeti.ru.
Автоматически определяет автора и создаёт правильную структуру папок.
Ссылка уже в коде — просто запусти.
"""

import os
import re
import requests
from bs4 import BeautifulSoup

# ⚠️ ВСТАВЬ НУЖНУЮ ССЫЛКУ СЮДА
URL = "https://nukadeti.ru/rasskazy/zhizn-i-vorotnik"

# Корень литературы
LITERATURE_DIR = os.path.join('Komorium', 'literature')

# Таблица транслитерации (только для имени автора, папка рассказа берётся из URL)
RUS_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    ' ': '-', '_': '-', ',': '', '.': '', '!': '', '?': '', ':': '',
    '«': '', '»': '', "'": '', '"': '', '–': '-', '—': '-'
}

def transliterate(text):
    """Транслитерация русского текста в латиницу."""
    slug = ''
    for ch in text.lower():
        slug += RUS_TO_LAT.get(ch, ch)
    slug = re.sub(r'-{2,}', '-', slug)
    return slug.strip('-')

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <link rel="apple-touch-icon" href="../../../../logo.png">
    <link rel="icon" type="image/png" href="../../../../logo.png">
    <meta name="description" content="{title} — {author}. Полный текст рассказа.">
    <meta name="keywords" content="{title}, {author}, рассказ, литература">
    <link rel="canonical" href="https://komorok.ru/Komorium/literature/{author_folder}/{folder}/">
    <meta property="og:title" content="{title} — {author} | Komorok">
    <meta property="og:description" content="Полный текст рассказа «{title}» ({author}).">
    <meta property="og:url" content="https://komorok.ru/Komorium/literature/{author_folder}/{folder}/">
    <meta property="og:image" content="https://komorok.ru/img/no-img.webp">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Komorok">
    <script>
        (function() {{
            var theme = localStorage.getItem('theme');
            if (theme === 'dark') {{
                document.documentElement.classList.add('dark-theme');
            }}
        }})();
    </script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../../../../common.css">
    <link rel="stylesheet" href="../../../komorium.css">
    <title>{title} — {author} | Komorok</title>
</head>
<body>
    <input type="checkbox" id="menu-toggle" class="menu-checkbox">
    <label for="menu-toggle" class="menu-toggle"><span></span><span></span><span></span></label>
    <nav class="sidebar">
        <div class="sidebar-title">Меню</div>
        <a href="../../../../index.html">Главная</a>
        <a href="../../../index.html">Komorium</a>
        <a href="../../../../about.html">О проекте</a>
        <button class="theme-toggle-btn" id="themeToggle">
            <span class="icon">🌙</span><span>Тёмная тема</span>
        </button>
    </nav>
    <label for="menu-toggle" class="overlay"></label>
    <button class="back-to-top" id="backToTop">↑</button>
    <main>
        <div class="top-menu">
            <a href="#about">О рассказе</a>
            <a href="#text">Текст</a>
            <a href="#other">Другие произведения</a>
        </div>
        <h1 style="text-align: center;">📖 {title}</h1>
        <p style="text-align: center; margin-bottom: 2rem;">{author}</p>
        <section id="about" class="content-section">
            <h2>📜 О рассказе</h2>
            <p>{description}</p>
        </section>
        <section id="text" class="content-section">
            <h2>📄 Текст рассказа</h2>
            {body}
        </section>
        <section id="other" class="content-section">
            <h2>📚 Другие произведения</h2>
            <div class="articles-grid">
                <a href="../index.html" class="article-card">
                    <img src="../../../../img/no-img.webp" alt="{author}" class="avatar">
                    <div class="card-content">
                        <span class="card-title">{author}: биография</span>
                        <span class="card-desc">Страница автора</span>
                    </div>
                </a>
            </div>
        </section>
    </main>
    <footer class="footer"><p>© 2026 Komorok — Литературный раздел</p></footer>
    <script src="../../../../script.js"></script>
</body>
</html>'''

# ------------------- ПОЕХАЛИ -------------------
folder_name = URL.rstrip('/').split('/')[-1]
print(f"📥 Загружаю: {URL}")

resp = requests.get(URL, timeout=15)
resp.encoding = resp.apparent_encoding
soup = BeautifulSoup(resp.text, 'html.parser')

# Заголовок
title_tag = soup.find('h1')
title = title_tag.get_text().strip() if title_tag else "Без названия"

# Автор: ищем в a.aut, span.aut, или берём из <title>
author_tag = (
    soup.find('a', class_='aut') or   # ← новый формат (Тэффи)
    soup.find('span', class_='aut')   # ← старый формат (Мопассан)
)
if author_tag:
    author = author_tag.get_text().strip()
else:
    # Запасной вариант: парсим <title>
    title_text = soup.find('title')
    if title_text:
        title_str = title_text.get_text()
        # "Жизнь и воротник - рассказ Н. Тэффи, читать онлайн"
        if ' - ' in title_str:
            parts = title_str.split(' - ')
            if len(parts) >= 2:
                second = parts[1].strip()
                # "рассказ Н. Тэффи, читать онлайн" → "Н. Тэффи"
                author = second.replace('рассказ ', '').replace(', читать онлайн', '').strip()
            else:
                author = "Неизвестный автор"
        else:
            author = "Неизвестный автор"
    else:
        author = "Неизвестный автор"

print(f"🖋️ Автор: {author}")

# Транслитерируем папку автора
author_folder = transliterate(author)
print(f"📁 Папка автора: {author_folder}")

# Поиск текста
text_block = (
    soup.find('div', class_='tale-text') or
    soup.find('div', class_='story-text') or
    soup.find('div', class_='text') or
    soup.find('div', class_='content') or
    soup.find('article') or
    soup.find('div', class_='entry-content') or
    soup.find('main')
)

if not text_block:
    print("❌ Не удалось найти блок с текстом на странице.")
    exit(1)

paragraphs = text_block.find_all('p')
text = '\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

if not text:
    print("❌ Текст пуст.")
    exit(1)

print(f"📖 Название: {title}")
print(f"📁 Папка рассказа: {folder_name}")
print(f"📏 Длина текста: {len(text)} символов")

# Форматируем
body_html = '\n'.join(f'<p>{p}</p>' for p in text.split('\n') if p)
description = f"Рассказ «{title}» ({author}). Здесь представлен полный текст."

# Создаём папки
author_dir = os.path.join(LITERATURE_DIR, author_folder)
novel_dir = os.path.join(author_dir, folder_name)
os.makedirs(novel_dir, exist_ok=True)

html = HTML_TEMPLATE.format(
    title=title,
    author=author,
    author_folder=author_folder,
    folder=folder_name,
    description=description,
    body=body_html
)

index_path = os.path.join(novel_dir, 'index.html')
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Страница создана: {index_path}")

# Попытаемся добавить карточку в биографию автора, если она существует
author_page = os.path.join(author_dir, 'index.html')
if os.path.exists(author_page):
    print("📝 Найдена страница автора, добавляю карточку...")
    with open(author_page, 'r', encoding='utf-8') as f:
        content = f.read()

    card = f'''                <a href="{folder_name}/" class="article-card">
                    <img src="../../img/no-img.webp" alt="{title}" class="avatar">
                    <div class="card-content">
                        <span class="card-title">{title}</span>
                        <span class="card-desc">Рассказ</span>
                    </div>
                </a>'''

    pattern = r'(<div class="articles-grid">.*?)(</div>)'
    new_content = re.sub(pattern, r'\1' + card + r'\n\2', content, count=1, flags=re.DOTALL)
    if new_content != content:
        with open(author_page, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Карточка добавлена в биографию автора.")
    else:
        print("⚠️ Не удалось вставить карточку в биографию.")
else:
    print("ℹ️ Страница автора ещё не создана. При желании создайте её вручную.")

print("🎉 Готово!")