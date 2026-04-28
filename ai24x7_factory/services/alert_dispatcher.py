#!/usr/bin/env python3
"""AI24x7 Alert Dispatcher v4 - TEXT + VOICE alerts via Telegram + WhatsApp"""
import sys, time, sqlite3, datetime, requests, os, subprocess

DB_PATH = "/opt/ai24x7-docker/factory/dashboard/factory_data.db"
CHECK_INTERVAL = 5
LOG_FILE = "/var/log/ai24x7/alert_dispatcher.log"
TEMP_DIR = "/tmp/ai24x7_audio"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n"); f.flush()
    except:
        pass

def get_config(key, default=""):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except:
        return default

def is_enabled(channel):
    return get_config("alert_%s_enabled" % channel, "false") == "true"

def get_camera_name(cam_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM cameras WHERE id=?", (cam_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else "Camera %d" % cam_id
    except:
        return "Camera %d" % cam_id

def format_alert(alert):
    cam = get_camera_name(alert["camera_id"])
    event = alert.get("event_type", "alert").replace("_", " ").title()
    msg = alert.get("message", "")
    conf = int(alert.get("confidence", 0) * 100)
    sev = alert.get("severity", "info").upper()
    return cam, event, msg, conf, sev

def generate_voice(text, output_path):
    """Generate voice MP3 from text using gTTS, convert to OGG"""
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        mp3_path = output_path.replace(".ogg", ".mp3")
        
        # Generate MP3 using Google TTS
        from gtts import gTTS
        tts = gTTS(text=text, lang="hi", tld="co.in", slow=False)
        tts.save(mp3_path)
        
        # Convert MP3 to OGG (Telegram/WhatsApp compatible)
        cmd = [
            "ffmpeg", "-y", "-i", mp3_path,
            "-vn", "-acodec", "libopus", "-b:a", "128k",
            "-ar", "48000", "-ac", "1",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            log("FFmpeg error: %s" % result.stderr.decode()[:80])
            # Fallback: just use MP3
            if os.path.exists(mp3_path):
                import shutil
                shutil.copy(mp3_path, output_path.replace(".ogg", ".mp3"))
                return output_path.replace(".ogg", ".mp3")
            return None
        
        # Cleanup MP3
        try:
            os.remove(mp3_path)
        except:
            pass
        
        return output_path
    except Exception as e:
        log("TTS error: %s" % e)
        return None

# ─── TELEGRAM ───────────────────────────────────────────────
def send_telegram_text(alert):
    token = get_config("alert_telegram_token", "")
    chat_id = get_config("alert_telegram_chat_id", "")
    if not token or not chat_id:
        return False, "Token missing"
    cam, event, msg, conf, sev = format_alert(alert)
    icon = {"critical": "[CRITICAL]", "warning": "[WARNING]", "info": "[INFO]"}.get(alert.get("severity", "i"), "[I]")
    text = "%s AI24x7 Alert\nCamera: %s\nEvent: %s\nMessage: %s\nSeverity: %s (%d%%)\nTime: %s" % (
        icon, cam, event, msg, sev, conf, datetime.datetime.now().strftime("%H:%M:%S"))
    try:
        url = "https://api.telegram.org/bot%s/sendMessage" % token
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        ok = r.status_code == 200
        return ok, "Sent" if ok else "HTTP %d" % r.status_code
    except Exception as e:
        return False, str(e)

def send_telegram_voice(alert):
    token = get_config("alert_telegram_token", "")
    chat_id = get_config("alert_telegram_chat_id", "")
    if not token or not chat_id:
        return False, "Token missing"
    
    cam, event, msg, conf, sev = format_alert(alert)
    # Build voice text
    voice_text = "Alert. %s. Camera %s. %s. Severity %s. Confidence %d percent. %s" % (
        sev, cam, event, sev, conf, "Please take immediate action." if sev == "CRITICAL" else "")
    
    ogg_path = "%s/alert_%d.ogg" % (TEMP_DIR, alert["id"])
    audio_file = generate_voice(voice_text, ogg_path)
    
    if not audio_file or not os.path.exists(audio_file):
        return False, "Voice generation failed"
    
    try:
        url = "https://api.telegram.org/bot%s/sendVoice" % token
        with open(audio_file, "rb") as f:
            files = {"voice": f}
            data = {"chat_id": chat_id, "caption": "AI24x7 Voice Alert"}
            r = requests.post(url, data=data, files=files, timeout=30)
        ok = r.status_code == 200
        try:
            os.remove(audio_file)
        except:
            pass
        return ok, "Voice sent" if ok else "HTTP %d" % r.status_code
    except Exception as e:
        return False, str(e)

# ─── WHATSAPP ───────────────────────────────────────────────
def send_whatsapp_text(alert):
    api_key = get_config("alert_whatsapp_api_key", "")
    phone = get_config("alert_whatsapp_phone", "")
    if not api_key or not phone:
        return False, "WhatsApp not configured"
    cam, event, msg, conf, sev = format_alert(alert)
    text = "AI24x7 Alert\n\nCamera: %s\nEvent: %s\nMessage: %s\nSeverity: %s (%d%%)" % (
        cam, event, msg, sev, conf)
    try:
        url = "https://graph.facebook.com/v18.0/me/messages"
        headers = {"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": text}}
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        ok = r.status_code == 200
        return ok, "Sent" if ok else "Error: %s" % r.text[:60]
    except Exception as e:
        return False, str(e)

def send_whatsapp_voice(alert):
    """Send WhatsApp audio message using Meta Graph API"""
    api_key = get_config("alert_whatsapp_api_key", "")
    phone = get_config("alert_whatsapp_phone", "")
    if not api_key or not phone:
        return False, "WhatsApp not configured"
    
    cam, event, msg, conf, sev = format_alert(alert)
    voice_text = "Alert. %s. Camera %s. %s. Severity %s. Confidence %d percent." % (
        sev, cam, event, sev, conf)
    
    ogg_path = "%s/wa_alert_%d.ogg" % (TEMP_DIR, alert["id"])
    audio_file = generate_voice(voice_text, ogg_path)
    
    if not audio_file or not os.path.exists(audio_file):
        return False, "Voice generation failed"
    
    try:
        # WhatsApp Audio: upload first, then send
        # Step 1: Get phone ID
        phone_id = get_config("alert_whatsapp_phone_id", "")
        if not phone_id:
            return False, "WhatsApp Phone ID not set"
        
        # Step 2: Upload audio to WhatsApp
        url_upload = "https://graph.facebook.com/v18.0/%s/media" % phone_id
        headers_upload = {"Authorization": "Bearer %s" % api_key}
        with open(audio_file, "rb") as f:
            files = {"file": f}
            data = {"messaging_product": "whatsapp", "type": "audio/ogg"}
            r_upload = requests.post(url_upload, headers=headers_upload, data=data, files=files, timeout=30)
        
        if r_upload.status_code != 200:
            return False, "Upload failed: %s" % r_upload.text[:60]
        
        media_id = r_upload.json().get("id")
        if not media_id:
            return False, "No media ID returned"
        
        # Step 3: Send audio message
        url_send = "https://graph.facebook.com/v18.0/me/messages"
        headers_send = {"Authorization": "Bearer %s" % api_key, "Content-Type": "application/json"}
        payload_send = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "audio",
            "audio": {"id": media_id}
        }
        r_send = requests.post(url_send, headers=headers_send, json=payload_send, timeout=10)
        ok = r_send.status_code == 200
        
        try:
            os.remove(audio_file)
        except:
            pass
        
        return ok, "Audio sent" if ok else "Send error: %s" % r_send.text[:60]
    except Exception as e:
        return False, str(e)

# ─── SMS ────────────────────────────────────────────────────
def send_sms(alert):
    provider = get_config("alert_sms_provider", "exotel")
    api_key = get_config("alert_sms_api_key", "")
    number = get_config("alert_sms_number", "")
    if not api_key or not number:
        return False, "SMS not configured"
    cam, event, msg, conf, sev = format_alert(alert)
    sms_text = "AI24x7: %s - %s (%d%%)" % (cam, event, conf)
    if len(sms_text) > 160:
        sms_text = sms_text[:157] + "..."
    try:
        if provider == "exotel":
            url = "https://api.exotel.com/v1/Accounts/%s/Sms" % api_key
            r = requests.post(url, json={"From": "AI24x7", "To": number, "Body": sms_text}, timeout=10)
            ok = r.status_code in (200, 201)
            return ok, "Sent" if ok else "Error: %s" % r.text[:60]
        elif provider == "msg91":
            url = "https://api.msg91.com/api/v5/flow/"
            headers = {"authkey": api_key, "content-type": "application/json"}
            payload = {"mobiles": number.replace("+91",""), "message": sms_text}
            r = requests.post(url, headers=headers, json=payload, timeout=10)
            ok = r.status_code == 200
            return ok, "Sent" if ok else "Error: %s" % r.text[:60]
        return False, "Provider %s not supported" % provider
    except Exception as e:
        return False, str(e)

# ─── VOICE CALL ─────────────────────────────────────────────
def send_voice_call(alert):
    """Make voice call for CRITICAL alerts via Twilio or Exotel"""
    provider = get_config("alert_sms_provider", "exotel")
    number = get_config("alert_sms_number", "")
    if not number:
        return False, "Number not set"
    
    cam, event, msg, conf, sev = format_alert(alert)
    tts_msg = "Alert from AI24x7. Camera %s. %s. %s. Severity %s. Please take immediate action." % (
        cam, event, msg, sev)
    
    try:
        if provider == "twilio":
            twilio_sid = get_config("alert_twilio_sid", "")
            twilio_token = get_config("alert_twilio_token", "")
            twilio_from = get_config("alert_twilio_from", "")
            if not twilio_sid or not twilio_token:
                return False, "Twilio not configured"
            twiml_url = "http://twimlets.com/echo?twiml=<Response><Say voice=\"alice\" language=\"en-IN\">%s</Say></Response>" % tts_msg.replace(" ", "+")
            url = "https://api.twilio.com/2010-04-01/Accounts/%s/Calls.json" % twilio_sid
            data = {"To": number, "From": twilio_from, "Url": twiml_url}
            r = requests.post(url, data=data, auth=(twilio_sid, twilio_token), timeout=10)
            ok = r.status_code in (200, 201)
            return ok, "Call initiated" if ok else "Call error"
        elif provider == "exotel":
            exotel_sid = get_config("alert_exotel_sid", "")
            if not exotel_sid:
                return False, "Exotel SID not set"
            url = "https://api.exotel.com/v1/Accounts/%s/Calls/connect" % exotel_sid
            payload = {"From": number, "To": number, "FirstSpeech": tts_msg, "LoopCount": 2}
            r = requests.post(url, json=payload, timeout=15)
            ok = r.status_code in (200, 201, 202)
            return ok, "Call initiated" if ok else "Call error"
        return False, "Provider %s not supported" % provider
    except Exception as e:
        return False, str(e)

# ─── DISPATCH ────────────────────────────────────────────────
def dispatch(alert):
    results = {}
    sev = alert.get("severity", "info")
    log("Processing alert #%d [%s]" % (alert["id"], sev))
    
    if is_enabled("telegram"):
        ok, msg = send_telegram_text(alert)
        results["telegram"] = ok
        log("Telegram text: %s - %s" % ("OK" if ok else "FAIL", msg))
        
        # Voice on critical
        if sev == "critical":
            ok2, msg2 = send_telegram_voice(alert)
            results["telegram_voice"] = ok2
            log("Telegram voice: %s - %s" % ("OK" if ok2 else "FAIL", msg2))
    
    if is_enabled("sms"):
        ok, msg = send_sms(alert)
        results["sms"] = ok
        log("SMS: %s - %s" % ("OK" if ok else "FAIL", msg))
        
        if sev == "critical":
            ok2, msg2 = send_voice_call(alert)
            results["call"] = ok2
            log("CALL: %s - %s" % ("OK" if ok2 else "FAIL", msg2))
    
    if is_enabled("whatsapp"):
        ok, msg = send_whatsapp_text(alert)
        results["whatsapp"] = ok
        log("WhatsApp text: %s - %s" % ("OK" if ok else "FAIL", msg))
        
        # Voice on critical
        if sev == "critical":
            ok2, msg2 = send_whatsapp_voice(alert)
            results["whatsapp_voice"] = ok2
            log("WhatsApp voice: %s - %s" % ("OK" if ok2 else "FAIL", msg2))
    
    return results

def main():
    log("Alert Dispatcher v4 started - TEXT + VOICE via Telegram/WhatsApp/SMS/Call")
    dispatched = set()
    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=3)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("""
                SELECT id, camera_id, event_type, confidence, message, severity, created_at
                FROM alerts
                WHERE severity IN ('critical', 'warning')
                AND acknowledged = 0
                ORDER BY CASE severity WHEN 'critical' THEN 1 ELSE 2 END, id DESC
                LIMIT 10
            """)
            rows = c.fetchall()
            conn.close()
            for row in rows:
                aid = row["id"]
                if aid in dispatched:
                    continue
                results = dispatch(dict(row))
                if any(results.values()):
                    dispatched.add(aid)
                    if len(dispatched) > 100:
                        dispatched = set(list(dispatched)[-50:])
                    log("Alert #%d dispatched: %s" % (aid, list(results.keys())))
        except Exception as e:
            log("Error: %s" % e)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
