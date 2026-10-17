// articles.js — логика страницы "Все статьи" Komorium
(function () {
    const grid = document.getElementById('articles-grid');
    const filtersBox = document.getElementById('filters');
    const emptyMsg = document.getElementById('empty-message');
    const searchInput = document.getElementById('search-input');
    const showMoreBtn = document.getElementById('show-more-btn');

    if (!grid) return;

    const PAGE_SIZE = 6;
    const PAGINATION_SIZE = 50;
    const CONTEXT_CHARS = 60;   // сколько символов вокруг совпадения показывать

    let currentCategory = 'all';
    let currentSearch = '';
    let visibleCount = PAGE_SIZE;
    let currentPage = 1;

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

    // === Подсветка + вырезание контекста вокруг совпадения ===
    function highlight(text, query) {
        const raw = String(text || '');
        const safe = escapeHTML(raw);
        const q = (query || '').trim();

        if (!q) return safe;

        // Ищем первое совпадение в исходном тексте
        const lowerText = raw.toLowerCase();
        const lowerQ = q.toLowerCase();
        const matchIdx = lowerText.indexOf(lowerQ);

        // Если не нашли — просто возвращаем как есть
        if (matchIdx === -1) return safe;

        // Вырезаем фрагмент вокруг совпадения
        const matchLen = q.length;
        const start = Math.max(0, matchIdx - CONTEXT_CHARS);
        const end = Math.min(raw.length, matchIdx + matchLen + CONTEXT_CHARS);

        let snippet = raw.slice(start, end);

        // Добавляем многоточия по краям, если обрезали
        const prefix = start > 0 ? '… ' : '';
        const suffix = end < raw.length ? ' …' : '';

        // Экранируем и подсвечиваем
        const safeSnippet = escapeHTML(snippet);
        const re = new RegExp(escapeRegex(escapeHTML(q)), 'gi');
        const highlighted = safeSnippet.replace(re, match => `<mark>${match}</mark>`);

        return prefix + highlighted + suffix;
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

        const totalPages = Math.max(1, Math.ceil(filtered.length / PAGINATION_SIZE));
        const pageStart = (currentPage - 1) * PAGINATION_SIZE;
        const slice = filtered.slice(pageStart, pageStart + visibleCount);

        grid.innerHTML = '';
        slice.forEach(a => grid.appendChild(renderCard(a)));

        emptyMsg.style.display = filtered.length === 0 ? 'block' : 'none';

        const shownOnThisPage = slice.length;
        const totalOnThisPage = Math.min(
            PAGINATION_SIZE,
            Math.max(0, filtered.length - pageStart)
        );
        showMoreBtn.style.display =
            shownOnThisPage < totalOnThisPage ? 'block' : 'none';

        renderPagination(totalPages);
    }

    function renderPagination(totalPages) {
        let pagination = document.getElementById('pagination');

        if (!pagination) {
            pagination = document.createElement('div');
            pagination.id = 'pagination';
            pagination.className = 'pagination';
            showMoreBtn.parentNode.insertBefore(pagination, showMoreBtn.nextSibling);
        }

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            pagination.style.display = 'none';
            return;
        }

        pagination.style.display = 'flex';
        pagination.innerHTML = '';

        if (currentPage > 1) {
            const prev = document.createElement('button');
            prev.className = 'page-btn';
            prev.textContent = '←';
            prev.addEventListener('click', () => {
                currentPage--;
                visibleCount = PAGE_SIZE;
                render();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            pagination.appendChild(prev);
        }

        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement('button');
            btn.className = 'page-btn';
            if (i === currentPage) btn.classList.add('active');
            btn.textContent = i;
            btn.addEventListener('click', () => {
                currentPage = i;
                visibleCount = PAGE_SIZE;
                render();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            pagination.appendChild(btn);
        }

        if (currentPage < totalPages) {
            const next = document.createElement('button');
            next.className = 'page-btn';
            next.textContent = '→';
            next.addEventListener('click', () => {
                currentPage++;
                visibleCount = PAGE_SIZE;
                render();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            pagination.appendChild(next);
        }
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
                currentPage = 1;
                render();
            });

            filtersBox.appendChild(btn);
        });
    }

    searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value;
        visibleCount = PAGE_SIZE;
        currentPage = 1;
        render();
    });

    showMoreBtn.addEventListener('click', () => {
        visibleCount += PAGE_SIZE;
        render();
    });

    renderFilters();

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