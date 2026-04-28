#!/usr/bin/env python3
"""
AI24x7 Multilingual Voice Bot v2c
Fixed: async event loop + reply_mode (voice/text) + proper settings
11 languages + voice/text toggle
"""
import asyncio, json, logging, os, sys, subprocess
from pathlib import Path
from aiohttp import web
import sqlite3, requests

ROOT = Path("/opt/ai24x7-docker/factory")
sys.path.insert(0, str(ROOT))

TEMP_AUDIO = Path("/tmp/ai24x7_audio")
TEMP_AUDIO.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("voicebot")

DB_PATH = "/opt/ai24x7-docker/factory/dashboard/factory_data.db"

EDGE_VOICES = {
    "hi": "hi-IN-MadhurNeural", "en": "en-IN-NeerjaNeural",
    "mr": "mr-IN-AarohiNeural", "gu": "gu-IN-DhwaniNeural",
    "ta": "ta-IN-PallaviNeural", "te": "te-IN-ShrutiNeural",
    "kn": "kn-IN-SapnaNeural", "ml": "ml-IN-SobhanaNeural",
    "bn": "bn-IN-TanishaaNeural",
}

LANG_META = {
    "hi": {"name": "Hindi", "native": "हिंदी", "flag": "🇮🇳"},
    "en": {"name": "English", "native": "English", "flag": "🇬🇧"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇲🇷"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "flag": "🇬🇾"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "flag": "🇮🇳"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇧🇩"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳"},
    "raj": {"name": "Rajasthani", "native": "राजस्थानी", "flag": "🇮🇳"},
}

# ── Async-safe TTS ─────────────────────────────────────────────
async def _edge_tts(text: str, voice: str, out_path: str) -> bool:
    try:
        import edge_tts
        await edge_tts.Communicate(text, voice).save(out_path)
        return os.path.getsize(out_path) > 500
    except Exception as e:
        logger.error(f"Edge TTS: {e}")
        return False

def _gtts(text: str, lang: str, out_path: str) -> bool:
    try:
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, _do_gtts_sync, text, lang, out_path)
        return loop.run_until_complete(future)
    except Exception as e:
        try:
            return _do_gtts_sync(text, lang, out_path)
        except:
            return False

def _do_gtts_sync(text: str, lang: str, out_path: str) -> bool:
    subprocess.run(["/usr/bin/python3", "-c",
        f"from gtts import gTTS; gTTS(text={repr(text)}, lang={repr(lang)}).save({repr(out_path)})"],
        capture_output=True, timeout=30)
    return os.path.getsize(out_path) > 500 if os.path.exists(out_path) else False

async def tts_generate(text: str, lang: str, out_path: str) -> bool:
    if lang in EDGE_VOICES:
        return await _edge_tts(text, EDGE_VOICES[lang], out_path)
    elif lang == "pa":
        return _gtts(text, "pa", out_path)
    elif lang == "raj":
        return _gtts(text, "hi", out_path)
    return False

# ── DB ──────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS user_languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, platform TEXT NOT NULL,
        platform_id TEXT NOT NULL, language TEXT NOT NULL DEFAULT 'hi',
        voice_enabled INTEGER DEFAULT 1, call_enabled INTEGER DEFAULT 0,
        reply_mode TEXT DEFAULT 'voice',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(platform, platform_id))""")
    conn.commit()
    conn.close()

def get_prefs(platform: str, pid: str) -> dict:
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT language, voice_enabled, call_enabled, reply_mode FROM user_languages WHERE platform=? AND platform_id=?",
                  (platform, str(pid)))
        row = c.fetchone()
        conn.close()
        if row:
            return {"language": row[0], "voice": bool(row[1]), "call": bool(row[2]), "mode": row[3] or "voice"}
    except:
        pass
    return {"language": "hi", "voice": True, "call": False, "mode": "voice"}

def set_lang(platform: str, pid: str, lang: str):
    if lang not in LANG_META:
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO user_languages (platform, platform_id, language, reply_mode, updated_at)
            VALUES (?, ?, ?, 'voice', datetime('now'))
            ON CONFLICT(platform, platform_id) DO UPDATE SET language=excluded.language, reply_mode='voice', updated_at=datetime('now')
        """, (platform, str(pid), lang))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"set_lang: {e}")

def set_reply_mode(platform: str, pid: str, mode: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO user_languages (platform, platform_id, language, reply_mode, updated_at)
            VALUES (?, ?, 'hi', ?, datetime('now'))
            ON CONFLICT(platform, platform_id) DO UPDATE SET reply_mode=excluded.reply_mode, updated_at=datetime('now')
        """, (platform, str(pid), mode))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"set_reply_mode: {e}")

def toggle_voice(platform: str, pid: str):
    prefs = get_prefs(platform, pid)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO user_languages (platform, platform_id, language, voice_enabled, reply_mode, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(platform, platform_id) DO UPDATE SET
                voice_enabled=excluded.voice_enabled, updated_at=datetime('now')
        """, (platform, str(pid), prefs["language"], int(not prefs["voice"]), prefs["mode"]))
        conn.commit()
        conn.close()
    except:
        pass

# ── Config ─────────────────────────────────────────────────────
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""
WA_API_KEY = ""
WA_PHONE_ID = ""

def load_config():
    global TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, WA_API_KEY, WA_PHONE_ID
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for key, var in [("alert_telegram_token","TELEGRAM_TOKEN"),
                         ("alert_telegram_chat_id","TELEGRAM_CHAT_ID"),
                         ("alert_whatsapp_api_key","WA_API_KEY"),
                         ("alert_whatsapp_phone_id","WA_PHONE_ID")]:
            c.execute("SELECT value FROM config WHERE key=?", (key,))
            row = c.fetchone()
            if row:
                globals()[var] = row[0]
        conn.close()
    except:
        pass

# ── Telegram API helpers ────────────────────────────────────────
def tg_send(text: str, chat_id: str = None):
    if not TELEGRAM_TOKEN:
        return False
    cid = chat_id or TELEGRAM_CHAT_ID
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": cid, "text": text, "parse_mode": "HTML"}, timeout=10)
        return r.status_code == 200
    except:
        return False

def tg_reply_markup(chat_id: str, text: str, rmk: str):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown",
                  "reply_markup": rmk}, timeout=10)
        return r.status_code == 200
    except:
        return False

def tg_edit_markup(chat_id: str, msg_id: int, rmk: str):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageReplyMarkup",
            json={"chat_id": chat_id, "message_id": msg_id, "reply_markup": rmk}, timeout=5)
    except:
        pass

def tg_answer_cb(query_id: str, text: str = "", alert: bool = False):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
            json={"callback_query_id": query_id, "text": text, "show_alert": alert}, timeout=5)
    except:
        pass

def tg_send_voice(audio_path: str, chat_id: str = None, caption: str = ""):
    if not TELEGRAM_TOKEN or not os.path.exists(audio_path):
        return False
    cid = chat_id or TELEGRAM_CHAT_ID
    try:
        with open(audio_path, "rb") as f:
            r = requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice",
                data={"chat_id": cid, "caption": caption[:200]},
                files={"voice": f}, timeout=30)
        return r.status_code == 200
    except:
        return False

# ── WhatsApp ────────────────────────────────────────────────────
def wa_send(to: str, text: str) -> bool:
    if not WA_API_KEY or not to:
        return False
    try:
        r = requests.post("https://graph.facebook.com/v18.0/me/messages",
            headers={"Authorization": f"Bearer {WA_API_KEY}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}},
            timeout=10)
        return r.status_code == 200
    except:
        return False

def wa_send_voice(to: str, audio_path: str) -> bool:
    if not WA_API_KEY or not WA_PHONE_ID or not os.path.exists(audio_path):
        return False
    try:
        r_up = requests.post(f"https://graph.facebook.com/v18.0/{WA_PHONE_ID}/media",
            headers={"Authorization": f"Bearer {WA_API_KEY}"},
            files={"file": open(audio_path, "rb")},
            data={"messaging_product": "whatsapp", "type": "audio/ogg"}, timeout=30)
        if r_up.status_code != 200:
            return False
        media_id = r_up.json().get("id")
        if not media_id:
            return False
        r_send = requests.post("https://graph.facebook.com/v18.0/me/messages",
            headers={"Authorization": f"Bearer {WA_API_KEY}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"id": media_id}},
            timeout=10)
        return r_send.status_code == 200
    except:
        return False

# ── Keyboard builders ───────────────────────────────────────────
LANG_KEYBOARD = {
    "inline_keyboard": [
        [{"text": "🇮🇳 हिंदी", "callback_data": "set_hi"}, {"text": "🇬🇧 English", "callback_data": "set_en"}],
        [{"text": "🇲🇷 मराठी", "callback_data": "set_mr"}, {"text": "🇬🇾 ગુજરાતી", "callback_data": "set_gu"}],
        [{"text": "🇮🇳 தமிழ்", "callback_data": "set_ta"}, {"text": "🇮🇳 తెలుగు", "callback_data": "set_te"}],
        [{"text": "🇮🇳 ಕನ್ನಡ", "callback_data": "set_kn"}, {"text": "🇮🇳 മലയാളം", "callback_data": "set_ml"}],
        [{"text": "🇧🇩 বাংলা", "callback_data": "set_bn"}, {"text": "🇮🇳 ਪੰਜਾਬੀ", "callback_data": "set_pa"}],
        [{"text": "🇮🇳 राजस्थानी", "callback_data": "set_raj"}, {"text": "⚙️ Reply Mode", "callback_data": "reply_mode_menu"}],
    ]
}

def reply_mode_keyboard(prefs: dict):
    voice_active = "🔔" if prefs["mode"] == "voice" else "  "
    text_active = "📝" if prefs["mode"] == "text" else "  "
    voice_line = f"{voice_active} 🔊 Voice Reply — bot voice note bhejega"
    text_line = f"{text_active} 📝 Text Reply — sirf text mein reply"
    lm = LANG_META.get(prefs["language"], LANG_META["hi"])
    return {
        "inline_keyboard": [
            [{"text": voice_line, "callback_data": "mode_voice"}, {"text": text_line, "callback_data": "mode_text"}],
            [{"text": f"🌐 {lm['flag']} {lm['name']}", "callback_data": "lang_settings"}, {"text": "✅ Done", "callback_data": "settings_done"}],
        ]
    }

def settings_keyboard(prefs: dict):
    lm = LANG_META.get(prefs["language"], LANG_META["hi"])
    mode_icon = "🔊" if prefs["mode"] == "voice" else "📝"
    return {
        "inline_keyboard": [
            [{"text": f"{mode_icon} Reply: {'Voice' if prefs['mode']=='voice' else 'Text'}", "callback_data": "reply_mode_menu"}],
            [{"text": "🌐 भाषा बदलें", "callback_data": "lang_settings"}, {"text": "✅ Done", "callback_data": "settings_done"}],
        ]
    }

# ── AI Response ──────────────────────────────────────────────────
async def ai_reply(text: str, lang: str) -> str:
    lang_name = LANG_META.get(lang, LANG_META["hi"])["name"]
    try:
        r = requests.post("http://localhost:5050/analyze",
            json={"texts": [text], "images": [],
                  "prompt": f"AI24x7 CCTV assistant. Respond in {lang_name}. Short 1-2 lines only. User: {text}"},
            timeout=15)
        if r.status_code == 200:
            return (r.json().get("response") or r.json().get("text", ""))[:300]
    except:
        pass
    return None

RESPONSES = {
    "hi": {"greet": "नमस्ते! AI24x7 आपकी सेवा में है।", "camera": "सभी कैमरे ऑनलाइन हैं।", "default": "आपका संदेश मिला।"},
    "en": {"greet": "Hello! AI24x7 at your service.", "camera": "All cameras online.", "default": "Message received."},
    "mr": {"greet": "नमस्कार! AI24x7 सहाय्यक आपली सेवा करत आहे।", "camera": "सर्व कॅमेरे ऑनलाइन आहेत।", "default": "संदेश मिळाला।"},
    "gu": {"greet": "નમસ્તે! AI24x7 તમારી સેવામાં.", "camera": "બધા કૅમેરા ઓનલાઇન છે।", "default": "સંદેશ મળ્યો।"},
    "ta": {"greet": "வணக்கம்! AI24x7 உதவியாளர் உங்கள் சேவையில்.", "camera": "எல்லா கேமராக்களும் ஆன்லைனில் உள்ளன।", "default": "செய்தி பெறப்பட்டது।"},
    "te": {"greet": "నమస్కారం! AI24x7 మీ సేవలో.", "camera": "అన్ని కెమరాలు ఆన్‌లైన్‌లో ఉన్నాయి।", "default": "సందేశం అందింది।"},
    "kn": {"greet": "ನಮಸ್ತೆ! AI24x7 ನಿಮ್ಮ ಸೇವೆಯಲ್ಲಿ.", "camera": "ಎಲ್ಲಾ ಕ್ಯಾಮರಾಗಳು ಆನ್‌ಲೈನ್‌ನಲ್ಲಿವೆ।", "default": "ಸಂದೇಶ ಪಡೆದೆ।"},
    "ml": {"greet": "നമസ്തെ! AI24x7 നിങ്ങളുടെ സേവയിൽ.", "camera": "എല്ലാ ക്യാമറകളും ഓൺലൈനിലാണ്।", "default": "സന്ദേശം ലഭിച്ചു।"},
    "bn": {"greet": "নমস্কার! AI24x7 আপনার সेवায়।", "camera": "সব ক্যামেরা অনলাইন আছে।", "default": "বার্তা পেয়েছি।"},
    "pa": {"greet": "ਨਮਸਤੇ! AI24x7 ਤੁਹਾਡੀ ਸੇਵਾ ਵਿੱਚ।", "camera": "ਸਾਰੇ ਕੈਮਰੇ ਆਨਲਾਈਨ ਹਨ।", "default": "ਤੁਹਾਡਾ ਮੈਸੇਜ ਮਿਲਿਆ।"},
    "raj": {"greet": "ਨਮਸਤੇ! AI24x7 ਤੁਹਾਡੀ ਸੇਵਾ ਵਿੱਚ।", "camera": "ਸਾਰੇ ਕੈਮਰੇ ਆਨਲਾਈਨ ਹਨ।", "default": "ਤੁਹਾਡਾ ਮੈਸੇਜ ਮਿਲਿਆ।"},
}

def fallback(text: str, lang: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["hello", "hi", "namaste", "vanakkam", "namaskar"]):
        return RESPONSES.get(lang, RESPONSES["hi"])["greet"]
    if any(w in text_lower for w in ["camera", "kamera", "cctv", "online"]):
        return RESPONSES.get(lang, RESPONSES["hi"])["camera"]
    return RESPONSES.get(lang, RESPONSES["hi"])["default"]

# ── Send reply (text + optional voice) ─────────────────────────
async def send_reply(chat_id: str, text: str, lang: str, reply_mode: str):
    """Send text reply. If reply_mode=voice, also send voice note."""
    tg_send(text, chat_id)
    if reply_mode == "voice":
        out = str(TEMP_AUDIO / f"r_{lang}.mp3")
        ok = await tts_generate(text, lang, out)
        if ok and os.path.exists(out):
            tg_send_voice(out, chat_id)
            try:
                os.remove(out)
            except:
                pass

# ── Routes ─────────────────────────────────────────────────────
routes = web.RouteTableDef()

@routes.post("/telegram-webhook")
async def tg_webhook(request: web.Request) -> web.Response:
    load_config()
    try:
        update = await request.json()
    except:
        return web.Response(status=400)

    try:
        callback = update.get("callback_query", {})
        msg = update.get("message", {})

        # ── Callback buttons ──
        if callback:
            data = callback.get("data", "")
            chat_id = str(callback["message"]["chat"]["id"])
            msg_id = callback["message"]["message_id"]
            query_id = callback["id"]
            platform = "telegram"

            if data.startswith("set_"):
                lang = data[4:]
                set_lang(platform, chat_id, lang)
                lm = LANG_META.get(lang, LANG_META["hi"])
                tg_answer_cb(query_id, f"✅ {lm['flag']} {lm['name']} set!")
                tg_reply_markup(chat_id,
                    f"✅ *Language Set!*\n{lm['flag']} {lm['native']} — ab isme reply aayega\n\n/settings likho reply mode change karne ke liye",
                    json.dumps(LANG_KEYBOARD))
                logger.info(f"Lang set: {platform}/{chat_id} → {lang}")

            elif data == "reply_mode_menu":
                prefs = get_prefs(platform, chat_id)
                tg_answer_cb(query_id)
                tg_reply_markup(chat_id,
                    "🔊 *Reply Mode Chuno — ek baar set karo, forever save!*\n\nBot kaise reply karega:",
                    json.dumps(reply_mode_keyboard(prefs)))

            elif data == "mode_voice":
                set_reply_mode(platform, chat_id, "voice")
                prefs = get_prefs(platform, chat_id)
                tg_answer_cb(query_id, "🔊 Voice mode ON! Ab bot voice note bhejega!")
                tg_edit_markup(chat_id, msg_id, json.dumps(reply_mode_keyboard(prefs)))

            elif data == "mode_text":
                set_reply_mode(platform, chat_id, "text")
                prefs = get_prefs(platform, chat_id)
                tg_answer_cb(query_id, "📝 Text mode ON!")
                tg_edit_markup(chat_id, msg_id, json.dumps(reply_mode_keyboard(prefs)))

            elif data == "lang_settings":
                prefs = get_prefs(platform, chat_id)
                tg_answer_cb(query_id)
                tg_reply_markup(chat_id,
                    "🌐 *Language Selection* — Apni bhasha chuno:",
                    json.dumps(LANG_KEYBOARD))

            elif data == "settings_done":
                prefs = get_prefs(platform, chat_id)
                lm = LANG_META.get(prefs["language"], LANG_META["hi"])
                mode_icon = "🔊" if prefs["mode"] == "voice" else "📝"
                tg_answer_cb(query_id, "✅ Done!")
                tg_send(f"✅ *Settings Saved!*\n\n{lm['flag']} {lm['name']}\n{mode_icon} {prefs['mode'].capitalize()} Mode\n\nAI24x7 ready to protect!")
                await send_reply(chat_id,
                    f"Settings saved. {lm['name']} language. {prefs['mode'].capitalize()} mode. AI24x7 is ready!",
                    prefs["language"], prefs["mode"])

            return web.Response(status=200)

        # ── Regular messages ──
        if msg:
            text = msg.get("text", "")
            chat_id = str(msg["chat"]["id"])

            if text in ("/start", "/help"):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, datetime('now'))",
                              ("alert_telegram_chat_id", chat_id))
                    conn.commit()
                    conn.close()
                except:
                    pass
                tg_reply_markup(chat_id,
                    "Welcome to *AI24x7 Voice Bot*! 🎉\n\nYe kya karega:\n🔊 Voice notes bhejega aapki bhasha mein\n📝 Ya sirf text reply — aapke choice pe\n\n*Shuru karne ke liye language select karo:*",
                    json.dumps(LANG_KEYBOARD))
                return web.Response(status=200)

            if text in ("/language", "/lang"):
                tg_reply_markup(chat_id, "🌐 *Language Selection* — Apni bhasha chuno:",
                    json.dumps(LANG_KEYBOARD))
                return web.Response(status=200)

            if text == "/settings":
                prefs = get_prefs("telegram", chat_id)
                lm = LANG_META.get(prefs["language"], LANG_META["hi"])
                tg_reply_markup(chat_id,
                    f"⚙️ *Settings*\n{lm['flag']} {lm['name']}\n\nReply mode aur language yahan se badlo:",
                    json.dumps(settings_keyboard(prefs)))
                return web.Response(status=200)

            # Normal message → AI reply
            prefs = get_prefs("telegram", chat_id)
            lang = prefs["language"]
            mode = prefs.get("mode", "voice")
            ai_resp = await ai_reply(text, lang)
            if not ai_resp:
                ai_resp = fallback(text, lang)
            await send_reply(chat_id, ai_resp, lang, mode)

    except Exception as e:
        logger.error(f"TG webhook error: {e}")

    return web.Response(status=200)

@routes.post("/whatsapp-webhook")
async def wa_webhook(request: web.Request) -> web.Response:
    load_config()
    try:
        data = await request.json()
    except:
        return web.Response(status=400)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                for msg in change.get("value", {}).get("messages", []):
                    msg_type = msg.get("type")
                    from_num = msg.get("from")
                    if not from_num:
                        continue
                    prefs = get_prefs("whatsapp", from_num)
                    lang = prefs["language"]
                    mode = prefs.get("mode", "voice")
                    if msg_type == "text":
                        text = msg.get("text", {}).get("body", "")
                        ai_resp = await ai_reply(text, lang) or fallback(text, lang)
                        wa_send(from_num, ai_resp)
                        if mode == "voice":
                            out = str(TEMP_AUDIO / f"wa_{lang}.mp3")
                            ok = await tts_generate(ai_resp, lang, out)
                            if ok and os.path.exists(out):
                                wa_send_voice(from_num, out)
                                try:
                                    os.remove(out)
                                except:
                                    pass
    except Exception as e:
        logger.error(f"WA webhook error: {e}")

    return web.Response(status=200)

@routes.get("/health")
async def health(request: web.Request) -> web.Response:
    return web.Response(text=json.dumps({"status": "ok", "service": "voice_bot_v2c"}))

@routes.get("/")
async def index(request: web.Request) -> web.Response:
    return web.Response(text="AI24x7 Voice Bot v2c")

async def main():
    init_db()
    load_config()
    logger.info("Voice Bot v2c starting...")
    logger.info(f"Reply modes: voice / text")
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5058)
    await site.start()
    logger.info("Voice Bot v2c HTTP on port 5058")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
