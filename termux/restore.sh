#!/bin/bash
echo "Начинаю восстановление Termux-окружения..."

# Копируем .bashrc
cp /storage/emulated/0/Komorok/termux/bashrc ~/.bashrc
echo "✅ .bashrc восстановлен"

# Восстанавливаем Git-настройки
while IFS= read -r line; do
  git config --global --add safe.directory "$line" 2>/dev/null || \
  git config --global user.name "$line" || \
  git config --global user.email "$line"
done < /storage/emulated/0/Komorok/termux/gitconfig
echo "✅ Git-настройки восстановлены"

# Применяем алиасы
source ~/.bashrc
echo "✅ Алиасы применены"

echo ""
echo "🎉 Восстановление завершено! Ваши команды (komorok, komorok1, d, help) готовы к работе."
