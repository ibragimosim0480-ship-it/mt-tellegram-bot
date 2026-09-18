import os
import sys
from threading import Thread
from datetime import datetime, timedelta, timezone
from flask import Flask
import telebot
from telebot import types 

TOKEN = "8768800680:AAHLe-lweVOy2VKv5a54XEMeEcVw_2Ygs-Y"
ADMIN_ID = 8516047558  # ТВОЙ ID ЦИФРАМИ БЕЗ КАВЫЧЕК

bot = telebot.TeleBot(TOKEN)

# --- 1. ВЕБ-СЕРВЕР FLASK ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Бот работает стабильно!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


# --- ФУНКЦИЯ ПРОВЕРКИ РАБОЧЕГО ВРЕМЕНИ ПО МСК ---
def is_working_hours():
    # Создаем часовой пояс Москвы (UTC+3)
    moscow_tz = timezone(timedelta(hours=3))
    # Получаем текущее точное время по Москве
    moscow_now = datetime.now(moscow_tz)
    current_hour = moscow_now.hour

    # Бот работает с 9 утра (включая 9:00) до 8 вечера (в 20:00 уже отключается)
    if 9 <= current_hour < 20:
        return True
    return False


# --- 2. ОБРАБОТКА КОМАНДЫ /start И /help ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        # Если ночь — бот не реагирует или вежливо пишет, что спит
        if not is_working_hours():
            bot.reply_to(message, "🌙 Администратор сейчас отдыхает. Бот включится утром в 09:00 по МСК.")
            return

        help_text = (
            "👋 **Привет! Я бот обратной связи.**\n\n"
            "📌 **Доступные команды:**\n"
            "🔹 `/call` — Отправить экстренный вызов администратору\n"
            "🔹 `/help` — Показать это окно помощи\n\n"
            "⏰ **Режим работы:** с 09:00 до 20:00 по МСК."
        )
        bot.reply_to(message, help_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка в команде помощи: {e}")


# --- 3. ОБРАБОТКА КОМАНДЫ /call ---
@bot.message_handler(commands=['call'])
def handle_call(message):
    try:
        # Проверяем время перед отправкой вызова
        if not is_working_hours():
            bot.reply_to(message, "🌙 Извините, приём заявок окончен. Администратор отдыхает до 09:00 по МСК.")
            return

        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

        bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

        notification_text = (
            f"🔔 **ВАС ВЫЗЫВАЮТ!**\n\n"
            f"👤 Кто вызвал: {first_name}\n"
            f"🆔 ID аккаунта: {user_id}\n"
            f"🔗 Ссылка: {username}\n\n"
            f"ID:{user_id}"
        )

        bot.send_message(ADMIN_ID, notification_text)
    except Exception as e:
        print(f"Ошибка в команде /call: {e}")


# --- 4. ЕСЛИ ПОЛЬЗОВАТЕЛЬ ПИШЕТ ЛЮБОЙ ДРУГОЙ ТЕКСТ ---
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def handle_unknown_text(message):
    try:
        if not is_working_hours():
            bot.reply_to(message, "🌙 Бот спит до 09:00 по МСК. Сообщения не принимаются.")
            return
            
        bot.reply_to(
            message, 
            "⚠️ Я не понимаю обычные сообщения.\n"
            "Чтобы связаться с администратором, отправьте команду `/call`."
        )
    except Exception as e:
        print(f"Ошибка обработки текста: {e}")


# --- 5. П ПЕРЕСЫЛКА ОТВЕТА АДМИНИСТРАТОРА ЧЕРЕЗ REPLY ---
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.reply_to_message is not None)
def send_reply_to_user(message):
    try:
        reply_text = message.reply_to_message.text
        if not reply_text or "ID:" not in reply_text:
            return
            
        target_user_id = int(reply_text.split("ID:")[-1].strip())
        
        bot.send_message(target_user_id, f"💬 **Ответ от администратора:**\n\n{message.text}")
        bot.send_message(ADMIN_ID, "🚀 Ваш ответ успешно доставлен человеку!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Не удалось отправить ответ. Ошибка: {e}")


# --- 6. ЗАПУСК ---
if __name__ == "__main__":
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот @{bot_info.username} успешно запущен!")
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Ошибка поллинга: {e}")
        sys.exit(1)
