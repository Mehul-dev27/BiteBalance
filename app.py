"""
BiteBalance Meta WhatsApp Cloud API Webhook Server.
"""
import logging
import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import requests

from nutrition_core import analyze_meal

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def send_whatsapp_message(to_number: str, text: str):
    """Sends a text message back to the user via Meta WhatsApp Cloud API."""
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        logging.info(f"Message successfully sent to {to_number}")
    except Exception as e:
        logging.error(f"Failed to send WhatsApp message: {e}")

def get_whatsapp_media_bytes(media_id: str) -> tuple[bytes, str]:
    """Downloads an image from Meta Graph API using its media ID."""
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    meta_url = f"https://graph.facebook.com/v20.0/{media_id}"
    res = requests.get(meta_url, headers=headers, timeout=10)
    res.raise_for_status()
    meta_data = res.json()
    download_url = meta_data.get("url")
    mime_type = meta_data.get("mime_type", "image/jpeg")

    media_res = requests.get(download_url, headers=headers, timeout=20)
    media_res.raise_for_status()
    return media_res.content, mime_type

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta webhook verification handshake."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logging.info("Webhook verified successfully.")
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    """Processes incoming WhatsApp messages."""
    data = request.get_json()

    if not data or "entry" not in data:
        return jsonify({"status": "ignored"}), 200

    try:
        changes = data["entry"][0].get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return jsonify({"status": "no_messages"}), 200

        msg = messages[0]
        sender_phone = msg.get("from")
        msg_type = msg.get("type")

        user_text = None
        img_bytes = None
        mime_type = "image/jpeg"

        if msg_type == "text":
            user_text = msg["text"].get("body", "")
        elif msg_type == "image":
            image_id = msg["image"].get("id")
            user_text = msg["image"].get("caption")
            img_bytes, mime_type = get_whatsapp_media_bytes(image_id)
        else:
            send_whatsapp_message(
                sender_phone,
                "👋 Namaste! BiteBalance analyzes meal photos or text descriptions (e.g., '2 rotis, dal, bhindi'). Please send a meal to review!",
            )
            return jsonify({"status": "unsupported_type"}), 200

        advice = analyze_meal(user_text=user_text, image_bytes=img_bytes, mime_type=mime_type)
        send_whatsapp_message(sender_phone, advice)

    except Exception as e:
        logging.error(f"Error handling incoming message: {e}")

    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)