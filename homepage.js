// homepage.js — динамика для главной страницы Komorok
(function () {
    if (typeof articlesData === 'undefined') return;

    function formatDate(iso) {
        if (!iso) return '';
        const d = new Date(iso);
        if (isNaN(d)) return iso;
        return d.toLocaleDateString('ru-RU', {
            day: 'numeric', month: 'long', year: 'numeric'
        });
    }

    function escapeHTML(s) {
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
    function escapeAttr(s) {
        return String(s).replace(/"/g, '&quot;');
    }

    // Универсальный путь к картинке для главной страницы
    // "../img/x"      → "img/x"          (файл в корне сайта)
    // "bazanovo/x"    → "Komorium/bazanovo/x"  (файл внутри Komorium)
    function imageURL(img) {
        if (!img) return '';
        if (img.startsWith('../')) return img.slice(3);
        return 'Komorium/' + img;
    }

    const all = [...articlesData].sort(
        (a, b) => new Date(b.date) - new Date(a.date)
    );

    // 1. Последние материалы
    const latestGrid = document.getElementById('latest-grid');
    if (latestGrid) {
        latestGrid.innerHTML = all.slice(0, 3).map(cardHTML).join('');
    }

    // 2. Статья дня
    const dailyBox = document.getElementById('daily-article');
    if (dailyBox && all.length > 0) {
        const today = new Date();
        const startDate = new Date(2020, 0, 1);
        const dayNumber = Math.floor(
            (Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())
                - Date.UTC(startDate.getFullYear(), startDate.getMonth(), startDate.getDate()))
            / (1000 * 60 * 60 * 24)
        );
        const daily = all[dayNumber % all.length];

        if (daily) {
            const image = daily.image
                ? `<img src="${escapeAttr(imageURL(daily.image))}" alt="${escapeAttr(daily.title)}" loading="lazy">`
                : `<span class="placeholder">📄</span>`;

            dailyBox.innerHTML = `
                <div class="daily-label">📅 Статья дня</div>
                <div class="daily-card">
                    <div class="daily-image">${image}</div>
                    <div class="daily-body">
                        <h3 class="daily-title">${escapeHTML(daily.title)}</h3>
                        <div class="daily-meta">
                            <span class="badge">${escapeHTML(daily.categoryLabel || daily.category)}</span>
                            <span>${escapeHTML(formatDate(daily.date))}</span>
                        </div>
                        <p class="daily-desc">${escapeHTML(daily.description || '')}</p>
                        <a href="Komorium/${escapeAttr(daily.url)}" class="daily-link">Читать →</a>
                    </div>
                </div>
            `;
        }
    }

    // 3. Категории
    const catGrid = document.getElementById('categories-grid');
    if (catGrid) {
        const map = new Map();
        all.forEach(a => {
            const key = a.category;
            if (!map.has(key)) {
                map.set(key, {
                    code: key,
                    label: a.categoryLabel || a.category,
                    count: 0
                });
            }
            map.get(key).count++;
        });

        const categories = [...map.values()].sort((a, b) => b.count - a.count);

        catGrid.innerHTML = categories.map(c => `
            <a class="category-tile" href="Komorium/articles.html?category=${encodeURIComponent(c.code)}">
                <span class="category-name">${escapeHTML(c.label)}</span>
                <span class="category-count">${c.count}</span>
            </a>
        `).join('');
    }

    // 4. Поиск
    const searchForm = document.getElementById('home-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = searchForm.querySelector('input[name="q"]');
            const q = (input.value || '').trim();
            if (!q) return;
            window.location.href = 'Komorium/articles.html?q=' + encodeURIComponent(q);
        });
    }

    // Карточка статьи
    function cardHTML(a) {
        const image = a.image
            ? `<img src="${escapeAttr(imageURL(a.image))}" alt="${escapeAttr(a.title)}" loading="lazy">`
            : `<span class="placeholder">📄</span>`;
        return `
            <li class="article-card">
                <div class="article-image-wrapper">${image}</div>
                <div class="article-content">
                    <h2 class="article-title">${escapeHTML(a.title)}</h2>
                    <div class="article-meta">
                        <span class="badge">${escapeHTML(a.categoryLabel || a.category)}</span>
                        <span>${escapeHTML(a.date)}</span>
                    </div>
                    <p class="article-description">${escapeHTML(a.description || '')}</p>
                    <a href="Komorium/${escapeAttr(a.url)}" class="article-link">Читать статью →</a>
                </div>
            </li>
        `;
    }
})();