import os
import sys
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# ТОКЕН ТВОЕГО БОТА
TOKEN = "8768800680:AAE6LUotvVG8o9iGbuTz5_hgvHDFShmrPsg"

# СЮДА ВСТАВЬ СВОЙ ID ИЗ USERINFOBOT (ТОЛЬКО ЦИФРЫ, БЕЗ КАВЫЧЕК)
ADMIN_ID = 8516047558  

# --- 1. ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ОШИБКИ ПОРТОВ НА RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Бот успешно работает на сервере!"

def run_web_server():
    # Render автоматически выдает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. НАСТРОЙКА ТЕЛЕГРАМ БОТА ---
bot = telebot.TeleBot(TOKEN)
user_states = {}

# Обработка команды /call
@bot.message_handler(commands=['call'])
def handle_call(message):
    try:
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

        # Ответ тому, кто вызвал
        bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

        # Создаем кнопку "Ответить" для тебя
        keyboard = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="💬 Ответить пользователю", callback_data=f"reply_{user_id}")
        keyboard.add(reply_button)

        notification_text = (
            f"🔔 **ВАС ВЫЗЫВАЮТ!**\n\n"
            f"👤 Кто вызвал: {first_name}\n"
            f"🆔 ID аккаунта: {user_id}\n"
            f"🔗 Ссылка: {username}"
        )

        # Отправка уведомления тебе в личку с кнопкой
        bot.send_message(ADMIN_ID, notification_text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        print(f"Ошибка в команде /call: {e}")

# Обработка нажатия на кнопку "Ответить"
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def ask_for_reply(call):
    if call.from_user.id != ADMIN_ID:
        return
    target_user_id = int(call.data.split('_')[1])
    user_states[ADMIN_ID] = target_user_id
    bot.send_message(ADMIN_ID, "✍️ Введите сообщение для пользователя. Я перешлю его от имени бота:")
    bot.answer_callback_query(call.id)

# Пересылка твоего ответа обратно пользователю
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and ADMIN_ID in user_states)
def send_reply_to_user(message):
    target_user_id = user_states[ADMIN_ID]
    try:
        bot.send_message(target_user_id, f"💬 **Ответ от администратора:**\n\n{message.text}")
        bot.send_message(ADMIN_ID, "🚀 Ваш ответ успешно отправлен человеку!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Не удалось отправить ответ.")
    del user_states[ADMIN_ID]

# --- 3. ЗАПУСК ОБОИХ СЕРВИСОВ ОДНОВРЕМЕННО ---
if __name__ == "__main__":
    # Запускаем веб-сервер в отдельном потоке, чтобы Render не ругался на порты
    server_thread = Thread(target=run_web_server)
    server_thread.start()

    # Запускаем самого бота
    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот @{bot_info.username} успешно запущен!")
        bot.infinity_polling()
    except Exception as e:
        print(f"Ошибка поллинга: {e}")
        sys.exit(1)
