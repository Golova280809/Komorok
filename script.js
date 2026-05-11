(function() {
    var savedFontSize = localStorage.getItem('fontSize');
    if (savedFontSize) {
        var multiplier = parseInt(savedFontSize) / 100;
        document.documentElement.style.setProperty('--font-size-multiplier', multiplier.toString());
    }
})();

(function () {
    // === КНОПКА "НАВЕРХ" ===
    const backToTop = document.getElementById("backToTop");
    if (backToTop) {
        window.addEventListener("scroll", () => {
            backToTop.classList.toggle("show", window.scrollY > 300);
        });
        backToTop.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // === СВОРАЧИВАНИЕ ПОДРАЗДЕЛОВ ===
    const toggleButtons = document.querySelectorAll(".toggle-subcat");
    if (toggleButtons.length) {
        function toggleSubcategory(button) {
            const targetId = button.getAttribute("data-target");
            const subcat = document.getElementById(targetId);
            if (subcat) subcat.classList.toggle("collapsed");
        }
        toggleButtons.forEach((btn) => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                toggleSubcategory(this);
            });
        });
    }

    // === ПОИСК ===
    const searchInput = document.getElementById("searchInput");
    const clearBtn = document.getElementById("clearSearch");
    const noResultsMsg = document.getElementById("noResultsMessage");
    if (searchInput && clearBtn && noResultsMsg) {
        const subcategories = Array.from(document.querySelectorAll(".subcategory"));
        const standaloneSection = document.querySelector(".standalone-card");

        function filterCards() {
            const query = searchInput.value.trim().toLowerCase();
            clearBtn.classList.toggle("visible", query.length > 0);

            // каждый раз собираем актуальный список карточек (включая динамические)
            const allCards = Array.from(document.querySelectorAll(".article-card"));

            allCards.forEach((card) => {
                const title = (card.getAttribute("data-title") || "").toLowerCase();
                const desc = (card.getAttribute("data-desc") || "").toLowerCase();
                const matches = query === "" || title.includes(query) || desc.includes(query);
                card.classList.toggle("hidden-by-search", !matches);
            });

            subcategories.forEach((subcat) => {
                const visibleCards = subcat.querySelectorAll(".article-card:not(.hidden-by-search)").length;
                subcat.classList.toggle("hidden-subcat", visibleCards === 0);
                if (query !== "" && visibleCards > 0) {
                    subcat.classList.remove("collapsed");
                }
            });

            if (standaloneSection) {
                const visibleStandalone = standaloneSection.querySelectorAll(".article-card:not(.hidden-by-search)").length;
                standaloneSection.style.display = visibleStandalone === 0 ? "none" : "";
            }

            const totalVisible = allCards.filter((c) => !c.classList.contains("hidden-by-search")).length;
            noResultsMsg.classList.toggle("show", query !== "" && totalVisible === 0);

            if (query === "") {
                subcategories.forEach((subcat) => {
                    subcat.classList.add("collapsed");
                    subcat.classList.remove("hidden-subcat");
                });
                if (standaloneSection) standaloneSection.style.display = "";
            }
        }

        searchInput.addEventListener("input", filterCards);
        clearBtn.addEventListener("click", () => {
            searchInput.value = "";
            filterCards();
            searchInput.focus();
        });
        filterCards();
    }

    // === ТЁМНАЯ ТЕМА ===
    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
        const body = document.body;
        const iconSpan = themeToggle.querySelector(".icon");
        const textSpan = themeToggle.querySelector("span:last-child");

        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
            body.classList.add("dark-theme");
            if (iconSpan) iconSpan.textContent = "☀️";
            if (textSpan) textSpan.textContent = "Светлая тема";
        }

        themeToggle.addEventListener("click", () => {
            body.classList.toggle("dark-theme");
            const isDark = body.classList.contains("dark-theme");
            if (iconSpan) iconSpan.textContent = isDark ? "☀️" : "🌙";
            if (textSpan) textSpan.textContent = isDark ? "Светлая тема" : "Тёмная тема";
            localStorage.setItem("theme", isDark ? "dark" : "light");
        });
    }
})();

// ============================================================
//  УНИВЕРСАЛЬНЫЙ ЗАГРУЗЧИК КАРТОЧЕК ДЛЯ СТРАНИЦ-ХАБОВ
// ============================================================
/**
 * @param {string}  category    – категория статей (напр. 'china-history').
 * @param {string}  containerId – id контейнера для карточек.
 * @param {number}  batchSize   – сколько карточек за раз (по умолч. 5).
 * @param {string}  articlesPath – путь к articles.json (напр. '../articles.json').
 * @param {string}  imgFallback – путь к заглушке, если нет изображения (по умолч. '../../img/no-img.webp').
 */
function renderHab(category, containerId, batchSize = 5, articlesPath = 'articles.json', imgFallback = '../../img/no-img.webp') {
    const container = document.getElementById(containerId);
    if (!container) return;

    fetch(articlesPath)
        .then(res => res.json())
        .then(articles => {
            const items = articles.filter(a => a.category === category);
            if (items.length === 0) {
                container.innerHTML = '<p>Статей пока нет.</p>';
                return;
            }

            let offset = 0;

            function renderBatch() {
                const batch = items.slice(offset, offset + batchSize);
                batch.forEach(item => {
                    let rawImg = item.image && item.image.trim() !== '' ? item.image : imgFallback;
                    // Корректируем пути: ../img/ → ../../img/ для страниц второго уровня
                    if (rawImg.startsWith('../img/')) {
                        rawImg = '../../img/' + rawImg.slice(7);
                    }

                    const a = document.createElement('a');
                    a.href = '/Komorium/' + item.url;
                    a.className = 'article-card';
                    a.setAttribute('data-title', item.title);
                    a.setAttribute('data-desc', '');
                    a.innerHTML = `
                        <img src="${rawImg}" alt="" class="avatar">
                        <div class="card-content">
                            <span class="card-title">${item.title}</span>
                            <span class="card-desc"></span>
                        </div>`;
                    container.appendChild(a);
                });
                offset += batch.length;

                // Кнопка "Показать ещё"
                const oldBtn = container.querySelector('.show-more-btn');
                if (oldBtn) oldBtn.remove();
                if (offset < items.length) {
                    const btn = document.createElement('button');
                    btn.textContent = 'Показать ещё';
                    btn.className = 'show-more-btn';
                    btn.addEventListener('click', renderBatch);
                    container.appendChild(btn);
                }
            }

            renderBatch();
        })
        .catch(err => console.error('Ошибка загрузки articles.json', err));
}


// Автоматическая кнопка "Поделиться" для страниц статей
(function() {
    // Проверяем, что мы на странице статьи (есть навигация .top-menu или характерный заголовок)
    var isArticle = document.querySelector('.top-menu') ||
                    document.querySelector('h1') && document.querySelector('.content-section');

    if (!isArticle) return;

    // Проверяем, не добавлена ли уже кнопка
    if (document.getElementById('shareBtnContainer')) return;

    // Создаём контейнер
    var container = document.createElement('div');
    container.id = 'shareBtnContainer';
    container.style.cssText = 'text-align:center; margin:2rem 0;';

    // Кнопка
    var btn = document.createElement('button');
    btn.id = 'shareBtn';
    btn.textContent = '📤 Поделиться';
    btn.style.cssText = `
        display: inline-block;
        background: #4a6fa5;
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        cursor: pointer;
        font-weight: bold;
        transition: background 0.3s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    `;
    btn.onmouseover = function() { this.style.background = '#5f8bc9'; };
    btn.onmouseout = function() { this.style.background = '#4a6fa5'; };

    btn.addEventListener('click', function() {
        var url = window.location.href;
        var title = document.title;

        if (navigator.share) {
            navigator.share({
                title: title,
                url: url
            }).catch(function(err) {
                console.log('Ошибка шаринга: ', err);
            });
        } else {
            // Копирование ссылки для десктопа
            navigator.clipboard.writeText(url).then(function() {
                // Показываем всплывающую подсказку
                var tooltip = document.createElement('span');
                tooltip.textContent = '✅ Ссылка скопирована!';
                tooltip.style.cssText = `
                    display: inline-block;
                    margin-left: 10px;
                    background: #333;
                    color: #fff;
                    padding: 0.3rem 0.8rem;
                    border-radius: 4px;
                    font-size: 0.9rem;
                    animation: fadeOut 2s forwards;
                `;
                btn.parentNode.appendChild(tooltip);
                setTimeout(function() {
                    tooltip.remove();
                }, 2000);
            }).catch(function() {
                alert('Не удалось скопировать ссылку');
            });
        }
    });

    container.appendChild(btn);

    // Вставляем в конец <main> или после последней секции
    var main = document.querySelector('main');
    if (main) {
        main.appendChild(container);
    } else {
        // Запасной вариант: после последней .content-section
        var sections = document.querySelectorAll('.content-section');
        if (sections.length > 0) {
            var last = sections[sections.length - 1];
            last.parentNode.insertBefore(container, last.nextSibling);
        }
    }
})();