import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
D_ID_API_KEY = os.getenv("D_ID_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)

menu_keyboard = [["/start", "/help"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я NeyroTwin 🤖\nНапиши текст — и я создам видео с озвучкой.", reply_markup=ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто отправь текст, и я сгенерирую видео с говорящей головой 🎥")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    await update.message.reply_text("🎬 Генерирую видео...")

    response = requests.post(
        "https://api.d-id.com/talks",
        headers={
            "Authorization": f"Basic {D_ID_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "script": {
                "type": "text",
                "input": text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-AriaNeural"
                },
                "ssml": False
            },
            "config": {
                "fluent": True,
                "pad_audio": 0,
                "result_format": "mp4"
            },
            "source_url": "https://create-images-results.d-id.com/DefaultMale.png"
        }
    )

    if response.status_code == 200:
        result = response.json()
        video_url = f"https://api.d-id.com/talks/{result['id']}/video"
        await update.message.reply_text(f"✅ Видео готово: {video_url}")
    else:
        await update.message.reply_text("❌ Ошибка генерации видео.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
