#!/usr/bin/env python3
"""Telegram Alerts"""
import requests

TELEGRAM_BOT_TOKEN = "8751634203:AAEtay1djJH_Do7i_ZkBaX7CGXW6SPmAXTY"
CHAT_ID = "8566322083"

class TelegramAlerts:
    def __init__(self):
        print("✈️ Telegram alerts initialized")
    
    def send(self, message):
        print(f"✈️ Telegram: {message}")
        try:
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params={
                "chat_id": CHAT_ID, "text": message
            }, timeout=5)
        except:
            pass
