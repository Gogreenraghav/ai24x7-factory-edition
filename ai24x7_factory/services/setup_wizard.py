#!/usr/bin/env python3
"""
AI24x7 First-Run Setup Wizard
Appears when: factory_data.db has no license_key config
访问: http://43.242.224.231:5059
"""
import sys, os
sys.path.insert(0, '/opt/ai24x7-docker/factory/dashboard')

import streamlit as st
import sqlite3, requests, uuid, hashlib, datetime

st.set_page_config(page_title="AI24x7 Setup", page_icon="🏭", layout="centered")

DB_PATH = "/opt/ai24x7-docker/factory/dashboard/factory_data.db"

st.markdown("""
<style>
* { font-family: 'Segoe UI', system-ui, sans-serif !important; }
body { background: #07090f !important; color: #fff !important; }
.stApp { background: #07090f !important; }
h1 { text-align: center; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# ── Check if already configured ──
def is_configured():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key_name='factory_name'")
    row = c.fetchone()
    conn.close()
    return row is not None

def get_config(key, default=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key_name=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_config(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key_name, value, updated_at) VALUES (?, ?, datetime('now'))", (key, value))
    conn.commit()
    conn.close()

def get_machine_id():
    mac = ':'.join(f'{uuid.getnode():02x}'[i:i+2] for i in range(0,12,2))
    cpu = os.popen("cat /proc/cpuinfo | grep 'model name' | head -1").read()[:80].strip()
    hw = f"{mac}-{cpu}-{uuid.gethostname()}".encode('utf-8', errors='ignore')
    return hashlib.sha256(hw).hexdigest()[:32]

def register_license(key, machine_id):
    try:
        r = requests.post("http://localhost:5053/register",
            json={"license_key": key, "machine_id": machine_id, "client_name": get_config("factory_name", "AI24x7")},
            timeout=10)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

# ── Step tracking ──
step = st.session_state.get("wizard_step", 1)

st.markdown("""
<div style="text-align:center; padding: 20px 0;">
    <div style="font-size:3rem;">🏭</div>
    <h1 style="font-size:2rem; color:#00b4d8;">AI24x7 Factory Edition</h1>
    <p style="color:#4a5568; font-size:0.9rem;">Smart Layer CCTV Processing System</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

if is_configured() and get_config("alert_telegram_token", ""):
    st.success("System already configured!")
    st.markdown(f"""
    <div style="text-align:center; padding:30px;">
        <div style="font-size:2rem; color:#00e676;">✅ Setup Complete</div>
        <p style="color:#4a5568; margin-top:10px;">
            Factory: {get_config('factory_name', 'AI24x7')}<br/>
            License: {get_config('license_key', 'Not set')[:20]}...<br/>
            Scan Interval: {get_config('scan_interval_sec', '8')}s
        </p>
        <a href="http://43.242.224.231:5052">
            <div style="display:inline-block; background:linear-gradient(135deg,#00b4d8,#b388ff); color:#fff; padding:12px 30px; border-radius:10px; font-weight:800; margin-top:20px; cursor:pointer;">
                Open Dashboard →
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── STEP 1: Factory Info ──
if step == 1:
    st.subheader("Step 1: Factory Information")
    factory_name = st.text_input("Factory / Company Name", placeholder="e.g. Max Hotel, Raj Factory")
    factory_id = st.text_input("Factory ID (optional)", placeholder="e.g. FACT-001")
    if st.button("Next →"):
        if factory_name:
            set_config("factory_name", factory_name)
            if factory_id:
                set_config("factory_id", factory_id)
            st.session_state.wizard_step = 2
            st.rerun()
        else:
            st.error("Factory name required")

# ── STEP 2: License Key ──
elif step == 2:
    st.subheader("Step 2: License Activation")
    machine_id = get_machine_id()
    st.code(f"Machine ID: {machine_id}", language=None)
    st.caption("Ye machine ID license server pe register hoga. Isko share karein agar license purchase karna ho.")
    
    st.markdown("---")
    license_key = st.text_input("License Key", placeholder="AI24x7-XXXX-XXXX-XXXX-XXXX", help="Purchase se pehle demo mode mein continue kar sakte ho")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Activate License"):
            if license_key:
                result = register_license(license_key, machine_id)
                if result.get("success"):
                    set_config("license_key", license_key)
                    st.success(f"Activated! Plan: {result.get('plan','monthly')}, Expires: {result.get('expires','N/A')}")
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.error(result.get("message", "Activation failed"))
            else:
                st.warning("Enter license key")
    with col2:
        if st.button("Skip (Demo Mode) →"):
            set_config("license_key", "DEMO-MODE")
            st.info("Demo mode — license expires 31 Dec 2026")
            st.session_state.wizard_step = 3
            st.rerun()

    if st.button("← Back"):
        st.session_state.wizard_step = 1
        st.rerun()

# ── STEP 3: Alert Channels ──
elif step == 3:
    st.subheader("Step 3: Alert Channels (Optional)")
    st.caption("Ye optional hain — baad mein bhi configure kar sakte ho Settings tab se")
    
    tg = st.checkbox("📱 Telegram Alerts", value=False)
    if tg:
        st.text_input("Bot Token (from @BotFather)", key="tg_token", type="password")
        st.text_input("Chat ID", key="tg_chat")
        st.caption("Telegram pe @userinfobot ya @getidsbot se apna Chat ID pta kar sakte ho")
    
    sms = st.checkbox("📞 SMS / Call Alerts", value=False)
    if sms:
        provider = st.selectbox("Provider", ["exotel", "twilio", "msg91"])
        st.text_input("API Key / SID", key="sms_key", type="password")
        st.text_input("Phone Number (with country code)", value="+91", key="sms_num")
        st.selectbox("Alert Type", ["sms", "call"], key="sms_type")
    
    wa = st.checkbox("💬 WhatsApp Alerts", value=False)
    if wa:
        st.text_input("Meta WhatsApp API Key", key="wa_key", type="password")
        st.text_input("WhatsApp Number (with country code)", key="wa_num")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Alert Settings"):
            if tg:
                set_config("alert_telegram_enabled", "true")
                set_config("alert_telegram_token", st.session_state.get("tg_token",""))
                set_config("alert_telegram_chat_id", st.session_state.get("tg_chat",""))
            else:
                set_config("alert_telegram_enabled", "false")
            if sms:
                set_config("alert_sms_enabled", "true")
                set_config("alert_sms_provider", provider)
                set_config("alert_sms_api_key", st.session_state.get("sms_key",""))
                set_config("alert_sms_number", st.session_state.get("sms_num","+91"))
                set_config("alert_sms_type", st.session_state.get("sms_type","sms"))
            else:
                set_config("alert_sms_enabled", "false")
            if wa:
                set_config("alert_whatsapp_enabled", "true")
                set_config("alert_whatsapp_api_key", st.session_state.get("wa_key",""))
                set_config("alert_whatsapp_phone", st.session_state.get("wa_num",""))
            else:
                set_config("alert_whatsapp_enabled", "false")
            st.success("Alert settings saved!")
            st.session_state.wizard_step = 4
            st.rerun()
    with col2:
        if st.button("Skip →"):
            st.session_state.wizard_step = 4
            st.rerun()
    if st.button("← Back"):
        st.session_state.wizard_step = 2
        st.rerun()

# ── STEP 4: Scan Settings ──
elif step == 4:
    st.subheader("Step 4: AI Processing Settings")
    scan_int = st.slider("Layer 1 Scan Interval", 3, 30, 8, step=1,
        help="Har kitni seconds mein sab cameras scan honi hain")
    trigger = st.selectbox("Deep Analysis Trigger",
        [5, 6, 7, 8, 9], index=1,
        help="Priority kitna hone par deep analysis (Qwen3-VL) call ho")
    
    set_config("scan_interval_sec", str(scan_int))
    set_config("deep_trigger_priority", str(trigger))
    
    st.markdown(f"""
    <div style="background:rgba(0,180,216,0.08); border:1px solid rgba(0,180,216,0.2); border-radius:12px; padding:16px; margin:12px 0;">
        <div style="font-size:0.8rem; font-weight:800; color:#00b4d8; margin-bottom:8px;">Current Settings:</div>
        <div style="display:flex; gap:20px; flex-wrap:wrap;">
            <span style="color:#8b9dc3;">Scan every <b style="color:#00b4d8;">{scan_int} seconds</b></span>
            <span style="color:#8b9dc3;">Trigger at <b style="color:#b388ff;">Priority {trigger}/10</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Next →"):
        st.session_state.wizard_step = 5
        st.rerun()
    if st.button("← Back"):
        st.session_state.wizard_step = 3
        st.rerun()

# ── STEP 5: Done ──
elif step == 5:
    ip = "43.242.224.231"
    st.markdown(f"""
    <div style="text-align:center; padding:40px 20px;">
        <div style="font-size:4rem; margin-bottom:16px;">🎉</div>
        <h2 style="color:#00e676; margin-bottom:8px;">Setup Complete!</h2>
        <p style="color:#4a5568; margin-bottom:30px;">
            AI24x7 Factory Edition successfully configured.<br/>
            All services are running and monitoring your cameras.
        </p>
        <div style="background:rgba(0,180,216,0.08); border:1px solid rgba(0,180,216,0.2); border-radius:16px; padding:24px; max-width:500px; margin:0 auto;">
            <div style="font-size:0.8rem; font-weight:800; color:#4a5568; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.1em;">Dashboard Access</div>
            <div style="font-size:1.8rem; font-weight:900; color:#00b4d8; margin-bottom:8px;">http://{ip}:5052</div>
            <div style="font-size:0.75rem; color:#4a5568; margin-bottom:16px;">Factory: {get_config('factory_name', 'AI24x7')}</div>
            <a href="http://{ip}:5052">
                <div style="background:linear-gradient(135deg,#00b4d8,#00e676); color:#fff; padding:14px 30px; border-radius:12px; font-weight:800; display:inline-block;">
                    Open Dashboard →
                </div>
            </a>
        </div>
        <div style="margin-top:24px; font-size:0.75rem; color:#4a5568;">
            Settings tab mein koi bhi change kar sakte ho anytime.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🔄 Go to Dashboard"):
        st.success("Navigate to http://43.242.224.231:5052")

st.markdown(f"""
<div style="text-align:center; color:#4a5568; font-size:0.65rem; padding:16px 0;">
    AI24x7 Factory Edition v7.0 · © 2026 GOUP CONSULTANCY SERVICES LLP
</div>
""", unsafe_allow_html=True)