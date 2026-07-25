import json
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

ROOT = os.path.join(REPO_ROOT, 'Komorium')
IMAGES_DIR = os.path.join(REPO_ROOT, 'img')

def load_category_map():
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

def get_title_and_meta_description(html_file):
    """Извлекает заголовок из <h1> и описание из <meta name='description'>."""
    title = os.path.basename(os.path.dirname(html_file))
    description = ""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Заголовок (h1)
        match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE)
        if match:
            title = re.sub(r'<[^>]+>', '', match.group(1)).strip()

        # Описание из meta-description
        meta_match = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
            content, re.IGNORECASE
        )
        if meta_match:
            description = meta_match.group(1).strip()
    except:
        pass

    # Дата по времени изменения файла
    try:
        mtime = os.path.getmtime(html_file)
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except:
        date = datetime.now().strftime('%Y-%m-%d')

    return title, date, description

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
            html_path = os.path.join(dirpath, 'index.html')

            title, date, auto_description = get_title_and_meta_description(html_path)
            category = get_category(rel_path)
            url = f"{rel_path}/"

            existing_entry = existing.get(url)
            if existing_entry:
                # сохраняем ручное описание, если было, иначе берём из meta
                description = existing_entry.get('description', '')
                if not description:
                    description = auto_description
                # изображение тоже стараемся сохранить существующее
                existing_image = existing_entry.get('image', '')
                if existing_image and os.path.isfile(os.path.join(ROOT, existing_image)):
                    image = existing_image
                else:
                    image = find_image(rel_path, existing_image)
            else:
                description = auto_description
                image = find_image(rel_path, '')

            articles.append({
                'title': title,
                'url': url,
                'category': category,
                'date': date,
                'image': image,
                'description': description
            })
    return articles

# ... (остальные функции fix_broken_urls и generate_sitemap без изменений) ...

if __name__ == '__main__':
    fix_broken_urls()
    articles = find_articles()
    out_path = os.path.join(REPO_ROOT, 'Komorium', 'articles.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Обновлено статей: {len(articles)}")
    generate_sitemap(articles)