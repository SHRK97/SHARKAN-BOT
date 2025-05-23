import os
import json
import logging
import time
from datetime import datetime
from functools import wraps
from time import sleep

from ratelimit import limits, RateLimitException
import telebot
from telebot import types

# === Константи ===
ADMIN_ID = 693609628
VERSION = "SHARKAN BOT v1.0 — 2025-05-23"
CALLS = 1
PERIOD = 3
START_TIME = time.time()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
user_states = {}

# === Логування ===
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)

# === Завантаження збережених профілів ===
try:
    with open("user_profiles.json", "r") as f:
        user_profiles = json.load(f)
except FileNotFoundError:
    user_profiles = {}

def save_profiles():
    try:
        with open("user_profiles.json", "w") as f:
            json.dump(user_profiles, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"[SAVE_PROFILE_ERROR] {e}")

# === Обмеження запитів ===
def rate_limited(calls=CALLS, period=PERIOD):
    def decorator(func):
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            try:
                return limits(calls=calls, period=period)(func)(message, *args, **kwargs)
            except RateLimitException:
                logging.warning(f"[FLOOD] Too many requests from {message.chat.id}")
                bot.reply_to(message, "Забагато запитів. Зачекайте трохи.")
        return wrapper
    return decorator

# === Повідомлення адміну ===
def notify_admin(text):
    try:
        bot.send_message(ADMIN_ID, f"[ALERT] {text}")
    except Exception as e:
        logging.error(f"[ALERT-FAIL] {e}")

def send_log_to_admin(text):
    try:
        bot.send_message(ADMIN_ID, f"[LOG] {text}")
    except Exception as e:
        logging.error(f"[SEND-LOG-FAIL] {e}")

# === Команди ===
@rate_limited()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "Welcome to SHARKAN BOT. This bot is live 24/7!")
    send_log_to_admin(f"/start від {message.from_user.first_name} ({message.from_user.id})")

@rate_limited()
@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.reply_to(message, "SHARKAN BOT працює стабільно.")
    send_log_to_admin(f"/status від {message.from_user.first_name} ({message.from_user.id})")

@rate_limited()
@bot.message_handler(commands=['профіль'])
def profile_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    user_states[message.from_user.id] = {'stage': 'awaiting_height'}
    bot.reply_to(message, "Введи свій зріст у сантиметрах (наприклад, 175):")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('stage') == 'awaiting_height')
def get_height(message):
    try:
        height = int(message.text)
        user_states[message.from_user.id]['height'] = height
        user_states[message.from_user.id]['stage'] = 'awaiting_weight'
        bot.reply_to(message, "Введи свою вагу у кілограмах (наприклад, 70):")
    except ValueError:
        bot.reply_to(message, "Будь ласка, введи число.")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('stage') == 'awaiting_weight')
def get_weight(message):
    try:
        weight = int(message.text)
        user_states[message.from_user.id]['weight'] = weight
        user_states[message.from_user.id]['stage'] = 'awaiting_goal'
        bot.reply_to(message, "Яка твоя мета?\n- схуднути\n- набрати масу\n- підтримувати форму")
    except ValueError:
        bot.reply_to(message, "Будь ласка, введи число.")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('stage') == 'awaiting_goal')
def get_goal(message):
    try:
        goal = message.text.lower()
        if goal not in ['схуднути', 'набрати масу', 'підтримувати форму']:
            bot.reply_to(message, "Оберіть мету: схуднути, набрати масу, підтримувати форму.")
            return
        data = user_states.pop(message.from_user.id)
        data['goal'] = goal
        user_profiles[message.from_user.id] = data
        save_profiles()
        bot.reply_to(
            message,
            f"Профіль створено!\nЗріст: {data['height']} см\nВага: {data['weight']} кг\nМета: {data['goal']}"
        )
        notify_admin(
            f"Новий профіль:\nЗріст: {data['height']} см\nВага: {data['weight']} кг\nМета: {data['goal']}"
        )
    except Exception as e:
        bot.reply_to(message, "Помилка при збереженні профілю.")
        logging.error(f"[GOAL_HANDLER_ERROR] {e}")

@rate_limited()
@bot.message_handler(commands=['мійпрофіль'])
def show_profile(message):
    if message.from_user.id != ADMIN_ID:
        return
    profile = user_profiles.get(message.from_user.id)
    if profile:
        text = (
            f"**Профіль:**\n"
            f"- Зріст: {profile['height']} см\n"
            f"- Вага: {profile['weight']} кг\n"
            f"- Мета: {profile['goal']}"
        )
        bot.reply_to(message, text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Профіль не знайдено. Введіть /профіль")

@rate_limited()
@bot.message_handler(commands=['run'])
def run_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    weight = user_profiles.get(message.from_user.id, {}).get('weight')
    if weight:
        calories = weight * 1.036
        cal_text = f"Приблизно: {calories:.0f} ккал (за 1 км бігу)"
    else:
        cal_text = "Введіть профіль через /профіль, щоб бачити калорії."
    bot.reply_to(message, f"Режим БІГ активовано!\n{cal_text}")

# === Запуск ===
if __name__ == "__main__":
    print("Bot is running...")
    notify_admin("SHARKAN BOT запущен.")
    send_log_to_admin("Бот успішно стартував.")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            logging.critical(f"Bot crashed: {e}")
            notify_admin("SHARKAN BOT перезапущен після збою!")
            time.sleep(5)
