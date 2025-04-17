# Telegram Geolocation Bot

This project is a Telegram bot that uses the Picarta API to predict the geographical origin of user-submitted photos. The bot interacts with users, processes their images, and returns a list of possible locations based on AI analysis.

## Features

- Receives photos sent by users in Telegram.
- Uses the Picarta API to analyze image location.
- Returns top 5 most likely geolocations with confidence scores.
- Saves each photo to a local folder on the desktop (`TelegramBotPhotos`).
- Inline command interface with interactive buttons.
- Tracks and persists the number of remaining API requests.
- Environment-based API key configuration with `.env` support.

## Setup

1. Clone this repository or download the files.

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:

   ```env
   Telegram-Bot_API=your_telegram_token_here
   Picarta_API=your_picarta_api_key_here
   ```

5. Run the bot:

   ```bash
   python main.py
   ```

## File Structure

```
project_root/
├── main.py
├── requirements.txt
├── .env
├── requests_left.txt
└── TelegramBotPhotos/   # Automatically created folder for saved images
```

## Usage

- Run the bot and open it in Telegram.
- Send a photo to the bot.
- Wait for the analysis to complete.
- The bot will respond with the top 5 predicted locations and confidence levels.
- Use inline buttons like "What can you do?" or "How to use it?" for quick help.

## License

This project is licensed under the MIT License.
