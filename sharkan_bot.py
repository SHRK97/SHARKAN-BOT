import telebot
import os
import json

# Завантаження збережених профілів
try:
    with open("user_profiles.json", "r") as f:
        user_profiles = json.load(f)
except FileNotFoundError:
    user_profiles = {}
import logging
from ratelimit import limits, RateLimitException
from time import sleep
from functools import wraps
import time
from datetime import datetime
from telebot import types
def save_profiles():
    try:
        with open("user_profiles.json", "w") as f:
            json.dump(user_profiles, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"[SAVE_PROFILE_ERROR] {e}")

# === НАСТРОЙКИ ===
ADMIN_ID = 693609628  # Твій Telegram ID
VERSION = "SHARKAN BOT v1.0 — 2025-05-23"
CALLS = 1
PERIOD = 3
START_TIME = time.time()
user_states = {}       # Стан користувачів (наприклад: очікується відгук)
user_profiles = {}     # Дані профілю користувачів (ріст, вага, ціль)

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
def send_log_to_admin(text):
    try:
        bot.send_message(ADMIN_ID, f"[LOG] {text}")
    except Exception as e:
        logging.error(f"[SEND-LOG-FAIL] {e}")
        
# === КОМАНДА: /start ===
@rate_limited()
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, "Welcome to SHARKAN BOT. This bot is live 24/7!")
                send_log_to_admin(f"/start от {message.from_user.first_name} ({message.from_user.id})")
except Exception as e:
    error_msg = f"/start ERROR: {e}"
    logging.error(error_msg)
    send_log_to_admin(error_msg)

# === КОМАНДА: /status ===
@rate_limited()
@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, "SHARKAN BOT is active and running smoothly.")
        send_log_to_admin(f"/status от {message.from_user.first_name} ({message.from_user.id})")
    except Exception as e:
        error_msg = f"/status ERROR: {e}"
        logging.error(error_msg)
        send_log_to_admin(error_msg)
        
# === КОМАНДА: /профіль ===
@rate_limited()
@bot.message_handler(commands=['профіль'])
def profile_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_states[message.from_user.id] = 'awaiting_height'
        bot.reply_to(message, "Вкажи свій **ріст у сантиметрах** (наприклад, 180):", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"/профіль ERROR: {e}")

# === КОМАНДА: /мійпрофіль ===
@rate_limited()
@bot.message_handler(commands=['мійпрофіль'])
def show_profile(message):
    if message.from_user.id != ADMIN_ID:
        return

    profile = user_profiles.get(message.from_user.id)
    if profile:
        text = (
            f"**Ваш профіль:**\n"
            f"- Зріст: {profile.get('height')} см\n"
            f"- Вага: {profile.get('weight')} кг\n"
            f"- Ціль: {profile.get('goal').capitalize()}"
        )
        bot.reply_to(message, text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Профіль не знайдено. Введіть команду /профіль, щоб створити його.")

# === КОМАНДА: /мійпрофіль ===
@rate_limited()
@bot.message_handler(commands=['мійпрофіль'])
def show_profile(message):
    if message.from_user.id != ADMIN_ID:
        return

    profile = user_profiles.get(message.from_user.id)
    if profile:
        text = (
            f"**Ваш профіль:**\n"
            f"- Зріст: {profile.get('height')} см\n"
            f"- Вага: {profile.get('weight')} кг\n"
            f"- Ціль: {profile.get('goal').capitalize()}"
        )
        bot.reply_to(message, text, parse_mode="Markdown")
    else:
        bot.reply_to(message, "Профіль не знайдено. Введіть команду /профіль, щоб створити його.")

# === КОМАНДА: /startprofile ===
@bot.message_handler(commands=['startprofile'])
def start_profile(message):
    if message.from_user.id != ADMIN_ID:
        return
    user_states[message.from_user.id] = {'stage': 'awaiting_height'}
    bot.reply_to(message, "Введи свій зріст у сантиметрах (наприклад, 175):")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('stage') == 'awaiting_height')
def get_height(message):
    try:
        height = int(message.text)
        user_states[message.from_user.id]['height'] = height
        user_states[message.from_user.id]['stage'] = 'awaiting_weight'
        bot.reply_to(message, "Введи свою вагу у кілограмах (наприклад, 70):")
    except ValueError:
        bot.reply_to(message, "Будь ласка, введи ціле число для зросту.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('stage') == 'awaiting_weight')
def get_weight(message):
    try:
        weight = int(message.text)
        user_states[message.from_user.id]['weight'] = weight
        user_states[message.from_user.id]['stage'] = 'awaiting_goal'
        bot.reply_to(message, "Яка твоя мета? Напиши одну з опцій:\n- схуднути\n- набрати масу\n- підтримувати форму")
    except ValueError:
        bot.reply_to(message, "Будь ласка, введи ціле число для ваги.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('stage') == 'awaiting_goal')
def get_goal(message):
    goal = message.text.lower()
    if goal not in ['схуднути', 'набрати масу', 'підтримувати форму']:
        bot.reply_to(message, "Будь ласка, обери одну з цілей: схуднути, набрати масу, підтримувати форму.")
        return
    user_data = user_states.pop(message.from_user.id)
    user_data['goal'] = goal
    bot.reply_to(message, f"Профіль створено!\nЗріст: {user_data['height']} см\nВага: {user_data['weight']} кг\nМета: {user_data['goal']}")
    notify_admin(f"Новий профіль:\nЗріст: {user_data['height']} см\nВага: {user_data['weight']} кг\nМета: {user_data['goal']}")
    user_profiles[message.from_user.id] = user_data
save_profiles()

# === КОМАНДА: /help ===
@rate_limited()
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(
            message,
            "/start — запуск бота\n"
            "/status — статус\n"
            "/help — помощь\n"
            "/version — версия\n"
            "/menu — визуальное меню"
        )
        send_log_to_admin(f"/help от {message.from_user.first_name} ({message.from_user.id})")
    except Exception as e:
        error_msg = f"/help ERROR: {e}"
        logging.error(error_msg)
        send_log_to_admin(error_msg)

# === КОМАНДА: /donate ===
@rate_limited()
@bot.message_handler(commands=['donate'])
def donate_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        text = (
            "Підтримати SHARKAN BOT:\n\n"
            "Visa (Monobank): 4441 1144 4093 5169\n"
            "MasterCard (Revolut): 5354 5694 3011 9474\n"
            "USDT TRC20: TB1KukkxA29ra597t4uLVy2NjW6g36DmuY\n\n"
            "Дякую за підтримку!"
        )
        bot.reply_to(message, text)
        send_log_to_admin(f"/donate от {message.from_user.first_name} ({message.from_user.id})")
    except Exception as e:
        error_msg = f"/donate ERROR: {e}"
        logging.error(error_msg)
        send_log_to_admin(error_msg)

# === КОМАНДА: /version ===
@rate_limited()
@bot.message_handler(commands=['version'])
def version(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        bot.reply_to(message, VERSION)
        send_log_to_admin(f"/version от {message.from_user.first_name} ({message.from_user.id})")
    except Exception as e:
        error_msg = f"/version ERROR: {e}"
        logging.error(error_msg)
        send_log_to_admin(error_msg)

# === КОМАНДА: /info ===
@rate_limited()
@bot.message_handler(commands=['info'])
def info_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        text = (
            "SHARKAN BOT — це не просто бот. Це інструмент дисципліни, сили й трансформації.\n\n"
            "• Унікальна система викликів, тренувань, мотивації та режимів\n"
            "• Персональні плани й ШІ-наставник\n"
            "• Повністю автономний. Працює 24/7 прямо в Telegram\n"
            "• Створено для тих, хто не боїться болю й хоче результат\n\n"
            "SHARKAN — Добровільна дисципліна = Абсолютна свобода."
        )
        bot.reply_to(message, text)
        send_log_to_admin(f"/info от {message.from_user.first_name} ({message.from_user.id})")
    except Exception as e:
        logging.error(f"/info ERROR: {e}")
        send_log_to_admin(f"/info ERROR: {e}")

# === КОМАНДА: /run ===
@rate_limited()
@bot.message_handler(commands=['run'])
def run_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        weight = user_profiles.get(message.from_user.id, {}).get('weight', None)

        if weight:
            # Предполагаем пробежку 1 км
            distance_km = 1.0
            calories = weight * 1.036 * distance_km
            cal_text = f"\n\nПриблизно спалено: {calories:.0f} ккал (за 1 км бігу)"
        else:
            cal_text = "\n\nЩоб розрахувати калорії — введи свій профіль через /профіль."

        text = (
            "Ти увімкнув режим БІГ.\n"
            "Зараз не час думати — час діяти.\n"
            "Натягни капюшон, увімкни свою музику і біжи, ніби від себе вчорашнього."
            f"{cal_text}"
        )
        bot.reply_to(message, text)
        send_log_to_admin(f"/run від {message.from_user.first_name} ({message.from_user.id})")
    except Exception as e:
        error_msg = f"/run ERROR: {e}"
        logging.error(error_msg)
        send_log_to_admin(error_msg)
        
# === КОМАНДА: /log ===
@rate_limited()
@bot.message_handler(commands=['log'])
def show_log(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with open("log.txt", "r") as f:
            lines = f.readlines()[-20:]  # Показывает последние 20 строк
        log_text = "".join(lines) or "Лог пуст."
        bot.reply_to(message, f"<code>{log_text}</code>", parse_mode="HTML")
    except Exception as e:
        logging.error(f"/log: {e}")
        
# === КОМАНДА: /clearlog ===
@rate_limited()
@bot.message_handler(commands=['clearlog'])
def clear_log(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        open("log.txt", "w").close()
        bot.reply_to(message, "Логи успешно очищены.")
        send_log_to_admin(f"Админ очистил логи.")
    except Exception as e:
        logging.error(f"/clearlog: {e}")
        send_log_to_admin(f"[ERROR] Очистка логов не удалась: {e}")
        
# === КОМАНДА: /stats ===
@rate_limited()
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uptime = int(time.time() - START_TIME)
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}ч {minutes}м {seconds}с"

        text = f"Статистика:\n" \
               f"Версия: {VERSION}\n" \
               f"Аптайм: {uptime_str}\n" \
               f"ID Админа: {ADMIN_ID}"
        bot.reply_to(message, text)
    except Exception as e:
        logging.error(f"/stats: {e}")
@rate_limited()

# === КОМАНДА: /feedback ===
@rate_limited()
@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_states[message.from_user.id] = "awaiting_feedback"
        bot.reply_to(message, "Напиши, будь ласка, свій відгук. Я чекаю...")
    except Exception as e:
        logging.error(f"/feedback: {e}")
@bot.message_handler(commands=['menu'])
def menu(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
markup.add(
    types.InlineKeyboardButton("Статус", callback_data='status'),
    types.InlineKeyboardButton("Помощь", callback_data='help'),
    types.InlineKeyboardButton("Версия", callback_data='version'),
    types.InlineKeyboardButton("Статистика", callback_data='stats'),
    types.InlineKeyboardButton("Залишити відгук", callback_data='feedback'),
    types.InlineKeyboardButton("Очистить логи", callback_data='clearlog'),
    types.InlineKeyboardButton("Підтримати", callback_data='donate'),
    types.InlineKeyboardButton("Про SHARKAN", callback_data='info'),
    types.InlineKeyboardButton("Режим БІГ", callback_data='run'),
    types.InlineKeyboardButton("SHARKAN", url='https://t.me/rulya7777')
    

    bot.send_message(message.chat.id, "Вибери опцію:", reply_markup=markup)
    @bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    elif call.data == 'run':
    send_log_to_admin(f"Кнопка 'Режим БІГ' від {call.from_user.first_name} ({call.from_user.id})")
    run_command(call.message)

    elif call.data == 'info':
    info_command(call.message)
    
    elif call.data == 'donate':
    send_log_to_admin(f"Кнопка 'Підтримати' от {call.from_user.first_name} ({call.from_user.id})")
    donate_command(call.message)
    
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == 'clearlog':
        send_log_to_admin(f"Кнопка 'Очистить логи' от {call.from_user.first_name} ({call.from_user.id})")
        clear_log(call.message)

    elif call.data == 'feedback':
        send_log_to_admin(f"Кнопка 'Залишити відгук' от {call.from_user.first_name} ({call.from_user.id})")
        feedback_command(call.message)

    elif call.data == 'status':
        send_log_to_admin(f"Кнопка 'Статус' от {call.from_user.first_name} ({call.from_user.id})")
        status(call.message)

    elif call.data == 'help':
        send_log_to_admin(f"Кнопка 'Помощь' от {call.from_user.first_name} ({call.from_user.id})")
        help_command(call.message)

    elif call.data == 'version':
        send_log_to_admin(f"Кнопка 'Версия' от {call.from_user.first_name} ({call.from_user.id})")
        version(call.message)

    elif call.data == 'stats':
        send_log_to_admin(f"Кнопка 'Статистика' от {call.from_user.first_name} ({call.from_user.id})")
        stats(call.message)
# === ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ===
@rate_limited()
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        if user_states.get(message.from_user.id) == "awaiting_feedback":
            feedback = message.text
            user_states.pop(message.from_user.id)
            bot.reply_to(message, "Дякую за твій відгук!")
            notify_admin(f"Надійшов новий відгук:\n\n{feedback}")
        else:
            bot.reply_to(message, "SHARKAN BOT received your message.")
    except Exception as e:
        logging.error(f"/echo_all: {e}")

# === ЗАПУСК С АВТО-ПЕРЕЗАПУСКОМ ===
if __name__ == "__main__":
    print("Bot is running...")
    notify_admin("SHARKAN BOT запущен.")
    send_log_to_admin("Бот успешно стартовал.")
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            logging.critical(f"Bot crashed: {e}")
            notify_admin("SHARKAN BOT перезапущен после сбоя!")
            time.sleep(5)
