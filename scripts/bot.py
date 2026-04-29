#!/usr/bin/env python3
"""Telegram-бот Komorok с конкурсом (один ответ на пользователя, шифрование)."""
import os, sys, requests, json, base64
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
    print("❌ BOT_TOKEN не найден")
    sys.exit(1)

SITE_URL = "https://komorok.ru"
TIMEOUT = 5
POLLING_TIMEOUT = 45
CONTEST_FILE = "contest.json"          # зашифрованные ответы
FEEDBACK_FILE = "feedbacks.txt"       # отзывы (без шифрования)

# --- шифрование (base64) ---
def encrypt_data(name: str, surname: str, answer: str) -> str:
    """Склеивает данные через | и кодирует в base64."""
    raw = f"{name}|{surname}|{answer}"
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")

def decrypt_data(encoded: str):
    """Раскодирует base64 и возвращает (name, surname, answer)."""
    raw = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
    parts = raw.split("|")
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return None, None, None

# --- работа с JSON-файлом ---
def load_contest():
    if not os.path.isfile(CONTEST_FILE):
        return {}
    with open(CONTEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_contest(data):
    with open(CONTEST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- проверка сайта ---
def check_site(url: str) -> bool:
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "KomorokBot/1.0"})
        return resp.status_code == 200
    except Exception:
        return False

# --- обработчики ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            "Пример: Иван Иванов 7\n\n"
            "❗️ Каждый пользователь может дать только ОДИН ответ. "
            "При повторной отправке ваш ответ будет обновлён."
        )

    elif data == "feedback":
        await query.edit_message_text(
            "📝 Напишите ваш отзыв о сайте (можно со смайликами)."
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    user = update.effective_user
    user_id = str(user.id)

    # Проверяем, является ли сообщение ответом на конкурс (формат: два слова и число)
    parts = text.split()
    if len(parts) >= 3 and parts[-1].isdigit():
        name = parts[0]
        surname = parts[1]
        answer = parts[-1]

        # Загружаем существующие ответы
        contest_data = load_contest()
        encrypted = encrypt_data(name, surname, answer)

        if user_id in contest_data:
            # Пользователь уже давал ответ – обновляем
            contest_data[user_id] = encrypted
            save_contest(contest_data)
            await update.message.reply_text("✅ Ваш ответ обновлён! Спасибо за участие.")
        else:
            # Первый ответ
            contest_data[user_id] = encrypted
            save_contest(contest_data)
            await update.message.reply_text("✅ Ваш ответ принят! Спасибо за участие.")

    else:
        # Обычный отзыв
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user.full_name} (@{user.username}): {text}\n")
        await update.message.reply_text("💬 Спасибо за отзыв! Он сохранён.")

# --- запуск ---
def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Бот Komorok активирован (с шифрованием). Жду сообщений…")
    app.run_polling(timeout=POLLING_TIMEOUT)
    print("⏹️ Сеанс завершён.")

if __name__ == "__main__":
    main()