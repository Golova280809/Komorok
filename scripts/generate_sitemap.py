import os
from datetime import datetime

ROOT = 'Komorium'
BASE_URL = 'https://komorok.ru'

def get_modification_date(path):
    """Возвращает дату последнего изменения файла в формате YYYY-MM-DD."""
    try:
        mtime = os.path.getmtime(path)
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except:
        return '2026-05-04'  # на случай ошибки

def generate_sitemap():
    urls = []

    # Главная страница сайта
    urls.append((f'{BASE_URL}/', '1.0', get_modification_date('index.html')))

    # Основные статические страницы
    static_pages = [
        ('/about.html', '0.8'),
        ('/Alexander.html', '0.6'),
        ('/Komorium/', '0.9'),
    ]
    for path, priority in static_pages:
        full_path = path.lstrip('/')
        urls.append((f'{BASE_URL}{path}', priority, get_modification_date(full_path)))

    # Все статьи из Komorium (ищем index.html в подпапках)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if 'index.html' in filenames and dirpath != ROOT:
            rel_path = os.path.relpath(dirpath, ROOT)
            url = f'{BASE_URL}/{ROOT}/{rel_path}/'
            full_path = os.path.join(dirpath, 'index.html')
            urls.append((url, '0.7', get_modification_date(full_path)))

    # Генерируем XML
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, priority, lastmod in urls:
        lines.append(f'  <url>')
        lines.append(f'    <loc>{loc}</loc>')
        lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines.append(f'    <priority>{priority}</priority>')
        lines.append(f'  </url>')
    lines.append('</urlset>')

    # Записываем в корень репозитория
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'✅ sitemap.xml сгенерирован, статей: {len(urls)-4} (плюс основные страницы)')

if __name__ == '__main__':
    generate_sitemap()