import os
import telebot

# Получаем токен из настроек сервера
TOKEN = "8768800680:AAHam5grpXhdh0gLLSQy8G03UJmFjZcMuJY"
ADMIN_ID = 8516047558  # ЗАМЕНИТЕ НА СВОЙ ID ИЗ USERINFOBOT (ТОЛЬКО ЦИФРЫ)

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['call'])
def handle_call(message):
  user_id = message.from_user.id
  first_name = message.from_user.first_name
  username = (
      f"@{message.from_user.username}"
      if message.from_user.username
      else "нет юзернейма"
  )

  bot.reply_to(message, "✅ Ваш вызов успешно отправлен администратору!")

  notification_text = (
      f"🔔 ВАС ВЫЗЫВАЮТ!\n\n"
      f"👤 Кто вызвал: {first_name}\n"
      f"🆔 ID аккаунта: {user_id}\n"
      f"🔗 Ссылка: {username}"
  )

  try:
    bot.send_message(ADMIN_ID, notification_text)
  except Exception as e:
    print(f"Ошибка отправки: {e}")


# Файл конфигурации для сервера Amvera
if not os.path.exists("amvera.yml"):
  with open("amvera.yml", "w", encoding="utf-8") as f:
    f.write("meta:\n  environment: python\n  toolchain:\n    name: pip\n    version: 3.11\nrun:\n  scriptName: bot.py\n")

# Файл со списком библиотек для сервера
if not os.path.exists("requirements.txt"):
  with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("pyTelegramBotAPI\n")

print("Файлы для хостинга успешно подготовлены!")
bot.infinity_polling()
