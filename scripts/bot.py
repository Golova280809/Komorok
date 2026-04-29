#!/usr/bin/env python3
"""Telegram-бот Komorok с пошаговым вводом ответа на конкурс."""
import os, sys, requests, json, base64, subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Состояния диалога
ASK_NAME, ASK_SURNAME, ASK_ANSWER = range(3)

# --- настройки ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN не найден")
    sys.exit(1)

SITE_URL = "https://komorok.ru"
TIMEOUT = 5
POLLING_TIMEOUT = 45
CONTEST_FILE = "contest.json"
FEEDBACK_FILE = "feedbacks.txt"

# --- git helper ---
def git_commit_and_push(files):
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"] + files,
            capture_output=True, text=True, timeout=10
        )
        if not result.stdout.strip():
            print("Нет изменений для коммита")
            return
        subprocess.run(["git", "config", "user.name", os.environ.get("GIT_USER_NAME", "KomorokBot")], check=True)
        subprocess.run(["git", "config", "user.email", os.environ.get("GIT_USER_EMAIL", "bot@komorok.ru")], check=True)
        subprocess.run(["git", "add"] + files, check=True)
        subprocess.run(["git", "commit", "-m", "Обновлены ответы конкурса и отзывы"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Изменения запушены в репозиторий")
    except Exception as e:
        print(f"❌ Ошибка при git push: {e}")

# --- шифрование ---
def encrypt_data(name, surname, answer):
    raw = f"{name}|{surname}|{answer}"
    return base64.b64encode(raw.encode("utf-8")).decode("utf-8")

def load_contest():
    if not os.path.isfile(CONTEST_FILE):
        return {}
    with open(CONTEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_contest(data):
    with open(CONTEST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- проверка сайта ---
def check_site(url):
    try:
        resp = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": "KomorokBot/1.0"})
        return resp.status_code == 200
    except:
        return False

# --- обработчики меню ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟢 Проверить сайт", callback_data="check")],
        [InlineKeyboardButton("🔑 Конкурс", callback_data="contest")],
        [InlineKeyboardButton("📝 Оставить отзыв", callback_data="feedback")],
    ]
    await update.message.reply_text(
        "👋 Привет! Я бот Komorok. Выберите действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            "🔑 Давайте запишем ваш ответ на конкурс.\n\n"
            "Шаг 1/3: Введите ваше имя (например, Иван)."
        )
        return ASK_NAME

    elif data == "feedback":
        await query.edit_message_text("📝 Напишите ваш отзыв о сайте (можно со смайликами).")

# --- шаги диалога (конкурс) ---
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        "Шаг 2/3: Введите вашу фамилию.\n"
        "Если не хотите указывать, отправьте прочерк `-`."
    )
    return ASK_SURNAME

async def ask_surname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surname = update.message.text.strip()
    if surname == "-":
        surname = "не указана"
    context.user_data["surname"] = surname
    await update.message.reply_text(
        "Шаг 3/3: Введите количество найденных ключей на сайте Komorok (только число)."
    )
    return ASK_ANSWER

async def ask_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Пожалуйста, введите только число (например, 7).")
        return ASK_ANSWER

    user = update.effective_user
    user_id = str(user.id)
    name = context.user_data.get("name")
    surname = context.user_data.get("surname")
    answer = text

    data = load_contest()
    data[user_id] = encrypt_data(name, surname, answer)
    save_contest(data)
    git_commit_and_push([CONTEST_FILE])

    await update.message.reply_text("✅ Ваш ответ принят! Спасибо за участие в конкурсе.")
    return ConversationHandler.END

# --- отзывы (всё остальное) ---
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user.full_name} (@{user.username}): {text}\n")
    git_commit_and_push([FEEDBACK_FILE])
    await update.message.reply_text("💬 Спасибо за отзыв! Он сохранён.")

# --- запуск ---
def main():
    app = Application.builder().token(TOKEN).build()

    # ConversationHandler для конкурса
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^contest$")],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
            ASK_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_answer)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(check|feedback)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    print("🤖 Бот Komorok с диалогом активирован. Жду сообщений…")
    app.run_polling(timeout=POLLING_TIMEOUT)
    print("⏹️ Сеанс завершён.")

if __name__ == "__main__":
    main()