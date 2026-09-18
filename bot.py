import os
import sys
from threading import Thread
from flask import Flask
import telebot
# Возвращаем types, без них библиотека ругалась на запуск
from telebot import types 

TOKEN = "8768800680:AAE6LUotvVG8o9iGbuTz5_hgvHDFShmrPsg"
ADMIN_ID = 8516047558  # СЮДА ВСТАВЬ СВОЙ ID ИЗ USERINFOBOT (ТОЛЬКО ЦИФРЫ)

bot = telebot.TeleBot(TOKEN)

# --- 1. ВЕБ-СЕРВЕР FLASK ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Бот работает стабильно!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


# --- 2. ОБРАБОТКА КОМАНДЫ /call ---
@bot.message_handler(commands=['call'])
def handle_call(message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

        # Ответ тому, кто вызвал
        bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

        # Уведомление для тебя (ID зашит в самую нижнюю строчку)
        notification_text = (
            f"🔔 **ВАС ВЫЗЫВАЮТ!**\n\n"
            f"👤 Кто вызвал: {first_name}\n"
            f"🆔 ID аккаунта: {user_id}\n"
            f"🔗 Ссылка: {username}\n\n"
            f"✍️ Чтобы ответить человеку, сделай ОТВЕТ (Reply) на это сообщение и напиши свой текст.\n"
            f"ID:{user_id}"
        )

        bot.send_message(ADMIN_ID, notification_text)
    except Exception as e:
        print(f"Ошибка в команде /call: {e}")


# --- 3. ПЕРЕСЫЛКА ОТВЕТА ЧЕРЕЗ REPLY ---
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.reply_to_message is not None)
def send_reply_to_user(message):
    try:
        reply_text = message.reply_to_message.text
        
        # Проверяем, что ты ответил именно на сообщение с вызовом
        if not reply_text or "ID:" not in reply_text:
            return
            
        # Вытаскиваем ID пользователя из строчки ID:XXXXXX
        target_user_id = int(reply_text.split("ID:")[-1].strip())
        
        bot.send_message(target_user_id, f"💬 **Ответ от администратора:**\n\n{message.text}")
        bot.send_message(ADMIN_ID, "🚀 Ваш ответ успешно доставлен человеку!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Не удалось отправить ответ. Ошибка: {e}")


# --- 4. ЗАПУСК ---
if __name__ == "__main__":
    # Включаем Flask на фоне
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    # Включаем самого бота
    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот @{bot_info.username} успешно запущен!")
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"Ошибка поллинга: {e}")
        sys.exit(1)
