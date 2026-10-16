// recommend.js — автоматический блок «Рекомендуем почитать»
(function () {
    if (typeof articlesData === 'undefined') return;

    const container = document.getElementById('recommend-container');
    if (!container) return;

    const COUNT = 4;

    // === Определяем базовый префикс для ссылок ===
    // Смотрим на путь страницы и вычисляем, сколько "../" нужно,
    // чтобы дойти до папки Komorium/
    function getKomoriumPrefix() {
        // Примеры:
        // /Komorium/vov/index.html           → "../"
        // /Komorium/bazanovo/index.html      → "../"
        // /Komorium/bazanovo/shkola/index.html → "../../"
        // /Komorium/krasnokamensk/places/index.html → "../../"
        // /Komorium/krasnokamensk/civil-war/ataman-semenov/index.html → "../../../"

        const path = window.location.pathname.replace(/\/[^/]*$/, ''); // убираем "index.html"
        const idx = path.indexOf('/Komorium/');
        if (idx === -1) {
            // Не внутри Komorium — возвращаем корень
            return '';
        }
        // Часть пути ПОСЛЕ /Komorium/
        const after = path.substring(idx + '/Komorium/'.length);
        if (!after) return ''; // мы уже в Komorium/

        // Считаем количество сегментов
        const segments = after.split('/').filter(Boolean);
        return '../'.repeat(segments.length);
    }

    const PREFIX = getKomoriumPrefix();

    // === Определяем текущую статью ===
    const path = window.location.pathname;
    let currentUrl = '';
    for (const a of articlesData) {
        if (!a.url) continue;
        const clean = a.url.replace(/^\/+/, '').replace(/\/+$/, '');
        if (clean && path.includes(clean)) {
            currentUrl = a.url;
            break;
        }
    }

    const current = articlesData.find(a => a.url === currentUrl) || null;
    const currentCategory = current ? current.category : null;

    // === Кандидаты ===
    let sameCategory = articlesData.filter(a =>
        a.url !== currentUrl && currentCategory && a.category === currentCategory
    );
    let others = articlesData.filter(a =>
        a.url !== currentUrl && a.category !== currentCategory
    );

    function shuffle(arr) {
        const copy = [...arr];
        for (let i = copy.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    }
    sameCategory = shuffle(sameCategory);
    others = shuffle(others);

    const picked = [...sameCategory, ...others].slice(0, COUNT);

    if (picked.length === 0) {
        container.style.display = 'none';
        return;
    }

    const headingText = currentCategory
        ? '📖 Читайте также'
        : '📖 Рекомендуем почитать';

    // === Карточка ===
    // КАРТИНКИ — путь считается отдельно:
    //   "../img/x" → <PREFIX> + "img/x"
    //   "bazanovo/x" → <PREFIX> + "bazanovo/x"
    // Потому что картинки в data тоже записаны от Komorium/
    function imageURL(img) {
        if (!img) return '';
        // Если путь уже начинается с ../ — считаем его от корня сайта
        // Но для recommend.js мы находимся внутри Komorium, поэтому
        // любой путь в articles-data.js "относительно Komorium".
        // Используем универсальный подход:
        if (img.startsWith('../')) {
            // "../img/x" — файл в корне сайта
            // Тогда PREFIX ведёт до Komorium, а нам нужно ещё на 1 выше → добавляем ../
            return PREFIX + '../' + img.slice(3);
        }
        return PREFIX + img;
    }

    function cardHTML(a) {
        const image = a.image
            ? `<img src="${escapeAttr(imageURL(a.image))}" alt="${escapeAttr(a.title)}" loading="lazy">`
            : `<span class="placeholder">📄</span>`;

        // ССЫЛКА на статью — PREFIX + url из данных
        const href = PREFIX + a.url;

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
                    <a href="${href}" class="article-link">Читать статью →</a>
                </div>
            </li>
        `;
    }

    container.innerHTML = `
        <h2>${headingText}</h2>
        <ul class="articles-grid hub-grid">
            ${picked.map(cardHTML).join('')}
        </ul>
    `;

    // === Утилиты ===
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
})();