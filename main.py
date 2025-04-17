import telebot
from telebot import types
from picarta import Picarta
import os
from datetime import datetime

# API ключи
TG_API_KEY = '7507293866:AAEkZU-wm7IFeGKRbwy3uf10nb11JeZHga0'
GEO_API_KEY = 'RVMCGTHQP4Z4A3IFWF3S'

# Инициализация бота и Picarta
bot = telebot.TeleBot(TG_API_KEY)
localizer = Picarta(GEO_API_KEY)

# Количество оставшихся запросов
left_requests = 100

# Папка для сохранения фото
SAVE_DIR = "photos"
os.makedirs(SAVE_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/help')
    markup.row(btn1)
    bot.send_message(message.chat.id,
                     f'Hello, {message.from_user.first_name}!\nI am a bot that can help you with various tasks.\nType /help to see what I can do.',
                     reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global left_requests
    try:
        bot.send_message(message.chat.id, "📷 Фото получено, обрабатываю...")

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SAVE_DIR, f"photo_{timestamp}.jpg")

        # Сохраняем фото в файл
        with open(file_path, "wb") as f:
            f.write(downloaded_file)

        # Отправляем файл в Picarta
        scanned_location = localizer.localize(file_path)

        if not scanned_location:
            bot.send_message(message.chat.id, "❌ Не удалось определить местоположение.")
            return

        top = scanned_location.get("topk_predictions_dict", {}).get("1", {})
        address = top.get("address", {})
        gps = top.get("gps", [])
        confidence = top.get("confidence", 0)

        response = (
            f"🌍 Предположительно: {address.get('city', '???')}, "
            f"{address.get('province', '')}, {address.get('country', '')}\n"
            f"📍 Координаты: {gps}\n"
            f"🔎 Уверенность: {confidence:.2%}"
        )

        bot.send_message(message.chat.id, response)

        left_requests -= 1
        bot.send_message(message.chat.id, f"🧾 Осталось запросов: {left_requests}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

bot.polling(none_stop=True)
