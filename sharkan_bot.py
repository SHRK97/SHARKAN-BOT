import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Welcome to SHARKAN BOT. This bot is live 24/7!")
    except Exception as e:
        print(f"[ERROR] /start: {e}")

@bot.message_handler(commands=['status'])
def status(message):
    try:
        bot.reply_to(message, "SHARKAN BOT is active and running smoothly.")
    except Exception as e:
        print(f"[ERROR] /status: {e}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        bot.reply_to(message, "SHARKAN BOT received your message.")
    except Exception as e:
        print(f"[ERROR] echo_all: {e}")

if __name__ == "__main__":
    print("Bot is running...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"[CRITICAL] Bot crashed: {e}")
