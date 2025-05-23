import telebot
import os
import logging
from ratelimit import limits, RateLimitException
from time import sleep
from functools import wraps
import time
from datetime import datetime

# === НАСТРОЙКИ ===
ADMIN_ID = 693609628  # Твой Telegram ID
VERSION = "SHARKAN BOT v1.0 — 2025-05-23"
CALLS = 1
PERIOD = 3

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

# === ФУНКЦИЯ: ОГРАНИЧЕНИЕ ПО ВРЕМЕНИ ===
def rate_limited(calls=CALLS, period=PERIOD):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            try:
                return limits(calls=calls, period=period)(func)(message, *args, **kwargs)
            except RateLimitException:
                logging.warning(f"[FLOOD] Too many requests from {message.chat.id}")
                bot.reply_to(message, "Too many requests. Please wait a moment.")
        return wrapper
    return decorator

# === ПОЛУЧЕНИЕ ТОКЕНА ===
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# === УВЕДОМЛЕНИЕ АДМИНУ ===
def notify_admin(text):
    try:
        bot.send_message(ADMIN_ID, f"[ALERT] {text}")
    except Exception as e:
        logging.error(f"[ALERT-FAIL] Could not send alert: {e}")

# === КОМАНДА: /start ===
@rate_limited()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, "Welcome to SHARKAN BOT. This bot is live 24/7!")
    except Exception as e:
        logging.error(f"/start: {e}")

# === КОМАНДА: /status ===
@rate_limited()
@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, "SHARKAN BOT is active and running smoothly.")
    except Exception as e:
        logging.error(f"/status: {e}")

# === КОМАНДА: /help ===
@rate_limited()
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, "/start — запуск бота\n/status — статус\n/help — помощь\n/version — версия бота")
    except Exception as e:
        logging.error(f"/help: {e}")

# === КОМАНДА: /version ===
@rate_limited()
@bot.message_handler(commands=['version'])
def version(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, VERSION)
    except Exception as e:
        logging.error(f"/version: {e}")

# === ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ===
@rate_limited()
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, "SHARKAN BOT received your message.")
    except Exception as e:
        logging.error(f"/echo_all: {e}")

# === ЗАПУСК С АВТО-ПЕРЕЗАПУСКОМ ===
if __name__ == "__main__":
    print("Bot is running...")
    notify_admin("SHARKAN BOT запущен.")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            logging.critical(f"Bot crashed: {e}")
            notify_admin("SHARKAN BOT перезапущен после сбоя!")
            time.sleep(5)
