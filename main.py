import os
from pathlib import Path
from services.telegram import get_updates, send_message, answer_callback

STATE_DIR = Path(".state")
STATE_FILE = STATE_DIR / "last_update_id.txt"

TEST_TEXT = "👋 Хей! Этот бот в разработке.\nСкоро сюда будут приходить гранты по твоим параметрам."

def load_last_update_id() -> int | None:
    if not STATE_FILE.exists():
        return None
    try:
        return int(STATE_FILE.read_text().strip())
    except Exception:
        return None

def save_last_update_id(last_id: int):
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(str(last_id))

def status_keyboard():
    # Inline-кнопка под сообщением
    return {
        "inline_keyboard": [
            [{"text": "📌 Статус", "callback_data": "STATUS"}]
        ]
    }

def handle_message(msg: dict):
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    # /start или просто любой приветственный текст
    if text == "/start":
        send_message(
            chat_id,
            "🤖 Привет! Я Grants Bot.\nНажми кнопку ниже, чтобы проверить статус.",
            reply_markup=status_keyboard()
        )
        return

    # если человек набрал "статус" руками
    if text.lower() in {"статус", "status", "📌 статус"}:
        send_message(chat_id, TEST_TEXT, reply_markup=status_keyboard())
        return

def handle_callback(cb: dict):
    callback_id = cb["id"]
    data = cb.get("data")
    chat_id = cb["message"]["chat"]["id"]

    # чтобы Telegram убрал "часики" на кнопке
    answer_callback(callback_id)

    if data == "STATUS":
        send_message(chat_id, TEST_TEXT, reply_markup=status_keyboard())

def main():
    # читаем последний обработанный update_id
    last_update_id = load_last_update_id()

    # Telegram требует offset = last_update_id + 1
    offset = (last_update_id + 1) if last_update_id is not None else None

    updates = get_updates(offset=offset, timeout=0)
    results = updates.get("result", [])

    if not results:
        print("No new updates")
        return

    max_update_id = last_update_id or 0

    for upd in results:
        uid = upd.get("update_id", 0)
        if uid > max_update_id:
            max_update_id = uid

        if "message" in upd:
            handle_message(upd["message"])
        elif "callback_query" in upd:
            handle_callback(upd["callback_query"])

    save_last_update_id(max_update_id)
    print(f"Processed updates up to {max_update_id}")

if __name__ == "__main__":
    main()
