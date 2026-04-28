import json
import os
import re
from datetime import datetime

ROOT = 'Komorium'

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

def find_articles():
    articles = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if 'index.html' in filenames and dirpath != ROOT:
            rel_path = os.path.relpath(dirpath, ROOT)
            title, date = get_title_and_date(os.path.join(dirpath, 'index.html'))
            category = get_category(rel_path)
            avatar_path = os.path.join(dirpath, 'avatar.png')
            image_url = f"{rel_path}/avatar.png" if os.path.exists(avatar_path) else ""
            articles.append({
                'title': title,
                'url': f"{rel_path}/",
                'category': category,
                'date': date,
                'image': image_url
            })
    return articles

if __name__ == '__main__':
    articles = find_articles()
    with open('Komorium/articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Обновлено статей: {len(articles)}")