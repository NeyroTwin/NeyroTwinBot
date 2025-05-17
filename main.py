
import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
FREE_LIMIT = 2

# Тестовый ключ для отладки
D_ID_KEY = "YW12YjVwYlFhNjVhU0FWejpkVnEyODc4VjgxS2M5UjFxZGh1Y3p0d0Rhd0l2aQ"

user_data = {}

@app.route('/')
def index():
    return "NeyroTwinBot is live (debug mode)"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = str(data["message"]["chat"]["id"])
        text = data["message"].get("text", "").lower()

        if chat_id not in user_data:
            user_data[chat_id] = {"videos": [], "used": 0}

        if text == "/start":
            send_message(chat_id, "Привет! Я NeyroTwin 🤖\nНапиши текст — и я создам видео с озвучкой.")
        elif "создать" in text:
            send_message(chat_id, "Напиши текст, который должен озвучить аватар:")
        elif "мои видео" in text:
            videos = user_data[chat_id]["videos"]
            if videos:
                for url in videos:
                    send_message(chat_id, url)
            else:
                send_message(chat_id, "Ты пока не создавал видео.")
        elif text == "/admin" and chat_id == ADMIN_ID:
            total_users = len(user_data)
            send_message(chat_id, f"👨‍💼 Админ-панель\nПользователей: {total_users}")
        else:
            if user_data[chat_id]["used"] >= FREE_LIMIT:
                send_message(chat_id, "⚠️ Лимит бесплатных видео исчерпан. Подпишись, чтобы продолжить.")
            else:
                send_message(chat_id, "Генерирую видео...")
                video_url = generate_did_video(text)
                if video_url:
                    send_video(chat_id, video_url)
                    user_data[chat_id]["videos"].append(video_url)
                    user_data[chat_id]["used"] += 1
                else:
                    send_message(chat_id, "Ошибка генерации видео.")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

def send_video(chat_id, video_url):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    payload = {"chat_id": chat_id, "video": video_url}
    requests.post(url, json=payload)

def generate_did_video(text):
    url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Bearer {D_ID_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "script": {
            "type": "text",
            "input": text,
            "provider": {"type": "microsoft", "voice_id": "en-US-AriaNeural"},
            "ssml": False
        },
        "source_url": "https://create-images-results.d-id.com/DefaultPerson.png"
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        print("D-ID response status:", res.status_code)
        print("D-ID response body:", res.text)
        if res.status_code == 201:
            result = res.json()
            return f"https://talks.d-id.com/{result['id']}.mp4"
        else:
            return None
    except Exception as e:
        print("D-ID exception:", str(e))
        return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
