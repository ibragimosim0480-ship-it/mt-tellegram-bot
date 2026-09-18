import os
import sys
from threading import Thread
from flask import Flask
import telebot
from telebot import types

TOKEN = "8768800680:AAE6LUotvVG8o9iGbuTz5_hgvHDFShmrPsg"
ADMIN_ID = 8516047558  # УБЕДИСЬ, ЧТО ТУТ СТОИТ ТВОЙ РЕАЛЬНЫЙ ID ЦИФРАМИ

bot = telebot.TeleBot(TOKEN)
user_states = {}

# --- 1. НАСТРОЙКА ВЕБ-СЕРВЕРА FLASK ---
app = Flask('')

@app.route('/')
def home():
    return "Бот и Flask работают одновременно!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. ОБРАБОТКА КОМАНД ТЕЛЕГРАМ ---
@bot.message_handler(commands=['call'])
def handle_call(message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

        bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

        keyboard = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="💬 Ответить пользователю", callback_data=f"reply_{user_id}")
        keyboard.add(reply_button)

        notification_text = (
            f"🔔 **ВАС ВЫЗЫВАЮТ!**\n\n"
            f"👤 Кто вызвал: {first_name}\n"
            f"🆔 ID аккаунта: {user_id}\n"
            f"🔗 Ссылка: {username}"
        )

        bot.send_message(ADMIN_ID, notification_text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        print(f"Ошибка в команде /call: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def ask_for_reply(call):
    if call.from_user.id != ADMIN_ID:
        return
    target_user_id = int(call.data.split('_'))
    user_states[ADMIN_ID] = target_user_id
    bot.send_message(ADMIN_ID, "✍️ Введите сообщение для пользователя. Я перешлю его:")
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and ADMIN_ID in user_states)
def send_reply_to_user(message):
    target_user_id = user_states[ADMIN_ID]
    try:
        bot.send_message(target_user_id, f"💬 **Ответ от администратора:**\n\n{message.text}")
        bot.send_message(ADMIN_ID, "🚀 Ваш ответ успешно отправлен человеку!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Не удалось отправить ответ.")
    del user_states[ADMIN_ID]

# --- 3. ПРАВИЛЬНЫЙ ЗАПУСК ПОТОКОВ ---
if __name__ == "__main__":
    # Сначала запускаем фоновый веб-сервер для проверки портов
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True  # Это заставит поток работать на фоне
    server_thread.start()

    # Затем намертво включаем самого бота в основном процессе
    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот @{bot_info.username} успешно запущен на сервере!")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Ошибка поллинга: {e}")
        sys.exit(1)
