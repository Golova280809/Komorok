#!/usr/bin/env python3
"""
Telegram-бот Komorok для GitHub Actions.
Функции: /start, проверка сайта, отзывы, /admin.
"""

import os
import sys
import requests
import json
import hashlib
import subprocess

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❌ BOT_TOKEN не найден")
    sys.exit(1)

SITE_URL = "https://komorok.ru"
TIMEOUT = 5
UPDATE_FILE = "last_update_id.txt"
FEEDBACK_FILE = "feedbacks.txt"
ADMIN_DOUBLE_HASH = os.environ.get("ADMIN_DOUBLE_HASH", "")


def git_commit_and_push(files):
    """Сохраняет изменения в GitHub."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"] + files,
            capture_output=True, text=True, timeout=10
        )
        if not result.stdout.strip():
            return
        subprocess.run(["git", "config", "user.name", os.environ.get("GIT_USER_NAME", "KomorokBot")], check=True)
        subprocess.run(["git", "config", "user.email", os.environ.get("GIT_USER_EMAIL", "bot@komorok.ru")], check=True)
        subprocess.run(["git", "add"] + files, check=True)
        subprocess.run(["git", "commit", "-m", "Обновлены данные бота"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Изменения запушены")
    except Exception as e:
        print(f"❌ Git error: {e}")


def get_updates(offset):
    """Получает новые сообщения от Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
    try:
        resp = requests.get(url, timeout=45)
        data = resp.json()
        return data.get("result", [])
    except:
        return []


def send_message(chat_id, text, reply_markup=None):
    """Отправляет сообщение в Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass


def check_site():
    """Проверяет, работает ли сайт."""
    try:
        resp = requests.get(SITE_URL, timeout=TIMEOUT, headers={"User-Agent": "KomorokBot/1.0"})
        return resp.status_code == 200
    except:
        return False


def handle_start(chat_id):
    """Обрабатывает команду /start."""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🟢 Проверить сайт", "callback_data": "check"}],
            [{"text": "📝 Оставить отзыв", "callback_data": "feedback"}],
        ]
    }
    send_message(chat_id, "👋 Привет! Я бот Komorok. Выберите действие:", keyboard)


def handle_admin(chat_id, password=""):
    """Обрабатывает команду /admin."""
    if not password:
        send_message(chat_id, "🔒 Используйте: /admin <пароль>")
        return
    if not ADMIN_DOUBLE_HASH:
        send_message(chat_id, "❌ Хеш администратора не настроен")
        return

    first = hashlib.sha256(password.encode()).hexdigest()
    second = hashlib.sha256(first.encode()).hexdigest()

    if second != ADMIN_DOUBLE_HASH:
        send_message(chat_id, "❌ Неверный пароль!")
        return

    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        send_message(chat_id, f"📋 Отзывы:\n\n{text}" if text else "Нет отзывов")
    except:
        send_message(chat_id, "Нет отзывов")


def main():
    """Главный цикл бота."""
    # Читаем последний update_id
    try:
        with open(UPDATE_FILE, "r") as f:
            offset = int(f.read().strip()) + 1
    except:
        offset = 0

    updates = get_updates(offset)

    for update in updates:
        update_id = update["update_id"]
        offset = update_id

        # Обработка сообщений
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "").strip()

            if text == "/start":
                handle_start(chat_id)
            elif text.startswith("/admin"):
                password = text.removeprefix("/admin").strip()
                handle_admin(chat_id, password)
            elif text.startswith("/"):
                send_message(chat_id, "Неизвестная команда. Используйте /start")
            else:
                # Сохраняем как отзыв
                user = msg.get("from", {})
                name = user.get("first_name", "Аноним")
                username = user.get("username", "")
                with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{name} (@{username}): {text}\n")
                send_message(chat_id, "💬 Спасибо за отзыв! Он сохранён.")
                git_commit_and_push([FEEDBACK_FILE])

        # Обработка нажатий на кнопки
        if "callback_query" in update:
            query = update["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            data = query["data"]

            if data == "check":
                ok = check_site()
                send_message(chat_id, f"{'✅' if ok else '❌'} Сайт Komorok {'работает' if ok else 'не отвечает'}!")
            elif data == "feedback":
                send_message(chat_id, "📝 Напишите ваш отзыв о сайте (одним сообщением).")

    # Сохраняем offset
    with open(UPDATE_FILE, "w") as f:
        f.write(str(offset))


if __name__ == "__main__":
    main()