#!/usr/bin/env python3
import os, sys, requests, json, base64, subprocess, hashlib
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

# Состояния диалога (конкурс)
ASK_NAME, ASK_SURNAME, ASK_ANSWER = range(3)
# Состояние для /admin (запрос пароля)
ADMIN_PASSWORD = 100

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

# --- ХЕШ пароля для /admin ---
# Это хеш от строки "коморок2026"
# Если хочешь поменять пароль, замени этот хеш на хеш нового пароля.
# Вычислить новый хеш можно командой:
#   echo -n "новый_пароль" | sha256sum
ADMIN_PASSWORD_HASH = hashlib.sha256("bccc3def74f0e9499ee0fbe50014f8503c1539c74fb69d623f976dd3fef6c5ff".encode()).hexdigest()

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

def decrypt_data(encoded):
    raw = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
    parts = raw.split("|")
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return None, None, None

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

# --- меню ---
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

# --- команда /admin (защищена хешем) ---
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Введите пароль администратора:")
    return ADMIN_PASSWORD

async def admin_check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered = update.message.text.strip()
    entered_hash = hashlib.sha256(entered.encode()).hexdigest()

    if entered_hash != ADMIN_PASSWORD_HASH:
        await update.message.reply_text("❌ Неверный пароль.")
        return ConversationHandler.END

    # Пароль верный – расшифровываем и показываем ответы
    data = load_contest()
    if not data:
        await update.message.reply_text("Пока нет ответов.")
        return ConversationHandler.END

    lines = ["📋 Ответы участников:\n"]
    for uid, enc in data.items():
        name, surname, answer = decrypt_data(enc)
        lines.append(f"• {name} {surname}: {answer} ключей")
    await update.message.reply_text("\n".join(lines))
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
    contest_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^contest$")],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_surname)],
            ASK_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_answer)],
        },
        fallbacks=[],
    )

    # ConversationHandler для /admin
    admin_conv = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            ADMIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_check_password)],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(contest_conv)
    app.add_handler(admin_conv)
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(check|feedback)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    print("🤖 Бот Komorok (с /admin) активирован. Жду сообщений…")
    app.run_polling(timeout=POLLING_TIMEOUT)
    print("⏹️ Сеанс завершён.")

if __name__ == "__main__":
    main()