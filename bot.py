import os
import sys
import telebot
from telebot import types

TOKEN = "8768800680:AAHAm5grpXhdh0gLLSqy8G03UjFjZcMuJY"
ADMIN_ID = 8516047558  # ВСТАВЬ СЮДА СВОЙ ID ИЗ USERINFOBOT (ТОЛЬКО ЦИФРЫ)

# Проверяем, что ID изменен
if ADMIN_ID == 123456789:
  print("❌ ОШИБКА: Вы забыли заменить 123456789 на свой реальный Telegram ID!")
  sys.exit(1)

try:
  bot = telebot.TeleBot(TOKEN)
  user_states = {}
  print("✅ Объект бота успешно создан...")
except Exception as e:
  print(f"❌ ОШИБКА ПРИ СОЗДАНИИ БОТА: {e}")
  sys.exit(1)


# --- ОБРАБОТКА КОМАНДЫ /call ---
@bot.message_handler(commands=['call'])
def handle_call(message):
  try:
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "нет юзернейма"
    )

    bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

    keyboard = types.InlineKeyboardMarkup()
    reply_button = types.InlineKeyboardButton(
        text="💬 Ответить пользователю", callback_data=f"reply_{user_id}"
    )
    keyboard.add(reply_button)

    notification_text = (
        f"🔔 **ВАС ВЫЗЫВАЮТ!**\n\n"
        f"👤 Кто вызвал: {first_name}\n"
        f"🆔 ID аккаунта: {user_id}\n"
        f"🔗 Ссылка: {username}\n\n"
        f"Чтобы связаться, нажмите кнопку ниже:"
    )

    bot.send_message(
        ADMIN_ID,
        notification_text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
  except Exception as e:
    print(f"❌ Ошибка внутри команды /call: {e}")


# --- ОБРАБОТКА НАЖАТИЯ НА КНОПКУ "ОТВЕТИТЬ" ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def ask_for_reply(call):
  if call.from_user.id != ADMIN_ID:
    return
  target_user_id = int(call.data.split('_')[1])
  user_states[ADMIN_ID] = target_user_id
  bot.send_message(
      ADMIN_ID,
      "✍️ Введите сообщение для пользователя. Я перешлю его от вашего имени:",
  )
  bot.answer_callback_query(call.id)


# --- ПЕРЕСЫЛКА ОТВЕТА АДМИНИСТРАТОРА ---
@bot.message_handler(
    func=lambda message: message.from_user.id == ADMIN_ID
    and ADMIN_ID in user_states
)
def send_reply_to_user(message):
  target_user_id = user_states[ADMIN_ID]
  try:
    bot.send_message(
        target_user_id, f"💬 **Ответ от администратора:**\n\n{message.text}"
    )
    bot.send_message(ADMIN_ID, "🚀 Ваш ответ успешно отправлен человеку!")
  except Exception as e:
    bot.send_message(
        ADMIN_ID,
        f"❌ Не удалось отправить. Возможно, пользователь заблокировал бота.",
    )
  del user_states[ADMIN_ID]


# --- ЗАПУСК ПОЛЛИНГА С ВЫВОДОМ КРИТИЧЕСКИХ ОШИБОК ---
try:
  bot_info = bot.get_me()
  print("==========================================")
  print(f"🤖 Бот @{bot_info.username} успешно запустился на сервере!")
  print("==========================================")
  bot.infinity_polling()
except Exception as e:
  print("🚨 КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ ПОЛЛИНГА!")
  print(f"Текст ошибки от Telegram: {e}")
  sys.exit(1)
