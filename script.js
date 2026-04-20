const backToTopBtn = document.getElementById("backToTop");

        window.onscroll = function() {
            if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
                backToTopBtn.classList.add("show");
            } else {
                backToTopBtn.classList.remove("show");
            }
        };

        backToTopBtn.onclick = function() {
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        };
(function() {
            // Кнопка "Наверх"
            const backToTop = document.getElementById('backToTop');
            if (backToTop) {
                window.addEventListener('scroll', () => {
                    backToTop.classList.toggle('show', window.scrollY > 300);
                });
                backToTop.addEventListener('click', () => {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            }

            // Логика сворачивания/разворачивания подразделов
            const toggleButtons = document.querySelectorAll('.toggle-subcat');
            function toggleSubcategory(button) {
                const targetId = button.getAttribute('data-target');
                const subcat = document.getElementById(targetId);
                if (!subcat) return;
                subcat.classList.toggle('collapsed');
            }
            toggleButtons.forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    toggleSubcategory(this);
                });
            });

            // === ПОИСК ===
            const searchInput = document.getElementById('searchInput');
            const clearBtn = document.getElementById('clearSearch');
            const noResultsMsg = document.getElementById('noResultsMessage');
            
            // Все карточки статей
            const allCards = Array.from(document.querySelectorAll('.article-card'));
            // Все подразделы (и standalone секция — её тоже надо проверять)
            const subcategories = Array.from(document.querySelectorAll('.subcategory'));
            const standaloneSection = document.querySelector('.standalone-card');
            
            // Функция фильтрации
            function filterCards() {
                const query = searchInput.value.trim().toLowerCase();
                let visibleCount = 0;
                
                // Показываем/скрываем кнопку очистки
                clearBtn.classList.toggle('visible', query.length > 0);
                
                // Перебираем все карточки
                allCards.forEach(card => {
                    const title = (card.getAttribute('data-title') || '').toLowerCase();
                    const desc = (card.getAttribute('data-desc') || '').toLowerCase();
                    const matches = query === '' || title.includes(query) || desc.includes(query);
                    
                    if (matches) {
                        card.classList.remove('hidden-by-search');
                        visibleCount++;
                    } else {
                        card.classList.add('hidden-by-search');
                    }
                });
                
                // Обработка подразделов: скрываем те, в которых нет видимых карточек
                subcategories.forEach(subcat => {
                    const visibleCardsInSub = subcat.querySelectorAll('.article-card:not(.hidden-by-search)').length;
                    if (visibleCardsInSub === 0) {
                        subcat.classList.add('hidden-subcat');
                    } else {
                        subcat.classList.remove('hidden-subcat');
                        // Если подраздел был скрыт из-за поиска, но теперь есть результаты — можно автоматически развернуть?
                        // По желанию: разворачиваем, чтобы пользователь увидел результат
                        if (query !== '') {
                            subcat.classList.remove('collapsed');
                        }
                    }
                });
                
                // Обработка standalone секции: если карточка скрыта, можно скрыть весь блок или оставить заголовок?
                // Скрываем весь блок, если карточка не видна
                if (standaloneSection) {
                    const visibleStandaloneCards = standaloneSection.querySelectorAll('.article-card:not(.hidden-by-search)').length;
                    if (visibleStandaloneCards === 0) {
                        standaloneSection.style.display = 'none';
                    } else {
                        standaloneSection.style.display = '';
                    }
                }
                
                // Проверяем, есть ли вообще видимые карточки на странице (включая подразделы и standalone)
                const totalVisible = allCards.filter(c => !c.classList.contains('hidden-by-search')).length;
                
                // Показываем/скрываем сообщение "ничего не найдено"
                if (query !== '' && totalVisible === 0) {
                    noResultsMsg.classList.add('show');
                } else {
                    noResultsMsg.classList.remove('show');
                }
                
                // Если запрос пустой, возвращаем подразделы к исходному состоянию (свернуты)
                if (query === '') {
                    subcategories.forEach(subcat => {
                        // возвращаем collapsed как было изначально (в HTML они имеют класс collapsed)
                        // но могли быть развёрнуты при поиске. Восстановим collapsed.
                        subcat.classList.add('collapsed');
                        subcat.classList.remove('hidden-subcat');
                    });
                    if (standaloneSection) standaloneSection.style.display = '';
                } else {
                    // При поиске также можно развернуть все подразделы с результатами (уже сделано выше)
                }
            }
            
            // Обработчики событий
            searchInput.addEventListener('input', filterCards);
            clearBtn.addEventListener('click', function() {
                searchInput.value = '';
                filterCards();
                searchInput.focus();
            });
            
            // Инициализация: при загрузке скрываем подразделы? Уже collapsed в HTML
            // Дополнительно убедимся, что сообщение не показывается
            filterCards(); // чтобы синхронизировать clear button и т.д.
            
            // Для якорных ссылок ничего не меняем
        })();
        
