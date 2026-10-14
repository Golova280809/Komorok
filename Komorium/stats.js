// stats.js — автоматический подсчёт статистики для главной Komorium
(function () {
    if (typeof articlesData === 'undefined') return;

    const grid = document.getElementById('stats-grid');
    if (!grid) return;

    const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };

    const total = articlesData.length;
    const categories = new Set(articlesData.map(a => a.category)).size;

    const lastDate = articlesData
        .map(a => a.date)
        .filter(Boolean)
        .sort()
        .pop();

    const formatDate = (iso) => {
        if (!iso) return '—';
        const d = new Date(iso);
        if (isNaN(d)) return iso;
        return d.toLocaleDateString('ru-RU', {
            day: 'numeric', month: 'long', year: 'numeric'
        });
    };

    set('stat-articles', total);
    set('stat-categories', categories);
    set('stat-date', formatDate(lastDate));
})();