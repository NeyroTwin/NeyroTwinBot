
import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
D_ID_KEY = os.getenv("D_ID_KEY")
ADMIN_ID = os.getenv("ADMIN_ID")

@app.route('/')
def index():
    return "NeyroTwinBot is running!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "").lower()

        if text == "/start":
            send_message(chat_id, "Привет! Я NeyroTwin 🤖\nНапиши текст — и я создам видео с озвучкой.")
        elif text in ["создать аватар", "🎙 создать аватар"]:
            send_message(chat_id, "Напиши текст, который должен озвучить аватар:")
        elif text in ["мои видео", "🎬 мои видео"]:
            send_message(chat_id, "Здесь пока пусто. Когда появятся видео — я их пришлю.")
        elif text in ["помощь", "❓ помощь"]:
            send_message(chat_id, "Я создаю видео с озвучкой по тексту. Просто напиши фразу — и получишь результат!")
        else:
            send_message(chat_id, "Генерирую видео... (заглушка)")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
