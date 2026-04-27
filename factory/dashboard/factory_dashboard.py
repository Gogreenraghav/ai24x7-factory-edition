#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Dashboard v6.0
Day/Night Theme + SQLite Database + Bold Design
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import time
from datetime import datetime

# Database imports
from factory_db import (
    init_db, seed_demo_data, get_dashboard_stats, get_all_cameras,
    get_recent_alerts, get_equipment, get_ppe_violations,
    get_shift_reports, get_daily_stats, acknowledge_alert, get_config, set_config
)

# Init DB
init_db()
seed_demo_data()

st.set_page_config(page_title="AI24x7 Factory", page_icon="🏭", layout="wide", initial_sidebar_state="collapsed")

# ─── Theme Management ─────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = st.session_state.theme
is_dark = theme == "dark"

# ─── CSS THEME ───────────────────────────────────────────────────────────────
def css(dark):
    if dark:
        bg = "#080b12"; sb = "#0d1117"; cr = "#e5e7eb"; cr2 = "#9ca3af"; cr3 = "#6b7280"
        bc = "#1f2937"; crd = "#111827"; b2 = "#1a1d2e"
        g = "#10b981"; bl = "#3b82f6"; o = "#f59e0b"; r = "#ef4444"
        link = "rgba(255,255,255,0.6)"
    else:
        bg = "#f8fafc"; sb = "#f1f5f9"; cr = "#0f172a"; cr2 = "#475569"; cr3 = "#94a3b8"
        bc = "#e2e8f0"; crd = "#ffffff"; b2 = "#e2e8f0"
        g = "#10b981"; bl = "#3b82f6"; o = "#f59e0b"; r = "#ef4444"
        link = "rgba(15,23,42,0.6)"

    return f"""
<style>
* {{ font-weight: 700 !important; font-family: 'Segoe UI', system-ui, sans-serif; }}
.stApp {{ background: {bg}; color: {cr}; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, {bl}, {g}); border-radius: 3px; }}
[data-testid="stSidebar"] {{ background: {sb} !important; border-right: 2px solid {bc} !important; width: 240px !important; }}
.slbl {{ font-size: 0.58rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.15em; color: {cr3}; margin: 12px 0 5px; }}
.sval {{ font-size: 0.78rem !important; font-weight: 800 !important; color: {cr}; }}
.svall {{ font-size: 0.65rem !important; font-weight: 700 !important; color: {cr3}; }}
.mc {{ background: {crd}; border-radius: 16px; padding: 18px 20px; border: 2px solid {bc}; transition: all 0.25s; position: relative; overflow: hidden; }}
.mc:hover {{ border-color: {bl}; transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
.mc::before {{ content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0; }}
.mc.g::before {{ background: linear-gradient(90deg, {g}, #34d399); }}
.mc.b::before {{ background: linear-gradient(90deg, {bl}, #60a5fa); }}
.mc.o::before {{ background: linear-gradient(90deg, {o}, #fbbf24); }}
.mc.r::before {{ background: linear-gradient(90deg, {r}, #f87171); }}
.mn {{ font-size: 2.1rem !important; font-weight: 900 !important; line-height: 1 !important; margin-bottom: 4px; }}
.ml {{ font-size: 0.62rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.12em; color: {cr3}; }}
.md {{ font-size: 0.68rem !important; font-weight: 700 !important; margin-top: 5px; }}
.cc {{ background: {crd}; border: 2px solid {bc}; border-radius: 14px; overflow: hidden; transition: all 0.2s; }}
.cc:hover {{ border-color: {bl}; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(59,130,246,0.1); }}
.ct {{ background: linear-gradient(135deg, {b2}, {crd}); height: 108px; display: flex; align-items: center; justify-content: center; font-size: 2.6rem; position: relative; }}
.co {{ position: absolute; bottom: 0; left: 0; right: 0; padding: 5px 10px; background: linear-gradient(transparent, rgba(0,0,0,0.8)); display: flex; justify-content: space-between; align-items: center; }}
.cid {{ font-size: 0.58rem !important; font-weight: 800 !important; color: rgba(255,255,255,0.4) !important; }}
.cb {{ padding: 2px 8px; border-radius: 5px; font-size: 0.58rem !important; font-weight: 800 !important; text-transform: uppercase; }}
.cb.ok {{ background: rgba(16,185,129,0.18); color: {g} !important; border: 1px solid rgba(16,185,129,0.3); }}
.cb.wn {{ background: rgba(245,158,11,0.18); color: {o} !important; border: 1px solid rgba(245,158,11,0.3); }}
.cb.of {{ background: rgba(148,163,184,0.15); color: {cr3} !important; border: 1px solid rgba(148,163,184,0.25); }}
.cbdy {{ padding: 11px 13px; }}
.cn {{ font-size: 0.85rem !important; font-weight: 800 !important; margin-bottom: 7px; color: {cr}; }}
.cm {{ display: flex; justify-content: space-between; align-items: center; }}
.cm span {{ font-size: 0.68rem !important; font-weight: 700 !important; color: {cr3}; }}
.ac {{ background: {crd}; border-radius: 12px; padding: 12px 15px; margin-bottom: 7px; display: flex; align-items: flex-start; gap: 10px; border: 2px solid; transition: all 0.2s; }}
.ac:hover {{ transform: translateX(2px); }}
.ac.cri {{ border-color: rgba(239,68,68,0.4); border-left: 4px solid {r}; }}
.ac.war {{ border-color: rgba(245,158,11,0.4); border-left: 4px solid {o}; }}
.ac.inf {{ border-color: rgba(59,130,246,0.4); border-left: 4px solid {bl}; }}
.ac.suc {{ border-color: rgba(16,185,129,0.4); border-left: 4px solid {g}; }}
.ai {{ font-size: 1.1rem; flex-shrink: 0; margin-top: 1px; }}
.at {{ font-size: 0.85rem !important; font-weight: 800 !important; color: {cr}; margin-bottom: 2px; }}
.am {{ font-size: 0.75rem !important; font-weight: 700 !important; color: {cr3}; }}
.ati {{ font-size: 0.65rem !important; font-weight: 800 !important; color: {cr3}; margin-top: 2px; }}
.pr {{ margin-bottom: 10px; }}
.pl {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
.pll {{ font-size: 0.8rem !important; font-weight: 700 !important; color: {cr2}; }}
.plr {{ font-size: 0.8rem !important; font-weight: 900 !important; }}
.pt {{ height: 7px; background: {bc}; border-radius: 4px; overflow: hidden; }}
.pf {{ height: 100%; border-radius: 4px; }}
.ic {{ background: {crd}; border: 2px solid {bc}; border-radius: 14px; padding: 15px 17px; }}
.sh {{ display: flex; align-items: center; gap: 8px; margin: 16px 0 12px; }}
.si {{ font-size: 0.95rem; }}
.st {{ font-size: 0.62rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.15em; color: {cr3}; flex: 1; }}
.sl {{ height: 1px; flex: 3; background: linear-gradient(90deg, {bc}, transparent); }}
.er {{ display: flex; align-items: center; gap: 14px; padding: 9px 0; border-bottom: 1px solid {b2}; }}
.er:last-child {{ border-bottom: none; }}
.en {{ font-size: 0.82rem !important; font-weight: 800 !important; min-width: 135px; color: {cr}; }}
.es {{ font-size: 0.68rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.05em; min-width: 85px; }}
.eb {{ flex: 1; }}
.eu {{ font-size: 0.78rem !important; font-weight: 900 !important; min-width: 50px; text-align: right; }}
.sb {{ background: linear-gradient(135deg, #064e3b, #059669, {g}); border: 2px solid #059669; border-radius: 18px; padding: 24px; text-align: center; }}
.sn {{ font-size: 3rem !important; font-weight: 900 !important; color: #fff; line-height: 1 !important; text-shadow: 0 0 25px rgba(16,185,129,0.5); }}
.sl {{ font-size: 0.68rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(255,255,255,0.7); margin-top: 5px; }}
.stTable {{ background: {crd} !important; border-radius: 12px !important; border: 2px solid {bc} !important; overflow: hidden !important; }}
[data-testid="stTable"] th {{ background: {sb} !important; font-size: 0.6rem !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.12em !important; color: {cr3} !important; padding: 11px 15px !important; border-bottom: 2px solid {bc} !important; }}
[data-testid="stTable"] td {{ font-size: 0.8rem !important; font-weight: 700 !important; color: {cr2} !important; padding: 10px 15px !important; border-bottom: 1px solid {b2} !important; }}
[data-testid="stTable"] tr:last-child td {{ border-bottom: none !important; }}
[data-testid="stTable"] tr:hover td {{ background: {b2} !important; }}
.stButton > button {{ border-radius: 10px !important; font-weight: 800 !important; font-size: 0.78rem !important; transition: all 0.15s !important; border: 2px solid !important; }}
.stButton > button:hover {{ transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; }}
.streamlit-expanderHeader {{ background: {crd} !important; border: 2px solid {bc} !important; border-radius: 10px !important; font-size: 0.82rem !important; font-weight: 800 !important; }}
.streamlit-expanderContent {{ background: {bg} !important; border: 2px solid {bc} !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }}
hr {{ border: none !important; border-top: 2px solid {bc} !important; margin: 1rem 0 !important; }}
[data-testid="stHorizontalBlock"] > div {{ gap: 10px !important; }}
.lp {{ background: linear-gradient(135deg, {g}, #059669); color: white; padding: 4px 13px; border-radius: 20px; font-size: 0.65rem !important; font-weight: 900 !important; letter-spacing: 0.12em; text-transform: uppercase; box-shadow: 0 0 18px rgba(16,185,129,0.4); animation: lg 2s ease-in-out infinite alternate; }}
@keyframes lg {{ from{{box-shadow:0 0 8px rgba(16,185,129,0.3)}} to{{box-shadow:0 0 22px rgba(16,185,129,0.6)}} }}
.ft {{ text-align: center; font-size: 0.62rem !important; font-weight: 600 !important; color: {cr3}; padding: 14px 0; }}
.tg {{ color: {g} !important; }}
.tb {{ color: {bl} !important; }}
.to {{ color: {o} !important; }}
.tr {{ color: {r} !important; }}
.tp {{ color: #a78bfa !important; }}
@media (max-width: 768px) {{
    [data-testid="stHorizontalBlock"] > div {{ min-width: calc(50% - 8px) !important; flex: 1 1 calc(50% - 8px) !important; }}
    .mc {{ min-width: calc(50% - 8px) !important; }}
    .cc {{ min-width: calc(50% - 8px) !important; }}
    .ct {{ height: 88px !important; }}
    .stTabs {{ overflow-x: auto !important; white-space: nowrap !important; }}
    .stTabs [data-testid="stTab"] {{ min-width: max-content !important; font-size: 0.68rem !important; padding: 7px 13px !important; }}
    .er {{ flex-wrap: wrap !important; gap: 6px !important; }}
    .en {{ min-width: 100% !important; }}
    .eb {{ min-width: 100% !important; }}
}}
@media (max-width: 480px) {{
    [data-testid="stHorizontalBlock"] > div {{ min-width: 100% !important; flex: none !important; }}
    .mc {{ min-width: 100% !important; }}
    .cc {{ min-width: 100% !important; }}
    .mn {{ font-size: 1.7rem !important; }}
    .ct {{ height: 80px !important; font-size: 2rem !important; }}
    .stTabs [data-testid="stTab"] {{ font-size: 0.6rem !important; padding: 5px 9px !important; }}
}}
</style>
"""

st.markdown(css(is_dark), unsafe_allow_html=True)

# ─── TOP BAR ────────────────────────────────────────────────────────────────
col_t1, col_t2 = st.columns([5, 1])

with col_t1:
    factory_name = get_config("factory_name", "Alpha Industries")
    st.markdown(f"### 🏭 {factory_name}", unsafe_allow_html=False)

with col_t2:
    icon = "🌙" if is_dark else "☀️"
    label = "Dark" if not is_dark else "Light"
    if st.button(f"{icon} {label} Mode", use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Overview",
    "📹 Camera Feeds",
    "🔥 Safety Alerts",
    "🪖 PPE Compliance",
    "🔄 Shift Reports",
    "⚙️ Equipment",
    "📱 Notifications",
    "⚙️ Settings",
])

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    now = datetime.now()
    st.markdown(f"""
    <div style="text-align:center; padding:6px 0 2px;">
        <div style="font-size:1.5rem;">🏭</div>
        <div class="sval">AI24x7 Factory</div>
        <div class="svall">Edition v1.0</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")

    col_lp = st.columns([2, 1])
    with col_lp[0]:
        st.markdown('<span class="lp">● LIVE</span>', unsafe_allow_html=True)
    with col_lp[1]:
        st.markdown(f'<div class="svall" style="text-align:right; margin-top:4px;">{now.strftime("%H:%M")}</div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">Factory</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sval">{get_config("factory_name","Alpha Industries")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="svall">ID: {get_config("factory_id","FACT-001")}</div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">Current Shift</div>', unsafe_allow_html=True)
    st.markdown('<div class="sval">⏰ Morning Shift</div>', unsafe_allow_html=True)
    st.markdown('<div class="svall">06:00 – 14:00</div>', unsafe_allow_html=True)

    stats = get_dashboard_stats()
    st.markdown('<div class="slbl">Quick Stats</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sval tg">👷 {stats["workers"]} Workers</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sval tb">🪖 {stats["ppe"]}% PPE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sval to">🔔 {stats["alerts_today"]} Alerts</div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">Cameras</div>', unsafe_allow_html=True)
    for cam in get_all_cameras():
        dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
        col = g if cam["status"]=="online" else o if cam["status"]=="warning" else cr3
        st.markdown(f'<div style="font-size:0.7rem !important; font-weight:700 !important; color:{col};">{dot} {cam["name"]}</div>', unsafe_allow_html=True)

    st.markdown("")
    st.caption(f"Updated: {now.strftime('%H:%M:%S')}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 0: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    stats = get_dashboard_stats()
    cameras = get_all_cameras()

    st.markdown('<div class="sh"><span class="si">📊</span><span class="st">Key Metrics</span><span class="sl"></span></div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="mc g"><div class="mn tg">{stats["workers"]}</div><div class="ml">Active Workers</div><div class="md" style="color:{g};">▲ +3 today</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="mc b"><div class="mn tb">{stats["ppe"]}%</div><div class="ml">PPE Compliance</div><div class="md" style="color:{g};">▲ +2% this week</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="mc o"><div class="mn to">{stats["alerts_today"]}</div><div class="ml">Alerts Today</div><div class="md" style="color:{r};">🚨 {stats["critical"]} critical</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="mc g"><div class="mn tg">{stats["cameras_online"]}/{stats["cameras_total"]}</div><div class="ml">Cameras Online</div><div class="md" style="color:{o};">⚠️ {stats["cameras_total"]-stats["cameras_online"]} offline</div></div>', unsafe_allow_html=True)

    st.markdown("")
    col_grid, col_alrt = st.columns([2, 1])

    with col_grid:
        st.markdown('<div class="sh"><span class="si">📹</span><span class="st">Camera Grid</span><span class="sl"></span></div>', unsafe_allow_html=True)
        rows = [cameras[i:i+3] for i in range(0, len(cameras), 3)]
        for r in rows:
            cols_c = st.columns(3)
            for idx, cam in enumerate(r):
                with cols_c[idx]:
                    bdg = "ok" if cam["status"]=="online" else "wn" if cam["status"]=="warning" else "of"
                    dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
                    ppc = g if cam["ppe_score"]>=90 else o if cam["ppe_score"]>=75 else r
                    st.markdown(f'''<div class="cc">
<div class="ct">📹<div class="co"><span class="cid">#{cam["id"]:02d}</span><span class="cb {bdg}">{dot} {cam["status"].upper()}</span></div></div>
<div class="cbdy"><div class="cn">{cam["name"]}</div><div class="cm"><span>👥 {cam["persons"]}</span><span style="color:{ppc}; font-weight:900 !important;">PPE {cam["ppe_score"]}%</span><span>{cam["last_alert"]}</span></div></div>
</div>''', unsafe_allow_html=True)

    with col_alrt:
        st.markdown('<div class="sh"><span class="si">🚨</span><span class="st">Live Alerts</span><span class="sl"></span></div>', unsafe_allow_html=True)
        for a in get_recent_alerts(5):
            icon = {"critical":"🔥","warning":"🪖","info":"🚗","success":"✅"}.get(a["severity"],"⚠️")
            st.markdown(f'''<div class="ac {a["severity"]}">
<div class="ai">{icon}</div>
<div><div class="at">{a["message"]}</div>
<div class="am">{a.get("camera_name","")}</div>
<div class="ati">⏱ {a["created_at"]}</div></div>
</div>''', unsafe_allow_html=True)

    st.markdown("")
    col_sf, col_eq = st.columns(1)

    with col_sf:
        st.markdown('<div class="sh"><span class="si">🏆</span><span class="st">Safety Score</span><span class="sl"></span></div>', unsafe_allow_html=True)
        safety = [("🔥 Fire Safety",95,g),("🪖 PPE Compliance",stats["ppe"],g),("⚙️ Equipment",97,g),("🛢️ Spill Control",78,o),("🏗️ Hazard Zone",92,g)]
        for nm, sc, clr in safety:
            st.markdown(f'''<div class="pr"><div class="pl"><span class="pll">{nm}</span><span class="plr" style="color:{clr};">{sc}%</span></div><div class="pt"><div class="pf" style="width:{sc}%; background:linear-gradient(90deg,{clr},rgba(255,255,255,0.2));"></div></div></div>''', unsafe_allow_html=True)
        st.markdown('<div class="sb"><div class="sn">87<span style="font-size:1.3rem !important;">/100</span></div><div class="sl">Overall Safety Score</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="sh"><span class="si">⚡</span><span class="st">Quick Actions</span><span class="sl"></span></div>', unsafe_allow_html=True)
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("📸 Snapshot All", use_container_width=True):
            with st.spinner("Capturing..."):
                time.sleep(1.2)
            st.success("✅ All snapshots saved!")
    with qa2:
        if st.button("📋 Shift Report", use_container_width=True):
            st.info("📄 Report generated!")
    with qa3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with qa4:
        if st.button("🚨 Test Alert", use_container_width=True):
            st.warning("🚨 Test alert sent!")

    st.markdown(f'<div class="ft">AI24x7 Factory Edition v1.0.0 | © 2026 GOUP CONSULTANCY SERVICES LLP | Updated: {now.strftime("%d %b %Y, %H:%M")}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1: CAMERA FEEDS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="sh"><span class="si">📹</span><span class="st">Live Camera Feeds</span><span class="sl"></span></div>', unsafe_allow_html=True)
    cameras = get_all_cameras()
    fc1, fc2, fc3 = st.columns([1, 1, 1])
    fs = fc1.selectbox("Status", ["All", "Online", "Warning", "Offline"])
    fcam = fc2.selectbox("Camera", ["All"] + [c["name"] for c in cameras])
    vm = fc3.selectbox("View", ["Grid", "List"])
    filt = cameras
    if fs != "All":
        filt = [c for c in filt if c["status"].lower() == fs.lower()]
    if fcam != "All":
        filt = [c for c in filt if c["name"] == fcam]
    if vm == "Grid":
        rows2 = [filt[i:i+3] for i in range(0, len(filt), 3)]
        for r2 in rows2:
            cols_g = st.columns(3)
            for idx2, cam in enumerate(r2):
                with cols_g[idx2]:
                    bdg = "ok" if cam["status"]=="online" else "wn" if cam["status"]=="warning" else "of"
                    dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
                    ppc = g if cam["ppe_score"]>=90 else o if cam["ppe_score"]>=75 else r
                    st.markdown(f'''<div class="cc"><div class="ct" style="height:140px; font-size:3.2rem;">📹<div style="position:absolute;top:8px;right:8px;"><span class="cb {bdg}">{dot} {cam["status"].upper()}</span></div><div style="position:absolute;bottom:8px;left:8px;"><span class="cid">CAM {cam["id"]:02d}</span></div></div><div class="cbdy"><div class="cn">{cam["name"]}</div><div class="cm" style="margin-top:8px;"><span>👥 {cam["persons"]} workers</span><span style="color:{ppc}; font-weight:900 !important;">PPE {cam["ppe_score"]}%</span><span>{cam["last_alert"]}</span></div></div></div>''', unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        st.button(f"📸 #{cam['id']}", key=f"sn{cam['id']}", use_container_width=True)
                    with b2:
                        st.button(f"📊 #{cam['id']}", key=f"an{cam['id']}", use_container_width=True)
    else:
        import pandas as pd
        df = pd.DataFrame(filt)
        st.table(df)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2: SAFETY ALERTS
# ════════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    stats = get_dashboard_stats()
    st.markdown('<div class="sh"><span class="si">🔥</span><span class="st">Safety Alert Center</span><span class="sl"></span></div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    a1.metric("🔴 Total Alerts", stats["alerts_today"], delta=3)
    a2.metric("🚨 Critical", stats["critical"], delta_color="inverse")
    a3.metric("✅ Resolved", stats["alerts_today"] - stats["critical"])
    ft = st.selectbox("Filter by Type", ["All", "Fire", "PPE", "Spill", "Entry", "Equipment"])
    for a in get_recent_alerts(10):
        if ft != "All" and ft.lower() not in a["message"].lower():
            continue
        icon = {"critical":"🔥","warning":"🪖","info":"🚗","success":"✅"}.get(a["severity"],"⚠️")
        st.markdown(f'''<div class="ac {a["severity"]}"><div class="ai">{icon}</div><div><div class="at">{a["message"]}</div><div class="am">{a.get("camera_name","")}</div><div class="ati">⏱ {a["created_at"]}</div></div></div>''', unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            if st.button(f"✅ Ack #{a['id']}", key=f"ack{a['id']}", use_container_width=True):
                acknowledge_alert(a["id"])
                st.success("Alert acknowledged!")
        with cb2:
            st.button(f"📞 Escalate", key=f"esc{a['id']}", use_container_width=True)
    st.markdown("")
    st.markdown('<div class="sh"><span class="si">📊</span><span class="st">Alert History — Last 7 Days</span><span class="sl"></span></div>', unsafe_allow_html=True)
    st.bar_chart({"🔥 Fire":[2,1,0,3,1,0,1],"🪖 PPE":[5,3,4,2,6,1,2]}, height=200)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3: PPE COMPLIANCE
# ════════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="sh"><span class="si">🪖</span><span class="st">PPE Compliance Dashboard</span><span class="sl"></span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb"><div class="sn">91<span style="font-size:1.3rem !important;">/100</span></div><div class="sl">Overall PPE Compliance — Target: 95%</div></div>', unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("🪖 Helmet", "96%", delta=2)
    p2.metric("🦺 Safety Vest", "94%", delta=1)
    p3.metric("🧤 Gloves", "82%", delta=-5)
    p4.metric("👢 Safety Shoes", "88%", delta=-2)
    st.markdown('<div class="sh"><span class="si">📹</span><span class="st">Camera-wise PPE Score</span><span class="sl"></span></div>', unsafe_allow_html=True)
    for cam in get_all_cameras():
        sc = cam["ppe_score"]
        clr = g if sc>=90 else o if sc>=75 else r
        st.markdown(f'''<div style="display:flex; align-items:center; gap:14px; background:{crd}; border:2px solid {bc}; border-radius:10px; padding:10px 15px; margin-bottom:7px;">
<div style="min-width:125px;"><span style="font-size:0.85rem !important; font-weight:900 !important;">{cam["name"]}</span></div>
<div style="flex:1;"><div class="pt" style="height:8px;"><div class="pf" style="width:{sc}%; background:linear-gradient(90deg,{clr},rgba(255,255,255,0.25));"></div></div></div>
<div style="min-width:50px; text-align:right;"><span style="font-size:0.95rem !important; font-weight:900 !important; color:{clr};">{sc}%</span></div>
</div>''', unsafe_allow_html=True)
    st.markdown('<div class="sh"><span class="si">⚠️</span><span class="st">Recent Violations</span><span class="sl"></span></div>', unsafe_allow_html=True)
    for v in get_ppe_violations(5):
        vicon = {"no_helmet":"🪖","no_safety_vest":"🦺","no_gloves":"🧤","improper_shoes":"👢"}.get(v["violation_type"],"⚠️")
        st.markdown(f'''<div class="ac war"><div class="ai">{vicon}</div><div><div class