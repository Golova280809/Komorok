// articles.js — логика страницы "Все статьи" Komorium
(function () {
    const grid = document.getElementById('articles-grid');
    const filtersBox = document.getElementById('filters');
    const emptyMsg = document.getElementById('empty-message');
    const searchInput = document.getElementById('search-input');
    const showMoreBtn = document.getElementById('show-more-btn');

    if (!grid) return;

    const PAGE_SIZE = 6;

    let currentCategory = 'all';
    let currentSearch = '';
    let visibleCount = PAGE_SIZE;

    const sorted = [...articlesData].sort(
        (a, b) => new Date(b.date) - new Date(a.date)
    );

    // === Чтение параметров URL (?q=... и ?category=...) ===
    const params = new URLSearchParams(window.location.search);
    const urlQ = params.get('q');
    const urlCat = params.get('category');

    if (urlQ) {
        currentSearch = urlQ;
        if (searchInput) searchInput.value = urlQ;
    }

    const categoriesMap = new Map();
    categoriesMap.set('all', 'Все');
    sorted.forEach(a => {
        if (!categoriesMap.has(a.category)) {
            categoriesMap.set(a.category, a.categoryLabel || a.category);
        }
    });

    function getFiltered() {
        return sorted.filter(a => {
            const okCat = currentCategory === 'all' || a.category === currentCategory;
            const q = currentSearch.trim().toLowerCase();
            const okSearch = !q
                || a.title.toLowerCase().includes(q)
                || (a.description || '').toLowerCase().includes(q);
            return okCat && okSearch;
        });
    }

    function escapeHTML(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function highlight(text, query) {
        const safe = escapeHTML(text);
        const q = (query || '').trim();
        if (!q) return safe;
        const re = new RegExp(escapeRegex(escapeHTML(q)), 'gi');
        return safe.replace(re, match => `<mark>${match}</mark>`);
    }

    function renderCard(article) {
        const li = document.createElement('li');
        li.className = 'article-card';

        const imageHTML = article.image
            ? `<img src="${article.image}" alt="${escapeHTML(article.title)}" loading="lazy">`
            : `<span class="placeholder">📄</span>`;

        const titleHTML = highlight(article.title, currentSearch);
        const descHTML = highlight(article.description || '', currentSearch);

        li.innerHTML = `
            <div class="article-image-wrapper">${imageHTML}</div>
            <div class="article-content">
                <h2 class="article-title">${titleHTML}</h2>
                <div class="article-meta">
                    <span class="badge">${escapeHTML(article.categoryLabel || article.category)}</span>
                    <span>${escapeHTML(article.date)}</span>
                </div>
                <p class="article-description">${descHTML}</p>
                <a href="${article.url}" class="article-link">Читать статью →</a>
            </div>
        `;
        return li;
    }

    function render() {
        const filtered = getFiltered();
        const slice = filtered.slice(0, visibleCount);

        grid.innerHTML = '';
        slice.forEach(a => grid.appendChild(renderCard(a)));

        emptyMsg.style.display = filtered.length === 0 ? 'block' : 'none';
        showMoreBtn.style.display = filtered.length > visibleCount ? 'block' : 'none';
    }

    function renderFilters() {
        categoriesMap.forEach((label, key) => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn';
            btn.textContent = label;
            btn.dataset.category = key;
            if (key === currentCategory) btn.classList.add('active');

            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn')
                    .forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentCategory = key;
                visibleCount = PAGE_SIZE;
                render();
            });

            filtersBox.appendChild(btn);
        });
    }

    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        visibleCount = PAGE_SIZE;
        render();
    });

    showMoreBtn.addEventListener('click', () => {
        visibleCount += PAGE_SIZE;
        render();
    });

    renderFilters();

    // Если в URL есть ?category= — активируем соответствующую кнопку
    if (urlCat) {
        const btn = document.querySelector(`.filter-btn[data-category="${urlCat}"]`);
        if (btn) {
            document.querySelectorAll('.filter-btn')
                .forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = urlCat;
        }
    }

    render();
})();