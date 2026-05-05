#!/bin/bash
case "$1" in
  "/start")
    echo "👋 Привет! Я локальный помощник Komorok."
    ;;
  "/site")
    echo "🌐 https://komorok.ru"
    ;;
  "/help")
    echo "Доступные команды: /start, /site, /help, /komorok"
    ;;
  "/komorok")
    echo ""
    echo "┌─────────────────────────────────────────────┐"
    echo "│           📊  KOMOROK  STATUS                │"
    echo "├─────────────────────────────────────────────┤"

    # 1. Статус сайта
    status_code=$(curl -s -o /dev/null -w "%{http_code}" https://komorok.ru)
    if [ "$status_code" = "200" ]; then
        echo "│  🌐 Сайт:          🟢 онлайн (200)          │"
    else
        echo "│  🌐 Сайт:          🔴 офлайн ($status_code)     │"
    fi

    # 2. Возраст проекта
    if git -C /storage/emulated/0/Komorok rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        first_date=$(git -C /storage/emulated/0/Komorok log --reverse --format=%cd --date=short | head -1)
        if [ -n "$first_date" ]; then
            days=$(( ($(date +%s) - $(date -d "$first_date" +%s)) / 86400 ))
            echo "│  📅 Возраст сайта: $days дней              │"
        fi
    fi

    # 3. Количество статей
    articles=$(curl -s https://komorok.ru/Komorium/articles.json | grep -c '"title"')
    echo "│  📚 Статей:        $articles                 │"

    # 4. Проверка битых ссылок (быстрый прогон)
    echo "│  🔍 Проверка ссылок...                       │"
    broken=$(curl -s https://komorok.ru/sitemap.xml | grep -oP '(?<=<loc>)[^<]+' | \
        xargs linkinator --verbosity error --skip "^(?!https?://komorok.ru)" 2>&1 | \
        grep -c "ERROR\|Broken")
    if [ "$broken" -eq 0 ]; then
        echo "│  🔗 Битые ссылки:  ✅ не найдены            │"
    else
        echo "│  🔗 Битые ссылки:  ⚠️  $broken               │"
    fi

    # 5. Последний коммит
    if git -C /storage/emulated/0/Komorok rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        last_commit=$(git -C /storage/emulated/0/Komorok log -1 --format=%cr)
        echo "│  🕒 Последний коммит: $last_commit        │"
    fi

    echo "└─────────────────────────────────────────────┘"
    echo ""
    ;;
  *)
    echo "Неизвестная команда. Попробуй /help"
    ;;
esac
