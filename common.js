// common.js — общие скрипты для всего сайта Komorok
(function () {
    // Глобальный обработчик ошибок загрузки картинок.
    // Если картинка не загрузилась — скрываем её родителя (figure, div, p).
    document.addEventListener('error', function (event) {
        const target = event.target;
        if (!target || target.tagName !== 'IMG') return;

        // Не скрываем логотип и шапку
        if (target.classList.contains('no-hide') ||
            target.classList.contains('logo') ||
            target.classList.contains('hero-img')) {
            return;
        }

        // Скрываем родителя, если он есть
        if (target.parentElement) {
            target.parentElement.style.display = 'none';
        }
    }, true);  // ← true = ловим на этапе захвата (error не всплывает)
})();