import json
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

ROOT = os.path.join(REPO_ROOT, 'Komorium')
IMAGES_DIR = os.path.join(REPO_ROOT, 'img')

def load_category_map():
    """Загружает словарь категорий из внешнего JSON‑файла."""
    map_path = os.path.join(SCRIPT_DIR, 'category_map.json')
    if os.path.isfile(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

CATEGORY_MAP = load_category_map()

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
    if existing_image:
        full_path = os.path.join(ROOT, existing_image)
        if os.path.isfile(full_path):
            return existing_image
        alt_path = os.path.join(REPO_ROOT, existing_image)
        if os.path.isfile(alt_path):
            return existing_image

    basename = os.path.basename(rel_path)
    for ext in ['.webp', '.png']:
        avatar_path = os.path.join(ROOT, rel_path, f'avatar{ext}')
        if os.path.isfile(avatar_path):
            return f"{rel_path}/avatar{ext}"
    for ext in ['.webp', '.png']:
        exact_match = os.path.join(IMAGES_DIR, f"{basename}{ext}")
        if os.path.isfile(exact_match):
            return f"../img/{basename}{ext}"
    if os.path.isdir(IMAGES_DIR):
        for fname in os.listdir(IMAGES_DIR):
            if not fname.lower().endswith(('.webp', '.png')):
                continue
            stem = fname.rsplit('.', 1)[0].lower()
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

            existing_entry = existing.get(url)
            if existing_entry:
                existing_image = existing_entry.get('image', '')
                if existing_image and os.path.isfile(os.path.join(ROOT, existing_image)):
                    image = existing_image
                else:
                    image = find_image(rel_path, existing_image)
            else:
                image = find_image(rel_path, '')

            articles.append({
                'title': title,
                'url': url,
                'category': category,
                'date': date,
                'image': image
            })
    return articles

def fix_broken_urls():
    """Однократное исправление дублирующихся папок в articles.json"""
    articles_path = os.path.join(REPO_ROOT, 'Komorium', 'articles.json')
    if not os.path.isfile(articles_path):
        return
    with open(articles_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    changed = False
    for article in data:
        url = article.get('url', '')
        parts = url.split('/')
        new_parts = []
        for p in parts:
            if p and new_parts and p == new_parts[-1]:
                continue
            new_parts.append(p)
        new_url = '/'.join(new_parts)
        if new_url != url:
            article['url'] = new_url
            changed = True
            print(f'Исправлен URL: {url} → {new_url}')

    if changed:
        with open(articles_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('✅ Неправильные ссылки исправлены в articles.json')
    else:
        print('✅ Все ссылки уже корректны')

def generate_sitemap(articles):
    base_url = "https://komorok.ru"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append(f"  <url><loc>{base_url}/</loc><priority>1.0</priority></url>")
    static_pages = [
        ('/about.html', '0.8'),
        ('/Alexander.html', '0.6'),
        ('/Komorium/', '0.9'),
    ]
    for path, priority in static_pages:
        lines.append(f"  <url><loc>{base_url}{path}</loc><priority>{priority}</priority></url>")
    for article in articles:
        loc = f"{base_url}/Komorium/{article['url']}"
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{article['date']}</lastmod><priority>0.7</priority></url>")
    lines.append('</urlset>')
    sitemap_path = os.path.join(REPO_ROOT, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"✅ sitemap.xml сгенерирован (статей: {len(articles)})")

if __name__ == '__main__':
    fix_broken_urls()
    articles = find_articles()
    out_path = os.path.join(REPO_ROOT, 'Komorium', 'articles.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Обновлено статей: {len(articles)}")
    generate_sitemap(articles)