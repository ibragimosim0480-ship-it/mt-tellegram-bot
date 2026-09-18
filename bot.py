import os
import sys
from threading import Thread
from flask import Flask
import telebot
from telebot import types

TOKEN = "8768800680:AAE6LUotvVG8o9iGbuTz5_hgvHDFShmrPsg"
ADMIN_ID = 8516047558  # ОБЯЗАТЕЛЬНО ПОСТАВЬ СВОЙ ID ЦИФРАМИ

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

        bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

        # Передаем ID пользователя прямо в скрытые данные кнопки
        keyboard = types.InlineKeyboardMarkup()
        reply_button = types.InlineKeyboardButton(text="💬 Ответить пользователю", callback_data=f"rep_{user_id}")
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


# --- 3. НАЖАТИЕ НА КНОПКУ "ОТВЕТИТЬ" ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('rep_'))
def ask_for_reply(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    # Достаем ID того, кому отвечаем, из кнопки
    target_user_id = call.data.split('_')[1]
    
    # Бот присылает специальное сообщение-инструкцию. На него нужно будет сделать REPLY (ОТВЕТ) в Телеграме!
    msg = bot.send_message(
        ADMIN_ID, 
        f"✍️ Напишите ответ ПРЯМЫМ ОТВЕТОМ (через функцию Ответить/Reply) на это сообщение.\n"
        f"УДАЛЯТЬ СТРОКУ НИЖЕ НЕЛЬЗЯ:\n"
        f"to_user_id:{target_user_id}"
    )
    bot.answer_callback_query(call.id)


# --- 4. ПЕРЕСЫЛКА ОТВЕТА ЧЕРЕЗ ФУНКЦИЮ REPLY В ТЕЛЕГРАМЕ ---
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.reply_to_message is not None)
def send_reply_to_user(message):
    # Проверяем, что админ ответил именно на инструкцию бота
    reply_text = message.reply_to_message.text
    if "to_user_id:" not in reply_text:
        return
        
    try:
        # Вытаскиваем ID пользователя из текста старого сообщения
        target_user_id = int(reply_text.split("to_user_id:")[1].strip())
        
        bot.send_message(target_user_id, f"💬 **Ответ от администратора:**\n\n{message.text}")
        bot.send_message(ADMIN_ID, "🚀 Ваш ответ успешно доставлен человеку!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Не удалось отправить ответ. Ошибка: {e}")


# --- 5. ЗАПУСК ---
if __name__ == "__main__":
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()

    try:
        bot_info = bot.get_me()
        print(f"🤖 Бот @{bot_info.username} успешно запущен!")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Ошибка поллинга: {e}")
        sys.exit(1)
