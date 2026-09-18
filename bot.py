import os
import sys
from threading import Thread
from datetime import datetime, timedelta, timezone
from flask import Flask
import telebot
from telebot import types 

TOKEN = "8768800680:AAHLe-lweVOy2VKv5a54XEMeEcVw_2Ygs-Y"
ADMIN_ID = 8516047558  # ОБЯЗАТЕЛЬНО ПОСТАВЬ СВОЙ ID ЦИФРАМИ

bot = telebot.TeleBot(TOKEN)

# Временный список забаненных ID (после перезагрузки сбросится, но для защиты на день отлично подходит)
BANNED_USERS = set()

# --- 1. ВЕБ-СЕРВЕР FLASK ДЛЯ RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Супер-Бот Гарант работает стабильно!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)


# --- ФУНКЦИЯ ПРОВЕРКИ ВРЕМЕНИ ПО МСК ---
def is_working_hours():
    moscow_tz = timezone(timedelta(hours=3))
    moscow_now = datetime.now(moscow_tz)
    return 9 <= moscow_now.hour < 20


# --- 2. КОМАНДЫ СТАРТ И ПОМОЩЬ ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id in BANNED_USERS:
        return

    if not is_working_hours() and message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "🌙 Администратор сейчас отдыхает. Бот включится утром в 09:00 по МСК.")
        return

    help_text = (
        "👋 **Привет! Я бот-помощник для безопасного обмена Telegram Gifts!**\n\n"
        "📌 **Доступные команды:**\n"
        "📞 `/call` — Подать заявку на сделку через гаранта\n"
        "🧮 `/fee [сумма]` — Посчитать комиссию за сделку в Звёздах\n"
        "🛡️ `/check` — Инструкция, как проверить подарок на подлинность\n"
        "❓ `/help` — Показать это меню\n\n"
        "⏰ **Режим работы:** с 09:00 до 20:00 по МСК."
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")


# --- 3. ФУНКЦИЯ 1: КАЛЬКУЛЯТОР КОМИССИИ (/fee) ---
@bot.message_handler(commands=['fee'])
def calculate_fee(message):
    if message.from_user.id in BANNED_USERS:
        return
        
    try:
        # Берем число после команды /fee
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Напишите сумму сделки через пробел. Например: `/fee 100`", parse_mode="Markdown")
            return
            
        stars = int(args[1])
        # Считаем комиссию (например, 15%)
        fee_stars = round(stars * 0.15)
        if fee_stars < 1:
            fee_stars = 1
            
        # Считаем сколько это в мишках (1 мишка = 15 звезд)
        bears = round(fee_stars / 15, 1)
        if bears < 1:
            bears_text = "1 Мишка (сдачу оставишь себе 😉)"
        else:
            bears_text = f"{bears} шт. Мишек"

        result_text = (
            f"🧮 **Расчет сделки на {stars} 🌟:**\n\n"
            f"🔹 Продавцу прилетит: {stars} Звёзд\n"
            f"🔹 Комиссия гаранта (15%): {fee_stars} Звёзд\n"
            f"🎁 **Оплата за работу гаранту:** {bears_text} (из расчета 1 Мишка = 15 🌟)"
        )
        bot.reply_to(message, result_text, parse_mode="Markdown")
    except ValueError:
        bot.reply_to(message, "❌ Ошибка! Введите сумму сделки целым числом.")


# --- 4. ФУНКЦИЯ 4: ПРОВЕРКА ПОДЛИННОСТИ ГИФТОВ (/check) ---
@bot.message_handler(commands=['check'])
def check_gift_instruction(message):
    if message.from_user.id in BANNED_USERS:
        return
        
    instruction = (
        "🛡️ **АНТИ-ФЕЙК: Как проверить Telegram Gift на подлинность:**\n\n"
        "Мошенники часто присылают поддельные скриншоты подарков из Фотошопа. Вот как проверить всё на 100%:\n\n"
        "1️⃣ **Проверка через профиль:** Настоящий подарок ДОЛЖЕН отображаться во вкладке «Подарки» (Gifts) в профиле у человека, который его вам показывает.\n"
        "2️⃣ **Живой показ:** Попросите человека записать **видео экрана (экранную запись)** или кружочек, где он заходит в Telegram, открывает настройки и показывает этот подарок. На видео подделку сделать невозможно!\n"
        "3️⃣ **Передача гаранту:** Самый надежный способ — продавец пересылает подарок гаранту первым. Пока подарок не у меня на аккаунте, сделка не начинается!"
    )
    bot.reply_to(message, instruction, parse_mode="Markdown")


# --- 5. ФУНКЦИЯ 2: ЧЁРНЫЙ СПИСОК (/ban И /unban ДЛЯ АДМИНА) ---
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Напиши ID. Например: `/ban 123456789`")
            return
        user_id = int(args[1])
        BANNED_USERS.add(user_id)
        bot.reply_to(message, f"🚫 Пользователь {user_id} успешно добавлен в Чёрный список!")
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат ID.")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ Напиши ID. Например: `/unban 123456789`")
            return
        user_id = int(args[1])
        BANNED_USERS.discard(user_id)
        bot.reply_to(message, f"🟢 Пользователь {user_id} разбанен.")
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат ID.")


# --- 6. ОБРАБОТКА КОМАНДЫ /call ---
@bot.message_handler(commands=['call'])
def handle_call(message):
    if message.from_user.id in BANNED_USERS:
        return

    try:
        if not is_working_hours():
            bot.reply_to(message, "🌙 Извините, приём заявок окончен. Администратор отдыхает до 09:00 по МСК.")
            return

        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "нет юзернейма"

        bot.reply_to(message, "✅ Ваша заявка гаранту успешно отправлена! Ожидайте ответа администратора.")

        notification_text = (
            f"🔔 **НОВАЯ ЗАЯВКА НА СДЕЛКУ!**\n\n"
            f"👤 Клиент: {first_name}\n"
            f"🆔 ID аккаунта: {user_id}\n"
            f"🔗 Ссылка: {username}\n\n"
            f"✍️ Чтобы ответить человеку, сделай ОТВЕТ (Reply) на это сообщение.\n"
            f"ID:{user_id}"
        )
        bot.send_message(ADMIN_ID, notification_text)
    except Exception as e:
        print(f"Ошибка в команде /call: {e}")


# --- 7. ПЕРЕСЫЛКА ОТВЕТА АДМИНИСТРАТОРА ЧЕРЕЗ REPLY ---
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.reply_to_message is not None)
def send_reply_to_user(message):
    try:
        reply_text = message.reply_to_message.text
        if not reply_text or "ID:" not in reply_text:
            return
            
        target_user_id = int(reply_text.split("ID:")[-1].strip())
        
        bot.send_message(target_user_id, f"💬 **Ответ от Гаранта:**\n\n{message.text}")
        bot.send_message(ADMIN_ID, "🚀 Ответ успешно доставлен!")
    except Exception as e:
        bot.send_message(ADMIN_ID, f"❌ Не удалось отправить ответ. Ошибка: {e}")


# --- 8. ЗАПУСК ---
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
