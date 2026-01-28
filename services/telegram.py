import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

def api(method: str, payload: dict | None = None) -> dict:
    r = requests.post(f"{BASE_URL}/{method}", json=payload or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def send_message(chat_id: str | int, text: str, reply_markup: dict | None = None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("sendMessage", payload)

def answer_callback(callback_query_id: str):
    return api("answerCallbackQuery", {"callback_query_id": callback_query_id})

def get_updates(offset: int | None = None, timeout: int = 0) -> dict:
    payload = {"timeout": timeout}
    if offset is not None:
        payload["offset"] = offset
    return api("getUpdates", payload)
