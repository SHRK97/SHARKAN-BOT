import telebot
import os
import logging
from ratelimit import limits, RateLimitException
from time import sleep
from functools import wraps

# Защита от флуда: максимум 1 запрос в 3 секунды от одного пользователя
CALLS = 1
PERIOD = 3

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

# Логирование
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@rate_limited()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Welcome to SHARKAN BOT. This bot is live 24/7!")
    except Exception as e:
        logging.error(f"/start: {e}")

@rate_limited()
@bot.message_handler(commands=['status'])
def status(message):
    try:
        bot.reply_to(message, "SHARKAN BOT is active and running smoothly.")
    except Exception as e:
        logging.error(f"/status: {e}")

@rate_limited()
@bot.message_handler(commands=['ping'])
def ping(message):
    try:
        bot.reply_to(message, "PONG — бот на связи.")
    except Exception as e:
        logging.error(f"/ping: {e}")

@rate_limited()
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        bot.reply_to(message, "SHARKAN BOT received your message.")
    except Exception as e:
        logging.error(f"/echo_all: {e}")

if __name__ == "__main__":
    print("Bot is running...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.critical(f"Bot crashed: {e}")
