#!/usr/bin/env python3
"""
AI24x7 Alert Dispatcher - Background Daemon
Monitors alerts table -> sends via Telegram + SMS + WhatsApp
"""
import sys, time, sqlite3, json, os, datetime, requests

DB_PATH = "/opt/ai24x7-docker/factory/dashboard/factory_data.db"
CHECK_INTERVAL = 5
LOG_FILE = "/var/log/ai24x7/alert_dispatcher.log"

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

def get_config(key, default=""):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value FROM config WHERE key_name=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except:
        return default

def is_channel_enabled(channel):
    return get_config(f"alert_{channel}_enabled", "false") == "true"

def get_camera_name(camera_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM cameras WHERE id=?", (camera_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else f"Camera {camera_id}"
    except:
        return f"Camera {camera_id}"

def format_alert_message(alert):
    """Format alert into a readable message"""
    cam_name = get_camera_name(alert.get("camera_id", 0))
    event = alert.get("event_type", "alert").replace("_", " ").title()
    msg = alert.get("message", "")
    conf = alert.get("confidence", 0)
    sev = alert.get("severity", "info")
    return cam_name, event, msg, conf, sev

def send_telegram(alert):
    token = get_config("alert_telegram_token", "")
    chat_id = get_config("alert_telegram_chat_id", "")
    if not token or not chat_id:
        return False, "Token or Chat ID missing"
    
    cam_name, event, msg, conf, sev = format_alert_message(alert)
    icon = {"critical": "🔥", "warning": "⚠️", "info": "📹", "success": "✅"}.get(sev, "📢")
    
    text = f"{icon} <b>AI24x7 Alert</b>\n"
    text += f"<b>Camera:</b> {cam_name}\n"
    text += f"<b>Event:</b> {event}\n"
    text += f"<b>Message:</b> {msg}\n"
    text += f"<b>Severity:</b> {sev.upper()}\n"
    text += f"<b>Confidence:</b> {int(conf*100)}%\n"
    text += f"<b>Time:</b> {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
        if r.status_code == 200:
            return True, "Sent"
        else:
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

def send_sms(alert):
    provider = get_config("alert_sms_provider", "exotel")
    api_key = get_config("alert_sms_api_key", "")
    number = get_config("alert_sms_number", "")
    
    if not api_key or not number:
        return False, "API key or number missing"
    
    cam_name, event, msg, conf, sev = format_alert_message(alert)
    sms_msg = f"AI24x7: {cam_name} - {event} ({int(conf*100)}%) - {sev.upper()}"
    if len(sms_msg) > 160:
        sms_msg = sms_msg[:157] + "..."
    
    try:
        if provider == "exotel":
            url = f"https://api.exotel.com/v1/Accounts/{api_key}/Sms"
            r = requests.post(url, json={"From": "AI24x7", "To": number, "Body": sms_msg}, timeout=10)
        elif provider == "twilio":
            url = f"https://api.twilio.com/2010-04-01/Accounts/{api_key}/Messages.json"
            r = requests.post(url, data={"Body": sms_msg, "To": number, "From": "+1234567890"}, timeout=10)
        elif provider == "msg91":
            url = "https://api.msg91.com/api/v5/flow/"
            r = requests.post(url, json={"mobiles": number.replace("+91",""), "message": sms_msg}, headers={"authkey": api_key}, timeout=10)
        else:
            return False, f"Provider {provider} not implemented"
        
        if r.status_code in (200, 201):
            return True, "Sent"
        return False, f"HTTP {r.status_code}: {r.text[:80]}"
    except Exception as e:
        return False, str(e)

def send_whatsapp(alert):
    api_key = get_config("alert_whatsapp_api_key", "")
    phone = get_config("alert_whatsapp_phone", "")
    
    if not api_key or not phone:
        return False, "API key or phone missing"
    
    cam_name, event, msg, conf, sev = format_alert_message(alert)
    text = f"*AI24x7 Alert*\n\n📹 Camera: {cam_name}\n⚠️ Event: {event}\n📝 {msg}\n🔴 Severity: {sev.upper()} ({int(conf*100)}% confidence)"
    
    try:
        url = "https://graph.facebook.com/v18.0/me/messages"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"messaging_product": "whatsapp", "to": phone, "type": "text", "text": {"body": text}}
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        if r.status_code == 200:
            return True, "Sent"
        return False, f"HTTP {r.status_code}: {r.text[:80]}"
    except Exception as e:
        return False, str(e)

def process_alert(alert):
    results = {}
    if is_channel_enabled("telegram"):
        ok, msg = send_telegram(alert)
        results["telegram"] = {"ok": ok, "msg": msg}
        log(f"Telegram: {'OK' if ok else 'FAIL'} - {msg}")
    if is_channel_enabled("sms"):
        ok, msg = send_sms(alert)
        results["sms"] = {"ok": ok, "msg": msg}
        log(f"SMS: {'OK' if ok else 'FAIL'} - {msg}")
    if is_channel_enabled("whatsapp"):
        ok, msg = send_whatsapp(alert)
        results["whatsapp"] = {"ok": ok, "msg": msg}
        log(f"WhatsApp: {'OK' if ok else 'FAIL'} - {msg}")
    return results

def main():
    log("Alert Dispatcher started")
    log(f"Checking every {CHECK_INTERVAL}s")
    
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
                ORDER BY
                    CASE severity WHEN 'critical' THEN 1 ELSE 2 END,
                    created_at DESC
                LIMIT 10
            """)
            rows = c.fetchall()
            conn.close()
            
            for row in rows:
                alert_id = row["id"]
                if alert_id in dispatched:
                    continue
                
                results = process_alert(dict(row))
                
                if any(r.get("ok") for r in results.values()):
                    dispatched.add(alert_id)
                    if len(dispatched) > 100:
                        dispatched = set(list(dispatched)[-50:])
                    log(f"Alert #{alert_id} dispatched: {list(results.keys())}")
            
        except Exception as e:
            log(f"Error: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()