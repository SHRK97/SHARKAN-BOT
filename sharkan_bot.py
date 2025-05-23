
import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to SHARKAN BOT. This bot is live 24/7!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "SHARKAN BOT received your message.")

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
