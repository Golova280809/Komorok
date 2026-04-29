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

    // === ПОИСК (только если элементы есть) ===
    const searchInput = document.getElementById("searchInput");
    const clearBtn = document.getElementById("clearSearch");
    const noResultsMsg = document.getElementById("noResultsMessage");

    if (searchInput && clearBtn && noResultsMsg) {
        const allCards = Array.from(document.querySelectorAll(".article-card"));
        const subcategories = Array.from(document.querySelectorAll(".subcategory"));
        const standaloneSection = document.querySelector(".standalone-card");

        function filterCards() {
            const query = searchInput.value.trim().toLowerCase();
            clearBtn.classList.toggle("visible", query.length > 0);

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
                const visibleStandalone = standaloneSection.querySelectorAll(
                    ".article-card:not(.hidden-by-search)",
                ).length;
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

// === ДИНАМИЧЕСКАЯ ЗАГРУЗКА КАРТОЧЕК ===
(function() {
    const BATCH_SIZE = 5;
    const state = {};

    // Ручная карточка "Об авторе"
    const aboutContainer = document.getElementById('cards-about');
    if (aboutContainer) {
        aboutContainer.innerHTML = `
            <a href="../Alexander.html" class="article-card" data-title="Головачёв Александр" data-desc="Творчество">
                <img src="../img/about.png" alt="📰" class="avatar" />
                <div class="card-content">
                    <span class="card-title">Головачёв Александр</span>
                    <span class="card-desc">Творчество</span>
                </div>
            </a>`;
    }

    fetch('articles.json')
        .then(res => res.json())
        .then(articles => {
            const groups = {};
            articles.forEach(a => {
                if (!groups[a.category]) groups[a.category] = [];
                groups[a.category].push(a);
            });

            Object.entries(groups).forEach(([cat, items]) => {
                const container = document.getElementById(`cards-${cat}`);
                const btn = document.querySelector(`.show-more-btn[data-category="${cat}"]`);
                if (!container) return;
                state[cat] = 0;
                renderBatch(items, container, btn, cat);
            });
        })
        .catch(err => console.error('Ошибка загрузки articles.json', err));

    function renderBatch(items, container, btn, cat) {
        const start = state[cat];
        const batch = items.slice(start, start + BATCH_SIZE);
        batch.forEach(item => {
            const imgSrc = item.image && item.image.trim() !== '' ? item.image : '../img/no-img.png';
            const a = document.createElement('a');
            a.href = item.url;
            a.className = 'article-card';
            a.setAttribute('data-title', item.title);
            a.setAttribute('data-desc', '');
            a.innerHTML = `
                <img src="${imgSrc}" alt="" class="avatar">
                <div class="card-content">
                    <span class="card-title">${item.title}</span>
                    <span class="card-desc"></span>
                </div>`;
            container.appendChild(a);
        });
        state[cat] += batch.length;
        if (btn) {
            if (state[cat] < items.length) {
                btn.style.display = 'block';
                btn.onclick = () => renderBatch(items, container, btn, cat);
            } else {
                btn.style.display = 'none';
            }
        }
    }
})();

// === ПАГИНАЦИЯ ПОДРАЗДЕЛОВ (кнопка "Показать ещё подразделы") ===
(function() {
    const SECTIONS_SELECTOR = '.category-section'; // секции "География", "Технологии"
    const SUBCAT_SELECTOR = '.subcategory';
    const VISIBLE_SUBCATS = 5;

    document.querySelectorAll(SECTIONS_SELECTOR).forEach(section => {
        const subcats = section.querySelectorAll(SUBCAT_SELECTOR);
        if (subcats.length <= VISIBLE_SUBCATS) return;

        // Скрываем все подразделы, начиная с VISIBLE_SUBCATS
        for (let i = VISIBLE_SUBCATS; i < subcats.length; i++) {
            subcats[i].classList.add('hidden-subcat');
        }

        // Создаём кнопку
        const btn = document.createElement('button');
        btn.textContent = 'Показать ещё подразделы';
        btn.className = 'show-more-btn';
        // Вставляем кнопку после последнего подраздела (перед закрытием секции)
        const lastSubcat = subcats[subcats.length - 1];
        lastSubcat.insertAdjacentElement('afterend', btn);

        btn.addEventListener('click', () => {
            subcats.forEach(subcat => subcat.classList.remove('hidden-subcat'));
            btn.remove();
        });
    });
})();