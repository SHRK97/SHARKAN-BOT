import telebot
import os
import logging

from ratelimit import limits, RateLimitException
from t
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
