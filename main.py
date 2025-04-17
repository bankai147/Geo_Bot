import telebot
from telebot import types
from picarta import Picarta
import os
from datetime import datetime

# API keys
TG_API_KEY = '7507293866:AAEkZU-wm7IFeGKRbwy3uf10nb11JeZHga0'
GEO_API_KEY = 'RVMCGTHQP4Z4A3IFWF3S'

# Initialize bot and Picarta
bot = telebot.TeleBot(TG_API_KEY)
localizer = Picarta(GEO_API_KEY)

# Path to request counter file
REQUEST_FILE = "requests_left.txt"

# Load remaining requests from file or initialize
if os.path.exists(REQUEST_FILE):
    with open(REQUEST_FILE, "r") as f:
        left_requests = int(f.read())
else:
    left_requests = 100

# Folder for saving photos
SAVE_DIR = "photos"
os.makedirs(SAVE_DIR, exist_ok=True)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    help_button = types.InlineKeyboardButton("Help", callback_data="help")
    keyboard.add(help_button)

    bot.send_message(
        message.chat.id,
        f"Hello, {message.from_user.first_name}!\nI am a bot that can help you with various tasks.",
        reply_markup=keyboard
    )



@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "features":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         "I can analyze your photo and predict where it was taken using Picarta AI.\nJust send me a photo.")
    elif call.data == "instructions":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id,
                         "1. Send me a photo.\n2. Wait for the results.\n3. I will return 5 possible locations.")
    elif call.data == "help":
        bot.answer_callback_query(call.id)
        text = "Here are some things I can do:"
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("What can you do?", callback_data="features")
        btn2 = types.InlineKeyboardButton("How to use it?", callback_data="instructions")
        keyboard.add(btn1, btn2)
        bot.send_message(call.message.chat.id, text, reply_markup=keyboard)


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

        # Send file to Picarta requesting top 5 results
        scanned_location = localizer.localize(file_path, top_k=5)

        results = scanned_location.get("topk_predictions_dict", {})
        if not results:
            bot.send_message(message.chat.id, "❌ Unable to determine location.")
            return

        for rank, prediction in results.items():
            address = prediction.get("address", {})
            gps = prediction.get("gps", [])
            confidence = prediction.get("confidence", 0)

            response = (
                f"#{rank} 🌍 {address.get('city', '???')}, "
                f"{address.get('province', '')}, {address.get('country', '')}\n"
                f"📍 Coordinates: {gps}\n"
                f"🔎 Confidence: {confidence:.2%}"
            )
            bot.send_message(message.chat.id, response)

        # Decrease request counter and save to file
        left_requests -= 1
        with open(REQUEST_FILE, "w") as f:
            f.write(str(left_requests))

        bot.send_message(message.chat.id, f"🧾 Requests left: {left_requests}")

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Error: {e}")

# Remove webhook if any, then start polling
bot.remove_webhook()
bot.polling(none_stop=True)