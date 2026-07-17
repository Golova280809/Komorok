// === ПОИСК ПО КАРТОЧКАМ ===
(function () {
    const searchInput = document.getElementById("searchInput");
    const clearBtn = document.getElementById("clearSearch");
    const noResultsMsg = document.getElementById("noResultsMessage");

    if (!searchInput || !clearBtn || !noResultsMsg) return;

    function filterCards() {
        const query = searchInput.value.trim().toLowerCase();
        clearBtn.classList.toggle("visible", query.length > 0);

        const allCards = Array.from(document.querySelectorAll(".article-card"));
        let visibleCount = 0;

        allCards.forEach((card) => {
            const title = (card.getAttribute("data-title") || "").toLowerCase();
            const desc = (card.getAttribute("data-desc") || "").toLowerCase();
            const matches = query === "" || title.includes(query) || desc.includes(query);
            card.classList.toggle("hidden-by-search", !matches);
            if (matches) visibleCount++;
        });

        noResultsMsg.classList.toggle("show", query !== "" && visibleCount === 0);
    }

    searchInput.addEventListener("input", filterCards);

    clearBtn.addEventListener("click", () => {
        searchInput.value = "";
        filterCards();
        searchInput.focus();
    });

    filterCards(); // начальное состояние
})();

// === КНОПКА «ПОДЕЛИТЬСЯ» (для страниц статей) ===
(function () {
    // Определяем, что это страница статьи
    const isArticle =
        document.querySelector(".top-menu") ||
        (document.querySelector("h1") && document.querySelector(".content-section"));

    if (!isArticle) return;
    if (document.getElementById("shareBtnContainer")) return;

    const container = document.createElement("div");
    container.id = "shareBtnContainer";
    container.style.cssText = "text-align:center; margin:2rem 0;";

    const btn = document.createElement("button");
    btn.id = "shareBtn";
    btn.textContent = "📤 Поделиться";
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
    btn.onmouseover = () => (btn.style.background = "#5f8bc9");
    btn.onmouseout = () => (btn.style.background = "#4a6fa5");

    btn.addEventListener("click", () => {
        const url = window.location.href;
        const title = document.title;

        if (navigator.share) {
            navigator.share({ title, url }).catch((err) => {
                console.log("Ошибка шаринга:", err);
            });
        } else {
            navigator.clipboard
                .writeText(url)
                .then(() => {
                    const tooltip = document.createElement("span");
                    tooltip.textContent = "✅ Ссылка скопирована!";
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
                    setTimeout(() => tooltip.remove(), 2000);
                })
                .catch(() => {
                    alert("Не удалось скопировать ссылку");
                });
        }
    });

    container.appendChild(btn);

    const main = document.querySelector("main");
    if (main) {
        main.appendChild(container);
    } else {
        const sections = document.querySelectorAll(".content-section");
        if (sections.length > 0) {
            const last = sections[sections.length - 1];
            last.parentNode.insertBefore(container, last.nextSibling);
        }
    }
})();