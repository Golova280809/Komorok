import json
import os
import re
from datetime import datetime

ROOT = 'Komorium'
IMAGES_DIR = 'img'  # общая папка с изображениями в корне проекта

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
    """
    Ищет изображение для статьи.
    1. Если existing_image не пусто и файл существует, возвращаем его без изменений.
    2. Иначе ищем avatar.png в папке статьи.
    3. Если нет – ищем в общей папке img/ файл, имя которого соответствует последней части rel_path.
       Например, для 'Technology/termux-intro' будет искать 'img/termux-intro.png'.
    4. Если ничего не найдено, возвращаем пустую строку.
    """
    # Если уже задано вручную и файл существует – сохраняем
    if existing_image and os.path.isfile(existing_image):
        return existing_image

    # 1. avatar.png в папке статьи
    avatar_path = os.path.join(ROOT, rel_path, 'avatar.png')
    if os.path.isfile(avatar_path):
        return f"{rel_path}/avatar.png"

    # 2. Поиск в общей папке img/ по имени подпапки статьи
    folder_name = os.path.basename(rel_path)  # например, 'termux-intro'
    candidate = os.path.join(IMAGES_DIR, f"{folder_name}.png")
    if os.path.isfile(candidate):
        return f"{IMAGES_DIR}/{folder_name}.png"

    # 3. Альтернативные расширения можно добавить позже
    return ""

def load_existing_articles():
    """Загружает существующий articles.json, чтобы сохранить вручную установленные изображения."""
    if not os.path.isfile('Komorium/articles.json'):
        return {}
    with open('Komorium/articles.json', 'r', encoding='utf-8') as f:
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
            # Сохраняем предыдущее изображение, если оно было задано вручную
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

if __name__ == '__main__':
    articles = find_articles()
    with open('Komorium/articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Обновлено статей: {len(articles)}")