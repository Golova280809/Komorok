#!/usr/bin/env python3
"""
Скрипт для автоматического добавления новеллы Мопассана на сайт.
Использование:
  python scripts/add_novel.py "https://ilibrary.ru/text/XXXX/p.1/index.html" "nazvanie-novelly"
"""

import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Корень проекта (на уровень выше папки scripts)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# Базовая папка для литературного раздела
LITERATURE_DIR = os.path.join(REPO_ROOT, 'Komorium', 'literature', 'gi-de-maupassant')

# Шаблон HTML-страницы новеллы
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <link rel="apple-touch-icon" href="../../../../logo.png">
    <link rel="icon" type="image/png" href="../../../../logo.png">

    <meta name="description" content="{title} — Ги де Мопассан. Полный текст новеллы.">
    <meta name="keywords" content="{title}, Мопассан, новелла, французская литература">
    <link rel="canonical" href="https://komorok.ru/Komorium/literature/gi-de-maupassant/{folder}/">

    <meta property="og:title" content="{title} — Ги де Мопассан | Komorok">
    <meta property="og:description" content="Полный текст новеллы «{title}» Ги де Мопассана.">
    <meta property="og:url" content="https://komorok.ru/Komorium/literature/gi-de-maupassant/{folder}/">
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
    <title>{title} — Ги де Мопассан | Komorok</title>
</head>
<body>
    <input type="checkbox" id="menu-toggle" class="menu-checkbox">
    <label for="menu-toggle" class="menu-toggle">
        <span></span><span></span><span></span>
    </label>

    <nav class="sidebar">
        <div class="sidebar-title">Меню</div>
        <a href="../../../../index.html">Главная</a>
        <a href="../../../index.html">Komorium</a>
        <a href="../../../../about.html">О проекте</a>
        <button class="theme-toggle-btn" id="themeToggle">
            <span class="icon">🌙</span>
            <span>Тёмная тема</span>
        </button>
    </nav>

    <label for="menu-toggle" class="overlay"></label>
    <button class="back-to-top" id="backToTop">↑</button>

    <main>
        <div class="top-menu">
            <a href="#about">О новелле</a>
            <a href="#text">Текст</a>
            <a href="#other">Другие произведения</a>
        </div>

        <h1 style="text-align: center;">📖 {title}</h1>
        <p style="text-align: center; margin-bottom: 2rem;">Ги де Мопассан</p>

        <section id="about" class="content-section">
            <h2>📜 О новелле</h2>
            <p>{description}</p>
        </section>

        <section id="text" class="content-section">
            <h2>📄 Текст новеллы</h2>
            {body}
        </section>

        <section id="other" class="content-section">
            <h2>📚 Другие произведения</h2>
            <div class="articles-grid">
                <a href="../index.html" class="article-card">
                    <img src="../../../../img/no-img.webp" alt="Мопассан" class="avatar">
                    <div class="card-content">
                        <span class="card-title">Ги де Мопассан: биография</span>
                        <span class="card-desc">Полная биография автора</span>
                    </div>
                </a>
                <a href="../pyshka/index.html" class="article-card">
                    <img src="../../../../img/no-img.webp" alt="Пышка" class="avatar">
                    <div class="card-content">
                        <span class="card-title">Пышка</span>
                        <span class="card-desc">Новелла (1880)</span>
                    </div>
                </a>
            </div>
        </section>
    </main>
    <footer class="footer">
        <p>© 2026 Komorok — Литературный раздел</p>
    </footer>
    <script src="../../../../script.js"></script>
</body>
</html>
"""

def fetch_text(url):
    """Скачивает текст новеллы с переданного URL."""
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    # Попробуем найти основной текст (для ilibrary.ru это div с классом 'text')
    content = soup.find('div', class_='text')
    if not content:
        # Запасной вариант: любой большой div
        content = soup.find('div')
    # Извлекаем текст с абзацами
    paragraphs = content.find_all('p')
    text = '\n'.join(p.get_text() for p in paragraphs)
    # Название обычно в h1
    title_tag = soup.find('h1')
    title = title_tag.get_text().strip() if title_tag else "Без названия"
    return title, text

def format_body(text):
    """Преобразует текст в HTML-абзацы."""
    return '\n'.join(f'<p>{para}</p>' for para in text.split('\n') if para.strip())

def update_articles_json(title, folder):
    """Добавляет запись в articles.json."""
    json_path = os.path.join(REPO_ROOT, 'Komorium', 'articles.json')
    import json
    with open(json_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    # Проверим, нет ли уже такой записи
    url = f"literature/gi-de-maupassant/{folder}/"
    for art in articles:
        if art.get('url') == url:
            print(f"Статья уже существует: {url}")
            return
    articles.append({
        "title": title,
        "url": url,
        "category": "works",
        "date": "2026-05-06",
        "image": ""  # можно будет потом добавить
    })
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"✅ Добавлено в articles.json: {title}")

def update_sitemap():
    """Вызывает генерацию sitemap.xml (использует функцию из update_articles_list)."""
    # Просто импортируем и вызываем generate_sitemap из соседнего скрипта
    sys.path.insert(0, os.path.join(REPO_ROOT, 'scripts'))
    from update_articles_list import find_articles, generate_sitemap
    articles = find_articles()
    generate_sitemap(articles)

def main():
    if len(sys.argv) < 3:
        print("Использование: python add_novel.py <URL> <название_папки>")
        sys.exit(1)
    
    url = sys.argv[1]
    folder_name = sys.argv[2]
    
    # Скачиваем и обрабатываем текст
    print(f"Скачиваю текст с {url}...")
    title, text = fetch_text(url)
    print(f"Название: {title}")
    print(f"Длина текста: {len(text)} символов")
    
    # Создаём папку для новеллы
    novel_dir = os.path.join(LITERATURE_DIR, folder_name)
    os.makedirs(novel_dir, exist_ok=True)
    
    # Генерируем HTML
    # Добавляем описание по умолчанию (можно улучшить)
    description = f"Новелла «{title}» — одно из известных произведений Ги де Мопассана. Здесь представлен полный текст."
    body_html = format_body(text)
    html_content = HTML_TEMPLATE.format(
        title=title,
        folder=folder_name,
        description=description,
        body=body_html
    )
    
    # Записываем index.html
    index_path = os.path.join(novel_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Создана страница: {index_path}")
    
    # Обновляем articles.json
    update_articles_json(title, folder_name)
    
    # Обновляем sitemap.xml
    update_sitemap()
    print("✅ sitemap.xml обновлён")
    
    print("\n🎉 Готово! Осталось сделать git add, commit и push.")

if __name__ == '__main__':
    main()