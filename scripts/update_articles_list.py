import json
import os
import re
from datetime import datetime

# Определяем корень репозитория: на уровень выше папки scripts/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

ROOT = os.path.join(REPO_ROOT, 'Komorium')
IMAGES_DIR = os.path.join(REPO_ROOT, 'img')

CATEGORY_MAP = {
    'China': 'countries',
    'bazanovo': 'villages',
    'bazanovo/Gungunzhda': 'nature',
    'bazanovo/people': 'voices',
    'Technology/html-course': 'languages',
    'Technology/css-course': 'languages',
    'Technology/python-course': 'languages',
    'Technology/termux-intro': 'termux',
    'Technology/termux-python': 'termux',
    'Technology/termux-git': 'termux',
    'Technology/termux-linkcheck': 'termux',
    'Technology/termux-server': 'termux',
    'Technology/termux-abc': 'termux',
}

def get_category(rel_path):
    best = None
    for path, cat in CATEGORY_MAP.items():
        if rel_path.startswith(path):
            if best is None or len(path) > len(best[0]):
                best = (path, cat)
    return best[1] if best else 'other'

def get_title_and_date(html_file):
    title = os.path.basename(os.path.dirname(html_file))
    try:
        mtime = os.path.getmtime(html_file)
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except:
        date = datetime.now().strftime('%Y-%m-%d')
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
        if match:
            title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
    except:
        pass
    return title, date

def find_image(rel_path, existing_image):
    if existing_image and os.path.isfile(os.path.join(ROOT, existing_image)):
        return existing_image

    basename = os.path.basename(rel_path)
    avatar_path = os.path.join(ROOT, rel_path, 'avatar.png')
    if os.path.isfile(avatar_path):
        return f"{rel_path}/avatar.png"

    exact_match = os.path.join(IMAGES_DIR, f"{basename}.png")
    if os.path.isfile(exact_match):
        return f"../img/{basename}.png"

    if os.path.isdir(IMAGES_DIR):
        for fname in os.listdir(IMAGES_DIR):
            if not fname.lower().endswith('.png'):
                continue
            stem = fname[:-4].lower()
            if stem in basename.lower() or basename.lower() in stem:
                return f"../img/{fname}"
    return ""

def load_existing_articles():
    articles_path = os.path.join(REPO_ROOT, 'Komorium', 'articles.json')
    if not os.path.isfile(articles_path):
        return {}
    with open(articles_path, 'r', encoding='utf-8') as f:
        return {a['url']: a for a in json.load(f)}

def find_articles():
    existing = load_existing_articles()
    articles = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if 'index.html' in filenames and dirpath != ROOT:
            rel_path = os.path.relpath(dirpath, ROOT)
            title, date = get_title_and_date(os.path.join(dirpath, 'index.html'))
            category = get_category(rel_path)
            url = f"{rel_path}/"
            prev_image = existing.get(url, {}).get('image', '')
            image = find_image(rel_path, prev_image)
            articles.append({
                'title': title,
                'url': url,
                'category': category,
                'date': date,
                'image': image
            })
    return articles

def generate_sitemap(articles):
    """Создаёт sitemap.xml в корне репозитория на основе списка статей."""
    base_url = "https://komorok.ru"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Главная страница
    lines.append(f"  <url><loc>{base_url}/</loc><priority>1.0</priority></url>")
    
    # Статические страницы
    static_pages = [
        ('/', '1.0'),
        ('/about.html', '0.8'),
        ('/Alexander.html', '0.6'),
        ('/Komorium/', '0.9'),
    ]
    for path, priority in static_pages:
        lines.append(f"  <url><loc>{base_url}{path}</loc><priority>{priority}</priority></url>")
    
    # Все статьи из articles.json
    for article in articles:
        loc = f"{base_url}/Komorium/{article['url']}"
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{article['date']}</lastmod><priority>0.7</priority></url>")
    
    lines.append('</urlset>')
    
    sitemap_path = os.path.join(REPO_ROOT, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"✅ sitemap.xml сгенерирован (статей: {len(articles)})")

if __name__ == '__main__':
    articles = find_articles()
    out_path = os.path.join(REPO_ROOT, 'Komorium', 'articles.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Обновлено статей: {len(articles)}")
    
    generate_sitemap(articles)