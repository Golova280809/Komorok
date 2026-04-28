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

// Пагинация карточек: показывать первые 5, остальные по кнопке
(function() {
    const GRID_SELECTOR = '.articles-grid';
    const CARD_SELECTOR = '.article-card';
    const VISIBLE_COUNT = 5;

    function setupPagination(grid) {
        const cards = grid.querySelectorAll(CARD_SELECTOR);
        if (cards.length <= VISIBLE_COUNT) return;

        // Скрываем лишние карточки
        for (let i = VISIBLE_COUNT; i < cards.length; i++) {
            cards[i].classList.add('card-hidden');
        }

        // Создаём кнопку
        const btn = document.createElement('button');
        btn.textContent = 'Показать ещё';
        btn.className = 'show-more-btn';
        btn.style.cssText = 'display:block; margin:1rem auto; padding:0.6rem 2rem; background:var(--accent); color:white; border:none; border-radius:25px; cursor:pointer; font-weight:600; transition: all 0.2s;';
        btn.addEventListener('mouseenter', () => btn.style.transform = 'scale(1.03)');
        btn.addEventListener('mouseleave', () => btn.style.transform = 'none');

        btn.addEventListener('click', () => {
            // Показываем все скрытые карточки
            const hidden = grid.querySelectorAll(CARD_SELECTOR + '.card-hidden');
            hidden.forEach(card => card.classList.remove('card-hidden'));
            // Удаляем кнопку
            btn.remove();
        });

        grid.appendChild(btn);
    }

    // Инициализация на всех сетках
    document.querySelectorAll(GRID_SELECTOR).forEach(grid => setupPagination(grid));
})();
