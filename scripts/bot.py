"""
Telegram-бот Komorok
Отвечает на любое сообщение, проверяя доступность сайта.
Запускается через GitHub Actions каждые 5 минут.
"""
import os
import sys
import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Токен бота из секретов GitHub Actions
TOKEN = os.environ.get("BOT")
if not TOKEN:
    print("❌ Не указан BOT_TOKEN. Проверьте secrets в GitHub Actions.")
    sys.exit(1)

SITE_URL = "https://komorok.ru"
REQUEST_TIMEOUT = 5  # секунд
POLLING_TIMEOUT = 45  # секунд (бот будет слушать сообщения не дольше этого времени)

def check_site(url: str) -> bool:
    """Проверяет доступность сайта. Возвращает True, если сайт отвечает 200."""
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "KomorokBot/1.0"})
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False

async def site_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /site – принудительно выводит статус сайта."""
    is_ok = check_site(SITE_URL)
    if is_ok:
        await update.message.reply_text("✅ Сайт Komorok работает!")
    else:
        await update.message.reply_text("❌ Сайт Komorok не работает!")

async def any_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик любого текстового сообщения."""
    is_ok = check_site(SITE_URL)
    if is_ok:
        await update.message.reply_text("✅ Сайт Komorok работает!")
    else:
        await update.message.reply_text("❌ Сайт Komorok не работает!")

def main() -> None:
    """Собирает и запускает бота."""
    app = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", any_message))   # на /start тоже отвечаем проверкой
    app.add_handler(CommandHandler("site", site_command))   # отдельная команда /site
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, any_message))  # любой текст

    print("🤖 Бот Komorok активирован. Ожидаю сообщения (до 45 секунд)...")
    # Запуск полинга с ограниченным временем
    app.run_polling(timeout=POLLING_TIMEOUT)
    print("⏹️ Сеанс завершён.")

if __name__ == "__main__":
    main()