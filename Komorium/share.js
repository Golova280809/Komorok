// share.js — кнопка "Поделиться" на страницах статей
(function () {
    const container = document.getElementById('share-container');
    if (!container) return;

    // Одна кнопка
    container.innerHTML = `
        <button class="share-btn share-main" type="button" title="Поделиться">
            🔗 Поделиться
        </button>
    `;

    const btn = container.querySelector('.share-main');

    btn.addEventListener('click', async () => {
        const shareData = {
            title: document.title,
            text: document.title,
            url: window.location.href
        };

        // 1) Если браузер умеет системное "Поделиться" (телефоны, Safari, Chrome Android)
        if (navigator.share) {
            try {
                await navigator.share(shareData);
                return; // всё ок, ничего больше не делаем
            } catch (err) {
                // Пользователь отменил — тоже ок, просто выходим
                if (err && err.name === 'AbortError') return;
                // Иначе — падаем в fallback ниже
            }
        }

        // 2) Fallback: копируем ссылку
        copyLink(btn);
    });

    function copyLink(button) {
        const original = button.textContent;

        const showDone = (text) => {
            button.textContent = text;
            button.classList.add('copied');
            setTimeout(() => {
                button.textContent = original;
                button.classList.remove('copied');
            }, 2000);
        };

        // Современный API
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(window.location.href)
                .then(() => showDone('✓ Скопировано'))
                .catch(() => legacyCopy(showDone));
        } else {
            legacyCopy(showDone);
        }
    }

    // Старый способ (для http / старых браузеров)
    function legacyCopy(showDone) {
        const textarea = document.createElement('textarea');
        textarea.value = window.location.href;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showDone('✓ Скопировано');
        } catch (e) {
            showDone('⚠ Не удалось');
        }
        document.body.removeChild(textarea);
    }
})();