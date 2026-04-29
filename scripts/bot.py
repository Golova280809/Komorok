#!/usr/bin/env python3
"""Telegram-бот Komorok с главным меню (inline-кнопки)."""
import os, sys, requests, re, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# --- настройки ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN не найден в переменных окружения")
    sys.exit(1)

SITE_URL = "https://komorok.ru"
TIMEOUT = 5  # секунды для проверки сайта
POLLING_TIMEOUT = 45  # секунд (чтобы не зависать)

# --- инструменты ---
def check_site(url: str) -> bool:
    """True, если сайт отвечает 200."""
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "KomorokBot/1.0"})
        return resp.status_code == 200
    except Exception:
        return False

# --- обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главное меню с кнопками."""
    keyboard = [
        [InlineKeyboardButton("🟢 Проверить сайт", callback_data="check")],
        [InlineKeyboardButton("🔑 Конкурс", callback_data="contest")],
        [InlineKeyboardButton("📝 Оставить отзыв", callback_data="feedback")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Привет! Я бот Komorok. Выберите действие:",
        reply_markup=reply_markup,
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатия на кнопки."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "check":
        ok = check_site(SITE_URL)
        await query.edit_message_text(
            f"{'✅' if ok else '❌'} Сайт Komorok {'работает' if ok else 'не работает'}!"
        )

    elif data == "contest":
        await query.edit_message_text(
            "🔑 Введите ваше имя, фамилию и ответ (количество ключей) через пробел.\n"
            "Пример: Иван Иванов 7"
        )

    elif data == "feedback":
        await query.edit_message_text(
            "📝 Напишите ваш отзыв о сайте (можно со смайликами)."
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает любое текстовое сообщение (не команду)."""
    text = update.message.text.strip()
    user = update.effective_user

    # Пытаемся распознать ответ конкурса: три слова и последнее — число
    parts = text.split()
    if len(parts) >= 3 and parts[-1].isdigit():
        name, surname, answer = parts[0], parts[1], parts[-1]
        with open("contest.txt", "a", encoding="utf-8") as f:
            f.write(f"{user.full_name} (@{user.username}): {name} {surname} - {answer} ключей\n")
        await update.message.reply_text("✅ Ваш ответ принят! Спасибо за участие в конкурсе.")
    else:
        # Всё остальное сохраняем как отзыв
        with open("feedbacks.txt", "a", encoding="utf-8") as f:
            f.write(f"{user.full_name} (@{user.username}): {text}\n")
        await update.message.reply_text("💬 Спасибо за отзыв! Он сохранён.")

# --- запуск ---
def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Бот Komorok активирован. Жду сообщений…")
    app.run_polling(timeout=POLLING_TIMEOUT)
    print("⏹️ Сеанс завершён.")

if __name__ == "__main__":
    main()