// recommend.js — автоматический блок «Рекомендуем почитать»
(function () {
    if (typeof articlesData === 'undefined') return;

    const container = document.getElementById('recommend-container');
    if (!container) return;

    const COUNT = 4; // сколько рекомендаций показывать

    // === Определяем URL текущей статьи относительно Komorium/ ===
    // Например: /Komorium/bazanovo/shkola/ → "bazanovo/shkola/"
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

    // === Ищем текущую статью ===
    const current = articlesData.find(a => a.url === currentUrl) || null;
    const currentCategory = current ? current.category : null;

    // === Собираем пул кандидатов ===
    // 1) той же категории, кроме текущей
    let sameCategory = articlesData.filter(a =>
        a.url !== currentUrl && currentCategory && a.category === currentCategory
    );

    // 2) остальные (не текущая и не из sameCategory)
    let others = articlesData.filter(a =>
        a.url !== currentUrl && a.category !== currentCategory
    );

    // Перемешиваем
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

    // Итог: сначала из той же категории, добираем из других
    const picked = [...sameCategory, ...others].slice(0, COUNT);

    if (picked.length === 0) {
        container.style.display = 'none';
        return;
    }

    // === Заголовок блока ===
    const headingText = currentCategory
        ? '📖 Читайте также'
        : '📖 Рекомендуем почитать';

    // === Карточки ===
    function cardHTML(a) {
        const image = a.image
            ? `<img src="${a.image}" alt="${escapeAttr(a.title)}" loading="lazy">`
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
                    <a href="${a.url}" class="article-link">Читать статью →</a>
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