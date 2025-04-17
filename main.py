import telebot
from telebot import types
from picarta import Picarta
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# Hidden API keys
TG_API_KEY = os.getenv("TG_API_KEY")
GEO_API_KEY = os.getenv("GEO_API_KEY")

# Initialize bot and Picarta
bot = telebot.TeleBot(TG_API_KEY)
localizer = Picarta(GEO_API_KEY)

# Number of remaining requests
left_requests = 100

# Folder for saving photos
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
        bot.send_message(message.chat.id, "📷 Photo received, processing...")

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(SAVE_DIR, f"photo_{timestamp}.jpg")

        # Save photo to file
        with open(file_path, "wb") as f:
            f.write(downloaded_file)

        # Send file to Picarta
        scanned_location = localizer.localize(file_path)

        if not scanned_location:
            bot.send_message(message.chat.id, "❌ Unable to determine location.")
            return

        top = scanned_location.get("topk_predictions_dict", {}).get("1", {})
        address = top.get("address", {})
        gps = top.get("gps", [])
        confidence = top.get("confidence", 0)

        response = (
            f"🌍 Possibly: {address.get('city', '???')}, "
            f"{address.get('province', '')}, {address.get('country', '')}\n"
            f"📍 Coordinates: {gps}\n"
            f"🔎 Confidence: {confidence:.2%}"
        )

        bot.send_message(message.chat.id, response)

        left_requests -= 1
        bot.send_message(message.chat.id, f"🧾 Requests left: {left_requests}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {e}")

bot.polling(none_stop=True)
