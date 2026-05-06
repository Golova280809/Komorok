#!/usr/bin/env python3
"""
Скрипт для создания HTML-страницы новеллы с nukadeti.ru.
Ссылка уже вшита в код — просто запусти.
"""

import os
import requests
from bs4 import BeautifulSoup

# === ВСТАВЬ ССЫЛКУ СЮДА ===
URL = "https://nukadeti.ru/rasskazy/mopassan-rozhdestvenskaya-skazka"
# ===========================

# Папка, куда сохранять
LITERATURE_DIR = os.path.join('Komorium', 'literature', 'gi-de-maupassant')

HTML_TEMPLATE = '''<!DOCTYPE html>
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
    <footer class="footer"><p>© 2026 Komorok — Литературный раздел</p></footer>
    <script src="../../../../script.js"></script>
</body>
</html>'''

# === ПОЕХАЛИ ===
folder_name = URL.rstrip('/').split('/')[-1]
print(f"📥 Загружаю: {URL}")

resp = requests.get(URL, timeout=15)
resp.encoding = resp.apparent_encoding
soup = BeautifulSoup(resp.text, 'html.parser')

# Заголовок
title_tag = soup.find('h1')
title = title_tag.get_text().strip() if title_tag else "Без названия"

# Текст
text_block = soup.find('div', class_='story-text')
paragraphs = text_block.find_all('p')
text = '\n'.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

print(f"📖 Название: {title}")
print(f"📁 Папка: {folder_name}")
print(f"📏 Длина текста: {len(text)} символов")

# Форматируем
body_html = '\n'.join(f'<p>{p}</p>' for p in text.split('\n') if p)
description = f"Новелла «{title}» — одно из известных произведений Ги де Мопассана. Здесь представлен полный текст."

# Создаём
novel_dir = os.path.join(LITERATURE_DIR, folder_name)
os.makedirs(novel_dir, exist_ok=True)

html = HTML_TEMPLATE.format(title=title, folder=folder_name, description=description, body=body_html)

index_path = os.path.join(novel_dir, 'index.html')
with open(index_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ Страница создана: {index_path}")
print(f"🎉 Готово!")