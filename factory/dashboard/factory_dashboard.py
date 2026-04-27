#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Dashboard v4.0
Top Tab Navigation + Bold Design
"""
import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="AI24x7 Factory", page_icon="🏭", layout="wide", initial_sidebar_state="collapsed")

# ─── BOLD CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* BASE */
.stApp { background: #080b12; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
* { font-weight: 700 !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #3b82f6, #10b981); border-radius: 3px; }

/* TOP BAR */
.topbar { background: #0d1117; border-bottom: 2px solid #1f2937; padding: 0; margin: -1rem -1rem 1.5rem -1rem; display: flex; align-items: stretch; gap: 0; overflow-x: auto; }

/* TAB NAV */
.tab-btn { display: flex; align-items: center; gap: 7px; padding: 14px 22px; font-size: 0.82rem !important; font-weight: 700 !important; color: #6b7280; border: none; border-bottom: 3px solid transparent; background: none; cursor: pointer; white-space: nowrap; transition: all 0.2s; border-radius: 0; flex-shrink: 0; }
.tab-btn:hover { color: #e5e7eb; background: #161b26; }
.tab-btn.active { color: #3b82f6; border-bottom-color: #3b82f6; background: #111827; }
.tab-right { margin-left: auto; display: flex; align-items: center; padding: 0 20px; gap: 14px; flex-shrink: 0; }

/* SIDEBAR - MINIMAL */
[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 2px solid #1f2937 !important; width: 240px !important; }
.sidebar-mini { padding: 12px; }
.side-label { font-size: 0.6rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.15em; color: #374151; margin-bottom: 8px; margin-top: 14px; }

/* METRIC CARDS */
.metric-card { background: #111827; border-radius: 16px; padding: 20px 22px 18px; border: 2px solid #1f2937; transition: all 0.25s; overflow: hidden; position: relative; }
.metric-card:hover { border-color: #374151; transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.metric-card.g::before { background: linear-gradient(90deg, #10b981, #34d399, #10b981); }
.metric-card.b::before { background: linear-gradient(90deg, #3b82f6, #60a5fa, #3b82f6); }
.metric-card.o::before { background: linear-gradient(90deg, #f59e0b, #fbbf24, #f59e0b); }
.metric-card.r::before { background: linear-gradient(90deg, #ef4444, #f87171, #ef4444); }
.metric-card.p::before { background: linear-gradient(90deg, #8b5cf6, #a78bfa, #8b5cf6); }
.mnum { font-size: 2.4rem !important; font-weight: 900 !important; line-height: 1 !important; margin-bottom: 5px; letter-spacing: -0.02em; }
.mlbl { font-size: 0.65rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.12em; color: #4b5563; }
.mdlt { font-size: 0.7rem !important; font-weight: 700 !important; margin-top: 5px; }

/* CAMERA CARDS */
.cam-card { background: #111827; border: 2px solid #1f2937; border-radius: 14px; overflow: hidden; transition: all 0.2s; }
.cam-card:hover { border-color: #3b82f6; transform: translateY(-2px); box-shadow: 0 8px 25px rgba(59,130,246,0.15); }
.cam-thumb { background: linear-gradient(135deg, #060810, #0d1117, #111827); height: 110px; display: flex; align-items: center; justify-content: center; font-size: 2.8rem; position: relative; }
.cam-overlay { position: absolute; bottom: 0; left: 0; right: 0; padding: 6px 10px; background: linear-gradient(transparent, rgba(0,0,0,0.9)); display: flex; justify-content: space-between; align-items: center; }
.cam-id { font-size: 0.6rem !important; font-weight: 800 !important; color: rgba(255,255,255,0.4) !important; }
.cam-badge { padding: 2px 8px; border-radius: 6px; font-size: 0.6rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.05em; }
.cam-badge.ok { background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.35); }
.cam-badge.warn { background: rgba(245,158,11,0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); }
.cam-badge.off { background: rgba(107,114,128,0.15); color: #6b7280; border: 1px solid rgba(107,114,128,0.25); }
.cam-body { padding: 12px 14px; }
.cam-name { font-size: 0.88rem !important; font-weight: 800 !important; margin-bottom: 8px; color: #f9fafb; }
.cam-meta { display: flex; justify-content: space-between; align-items: center; }
.cam-meta span { font-size: 0.7rem !important; font-weight: 700 !important; color: #6b7280; }

/* ALERT CARDS */
.alert-card { background: #111827; border-radius: 12px; padding: 13px 16px; margin-bottom: 7px; display: flex; align-items: flex-start; gap: 11px; border: 2px solid; transition: all 0.2s; }
.alert-card:hover { transform: translateX(2px); }
.alert-card.cri { border-color: rgba(239,68,68,0.4); border-left: 4px solid #ef4444; }
.alert-card.war { border-color: rgba(245,158,11,0.4); border-left: 4px solid #f59e0b; }
.alert-card.inf { border-color: rgba(59,130,246,0.4); border-left: 4px solid #3b82f6; }
.alert-card.suc { border-color: rgba(16,185,129,0.4); border-left: 4px solid #10b981; }
.a-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }
.a-title { font-size: 0.88rem !important; font-weight: 800 !important; color: #f9fafb; margin-bottom: 2px; }
.a-msg { font-size: 0.78rem !important; font-weight: 700 !important; color: #6b7280; }
.a-time { font-size: 0.68rem !important; font-weight: 800 !important; color: #374151; margin-top: 2px; }

/* PROGRESS BAR */
.prog-row { margin-bottom: 11px; }
.prog-lbl { display: flex; justify-content: space-between; margin-bottom: 5px; }
.prog-lbl-l { font-size: 0.82rem !important; font-weight: 700 !important; color: #9ca3af; }
.prog-lbl-r { font-size: 0.82rem !important; font-weight: 900 !important; }
.prog-track { height: 8px; background: #1f2937; border-radius: 4px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 4px; transition: width 1.2s cubic-bezier(0.4,0,0.2,1); }

/* INFO CARD */
.info-card { background: #111827; border: 2px solid #1f2937; border-radius: 14px; padding: 16px 18px; }

/* SECTION HEADER */
.sec-hdr { display: flex; align-items: center; gap: 8px; margin: 18px 0 14px 0; }
.sec-icon { font-size: 1rem; }
.sec-txt { font-size: 0.65rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.15em; color: #374151; flex: 1; }
.sec-line { height: 1px; flex: 3; background: linear-gradient(90deg, #1f2937, transparent); }

/* EQUIPMENT ROW */
.equip-row { display: flex; align-items: center; gap: 14px; padding: 10px 0; border-bottom: 1px solid #1a1d2e; }
.equip-row:last-child { border-bottom: none; }
.equip-name { font-size: 0.85rem !important; font-weight: 800 !important; min-width: 140px; }
.equip-stat { font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.05em; min-width: 90px; }
.equip-bar { flex: 1; }
.equip-uptime { font-size: 0.8rem !important; font-weight: 900 !important; min-width: 55px; text-align: right; }

/* SCORE BIG */
.score-box { background: linear-gradient(135deg, #064e3b, #059669, #10b981); border: 2px solid #059669; border-radius: 18px; padding: 26px; text-align: center; }
.score-num { font-size: 3.2rem !important; font-weight: 900 !important; color: #fff; line-height: 1 !important; text-shadow: 0 0 25px rgba(16,185,129,0.5); }
.score-lbl { font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.12em; color: rgba(255,255,255,0.7); margin-top: 6px; }

/* BIG HERO */
.hero-callout { background: linear-gradient(135deg, #0c1a35, #0d1117); border: 2px solid #1e3a5f; border-radius: 20px; padding: 28px; text-align: center; }
.hero-num { font-size: 3.5rem !important; font-weight: 900 !important; color: #fff; line-height: 1 !important; text-shadow: 0 0 20px rgba(59,130,246,0.4); }
.hero-lbl { font-size: 0.8rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.12em; color: #60a5fa; margin-top: 6px; }

/* TABLE */
.stTable { background: #111827 !important; border-radius: 12px !important; border: 2px solid #1f2937 !important; overflow: hidden !important; }
[data-testid="stTable"] th { background: #0d1117 !important; font-size: 0.62rem !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.12em !important; color: #374151 !important; padding: 12px 16px !important; border-bottom: 2px solid #1f2937 !important; }
[data-testid="stTable"] td { font-size: 0.82rem !important; font-weight: 700 !important; color: #d1d5db !important; padding: 11px 16px !important; border-bottom: 1px solid #1a1d2e !important; }
[data-testid="stTable"] tr:last-child td { border-bottom: none !important; }
[data-testid="stTable"] tr:hover td { background: #161b26 !important; }

/* BUTTON */
.stButton > button { border-radius: 10px !important; font-weight: 800 !important; font-size: 0.8rem !important; transition: all 0.15s !important; border: 2px solid !important; }
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important; }

/* EXPANDER */
.streamlit-expanderHeader { background: #111827 !important; border: 2px solid #1f2937 !important; border-radius: 10px !important; font-size: 0.85rem !important; font-weight: 800 !important; }
.streamlit-expanderContent { background: #080b12 !important; border: 2px solid #1f2937 !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }

/* DIVIDER */
hr { border: none !important; border-top: 2px solid #1f2937 !important; margin: 1rem 0 !important; }

/* COLUMNS */
[data-testid="stHorizontalBlock"] > div { gap: 10px !important; }

/* LIVE BADGE */
.live-pill { background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 5px 14px; border-radius: 20px; font-size: 0.68rem !important; font-weight: 900 !important; letter-spacing: 0.12em; text-transform: uppercase; box-shadow: 0 0 18px rgba(16,185,129,0.4); animation: lg 2s ease-in-out infinite alternate; }
@keyframes lg { from{box-shadow:0 0 8px rgba(16,185,129,0.3)} to{box-shadow:0 0 22px rgba(16,185,129,0.6)} }

/* TEXT COLORS */
.tg { color: #10b981 !important; }
.tb { color: #3b82f6 !important; }
.to { color: #f59e0b !important; }
.tr { color: #ef4444 !important; }
.tp { color: #a78bfa !important; }
.tgr { color: #6b7280 !important; }
.tw { color: #f9fafb !important; }
.tk { color: #9ca3af !important; }

/* FOOTER */
.foot { text-align: center; font-size: 0.65rem !important; font-weight: 600 !important; color: #1f2937; padding: 16px 0; }

/* NAVIGATION ACTIVE STATE */
.nav-active { background: #111827; color: #3b82f6; font-weight: 800 !important; }
.nav-inactive { background: transparent; color: #6b7280; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
def get_stats():
    return {"workers":47,"ppe":91,"alerts":12,"critical":1,"cams_on":5,"cams_tot":6,"fire_risk":"Low","uptime":97.3,"shift":"Morning"}

def get_cameras():
    return [
        {"id":1,"name":"Assembly Area","status":"online","persons":12,"ppe":94,"last":"5m ago"},
        {"id":2,"name":"Gate 1 - Entry","status":"online","persons":3,"ppe":100,"last":"23m ago"},
        {"id":3,"name":"Paint Shop","status":"warning","persons":5,"ppe":78,"last":"12m ago"},
        {"id":4,"name":"Machine Hall A","status":"online","persons":8,"ppe":96,"last":"45m ago"},
        {"id":5,"name":"Storage Area","status":"offline","persons":0,"ppe":0,"last":"2h ago"},
        {"id":6,"name":"Loading Dock","status":"online","persons":4,"ppe":100,"last":"1h ago"},
    ]

def get_alerts():
    return [
        {"t":"cri","i":"🔥","tt":"Fire Detected!","mm":"Assembly Area — confidence 94%","tm":"5 min ago"},
        {"t":"war","i":"🪖","tt":"PPE Violation","mm":"Paint Shop — No helmet detected","tm":"12 min ago"},
        {"t":"inf","i":"🚗","tt":"Unknown Vehicle","mm":"Gate 1 — Unrecognized vehicle","tm":"23 min ago"},
        {"t":"war","i":"🛢️","tt":"Spill Detected","mm":"Machine Hall A — Oil spill near Machine B","tm":"45 min ago"},
        {"t":"suc","i":"🔄","tt":"Shift Changed","mm":"Now: Afternoon Shift — 14:00 to 22:00","tm":"1 hour ago"},
    ]

def get_safety():
    return [("🔥 Fire Safety",95,"#10b981"),("🪖 PPE Compliance",91,"#10b981"),("⚙️ Equipment",97,"#10b981"),("🛢️ Spill Control",78,"#f59e0b"),("🏗️ Hazard Zone",92,"#10b981")]

def get_equip():
    return [
        ("Conveyor A","RUNNING",98,True),("Conveyor B","RUNNING",95,True),("Robot Arm 1","RUNNING",100,True),
        ("CNC Machine","MAINTENANCE",0,False),("Furnace 1","RUNNING",92,True),("Compressor","RUNNING",88,True),
    ]

# ─── TOP NAV BAR ──────────────────────────────────────────────────────────────
nav_items = [
    ("📊","Overview"),("📹","Camera Feeds"),("🔥","Safety Alerts"),
    ("🪖","PPE Compliance"),("🔄","Shift Reports"),("⚙️","Equipment"),
    ("📱","Notifications"),("⚙️","Settings"),
]

# Query param for active tab
params = st.query_params
active_param = params.get("page", "Overview")

# Map nav items
nav_map = {name: idx for idx, (icon, name) in enumerate(nav_items)}

# JS for tab switching - use Streamlit tabs instead
tab_icons = [f"{icon} {name}" for icon, name in nav_items]

# Use Streamlit native tabs
page = st.tabs(tab_icons)

# Map page back to active tab index
def get_page_idx():
    try:
        return nav_map.get(active_param, 0)
    except:
        return 0

# ─── SIDEBAR (MINIMAL) ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 8px 0 4px;">
        <div style="font-size:1.6rem;">🏭</div>
        <div style="font-size:0.75rem !important; font-weight:900 !important; color:#f9fafb; margin-top:2px;">AI24x7</div>
        <div style="font-size:0.6rem !important; font-weight:700 !important; color:#374151; text-transform:uppercase; letter-spacing:0.1em;">Factory Edition</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""<hr style="margin:8px 0;">""", unsafe_allow_html=True)

    # Live badge + time
    now = datetime.now()
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; padding:0 4px;">
        <span class="live-pill">● LIVE</span>
        <span style="font-size:0.72rem !important; font-weight:700 !important; color:#4b5563;">{now.strftime('%H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""<div class="side-label">Factory</div>""", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.78rem !important; font-weight:800 !important; color:#e5e7eb;'>Alpha Industries</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.68rem !important; font-weight:700 !important; color:#374151;'>ID: FACT-001</div>", unsafe_allow_html=True)

    st.markdown(f"""<div class="side-label">Shift</div>""", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem !important; font-weight:800 !important; color:#60a5fa;'>⏰ Morning Shift</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.68rem !important; font-weight:700 !important; color:#374151;'>06:00 – 14:00</div>", unsafe_allow_html=True)

    st.markdown(f"""<div class="side-label">Quick Stats</div>""", unsafe_allow_html=True)
    stats = get_stats()
    st.markdown(f"<div style='font-size:0.82rem !important; font-weight:800 !important; color:#10b981;'>👷 {stats['workers']} Workers</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.82rem !important; font-weight:800 !important; color:#3b82f6;'>🪖 {stats['ppe']}% PPE</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.82rem !important; font-weight:800 !important; color:#f59e0b;'>🔔 {stats['alerts']} Alerts</div>", unsafe_allow_html=True)

    st.markdown(f"""<div class="side-label">Cameras</div>""", unsafe_allow_html=True)
    for cam in get_cameras():
        dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "⚫"
        tc = "#10b981" if cam["status"]=="online" else "#f59e0b" if cam["status"]=="warning" else "#374151"
        st.markdown(f"<div style='font-size:0.72rem !important; font-weight:700 !important; color:{tc};'>{dot} {cam['name']}</div>", unsafe_allow_html=True)

    st.markdown("")
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 0: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════════
with page[0]:
    stats = get_stats()
    cameras = get_cameras()

    # TOP METRICS ROW
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📊</span><span class="sec-txt">Key Metrics</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class="metric-card g">
            <div class="mnum tg">47</div>
            <div class="mlbl">Active Workers</div>
            <div class="mdlt" style="color:#10b981;">▲ +3 today</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="metric-card b">
            <div class="mnum tb">91%</div>
            <div class="mlbl">PPE Compliance</div>
            <div class="mdlt" style="color:#10b981;">▲ +2% this week</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="metric-card o">
            <div class="mnum to">12</div>
            <div class="mlbl">Alerts Today</div>
            <div class="mdlt" style="color:#ef4444;">🚨 1 critical</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="metric-card g">
            <div class="mnum tg">5/6</div>
            <div class="mlbl">Cameras Online</div>
            <div class="mdlt" style="color:#f59e0b;">⚠️ 1 offline</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # CAMERA GRID + ALERTS
    col_grid, col_alrt = st.columns([2, 1])

    with col_grid:
        st.markdown("""
        <div class="sec-hdr"><span class="sec-icon">📹</span><span class="sec-txt">Camera Grid</span><span class="sec-line"></span></div>
        """, unsafe_allow_html=True)

        rows = [cameras[i:i+3] for i in range(0, len(cameras), 3)]
        for r in rows:
            cols_c = st.columns(3)
            for idx, cam in enumerate(r):
                with cols_c[idx]:
                    bdg = "ok" if cam["status"]=="online" else "warn" if cam["status"]=="warning" else "off"
                    dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
                    ppc = "#10b981" if cam["ppe"]>=90 else "#f59e0b" if cam["ppe"]>=75 else "#ef4444"

                    st.markdown(f"""
                    <div class="cam-card">
                        <div class="cam-thumb">
                            📹
                            <div class="cam-overlay">
                                <span class="cam-id">#{cam['id']:02d}</span>
                                <span class="cam-badge {bdg}">{dot} {cam['status'].upper()}</span>
                            </div>
                        </div>
                        <div class="cam-body">
                            <div class="cam-name">{cam['name']}</div>
                            <div class="cam-meta">
                                <span>👥 {cam['persons']}</span>
                                <span style="color:{ppc}; font-weight:900 !important;">PPE {cam['ppe']}%</span>
                                <span>{cam['last']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with col_alrt:
        st.markdown("""
        <div class="sec-hdr"><span class="sec-icon">🚨</span><span class="sec-txt">Live Alerts</span><span class="sec-line"></span></div>
        """, unsafe_allow_html=True)

        for a in get_alerts():
            st.markdown(f"""
            <div class="alert-card {a['t']}">
                <div class="a-icon">{a['i']}</div>
                <div>
                    <div class="a-title">{a['tt']}</div>
                    <div class="a-msg">{a['mm']}</div>
                    <div class="a-time">⏱ {a['tm']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # SAFETY + EQUIPMENT
    col_sf, col_eq = st.columns([1, 1])

    with col_sf:
        st.markdown("""
        <div class="sec-hdr"><span class="sec-icon">🏆</span><span class="sec-txt">Safety Score</span><span class="sec-line"></span></div>
        """, unsafe_allow_html=True)

        for nm, sc, clr in get_safety():
            st.markdown(f"""
            <div class="prog-row">
                <div class="prog-lbl">
                    <span class="prog-lbl-l">{nm}</span>
                    <span class="prog-lbl-r" style="color:{clr};">{sc}%</span>
                </div>
                <div class="prog-track">
                    <div class="prog-fill" style="width:{sc}%; background:linear-gradient(90deg,{clr},rgba(255,255,255,0.2));"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("""
        <div class="score-box">
            <div class="score-num">87<span style="font-size:1.4rem !important;">/100</span></div>
            <div class="score-lbl">Overall Safety Score</div>
        </div>
        """, unsafe_allow_html=True)

    with col_eq:
        st.markdown("""
        <div class="sec-hdr"><span class="sec-icon">⚙️</span><span class="sec-txt">Equipment</span><span class="sec-line"></span></div>
        """, unsafe_allow_html=True)

        for nm, st2, up, ok in get_equip():
            clr = "#10b981" if ok else "#ef4444"
            dot = "🟢" if ok else "🔴"
            st2_cls = "tg" if ok else "tr"
            bar_w = up if ok else 100

            st.markdown(f"""
            <div class="equip-row">
                <div class="equip-name">{dot} {nm}</div>
                <div class="equip-stat {st2_cls}">{st2}</div>
                <div class="equip-bar">
                    <div class="prog-track" style="height:6px;">
                        <div class="prog-fill" style="width:{bar_w}%; background:{clr};"></div>
                    </div>
                </div>
                <div class="equip-uptime" style="color:{clr};">{up}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # QUICK ACTIONS
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">⚡</span><span class="sec-txt">Quick Actions</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)
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

    st.markdown(f"""<div class="foot">AI24x7 Factory Edition v1.0.0 | © 2026 GOUP CONSULTANCY SERVICES LLP | FACT-001 | Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1: CAMERA FEEDS
# ════════════════════════════════════════════════════════════════════════════════
with page[1]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📹</span><span class="sec-txt">Live Camera Feeds</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    cameras = get_cameras()
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
                    bdg = "ok" if cam["status"]=="online" else "warn" if cam["status"]=="warning" else "off"
                    dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
                    ppc = "#10b981" if cam["ppe"]>=90 else "#f59e0b" if cam["ppe"]>=75 else "#ef4444"

                    st.markdown(f"""
                    <div class="cam-card">
                        <div class="cam-thumb" style="height:145px; font-size:3.5rem;">
                            📹
                            <div style="position:absolute; top:8px; right:8px;">
                                <span class="cam-badge {bdg}">{dot} {cam['status'].upper()}</span>
                            </div>
                            <div style="position:absolute; bottom:8px; left:8px;">
                                <span class="cam-id">CAM {cam['id']:02d}</span>
                            </div>
                        </div>
                        <div class="cam-body">
                            <div class="cam-name">{cam['name']}</div>
                            <div class="cam-meta" style="margin-top:8px;">
                                <span>👥 {cam['persons']} workers</span>
                                <span style=":color:{ppc}; font-weight:900 !important;">PPE {cam['ppe']}%</span>
                                <span>{cam['last']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1:
                        st.button(f"📸 Snapshot #{cam['id']}", key=f"sn{cam['id']}", use_container_width=True)
                    with b2:
                        st.button(f"📊 Analytics #{cam['id']}", key=f"an{cam['id']}", use_container_width=True)
    else:
        import pandas as pd
        df = pd.DataFrame(filt)
        st.table(df)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2: SAFETY ALERTS
# ════════════════════════════════════════════════════════════════════════════════
with page[2]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">🔥</span><span class="sec-txt">Safety Alert Center</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3)
    a1.metric("🔴 Total Alerts", 12, delta=3)
    a2.metric("🚨 Critical", 1, delta_color="inverse")
    a3.metric("✅ Resolved", 9)

    ft = st.selectbox("Filter by Type", ["All","Fire","PPE","Spill","Entry","Equipment"])
    fs2 = st.selectbox("Status", ["All","Unhandled","Handled"])

    for a in get_alerts():
        if ft != "All" and ft.lower() not in a["tt"].lower():
            continue
        st.markdown(f"""
        <div class="alert-card {a['t']}">
            <div class="a-icon">{a['i']}</div>
            <div>
                <div class="a-title">{a['tt']}</div>
                <div class="a-msg">{a['mm']}</div>
                <div class="a-time">⏱ {a['tm']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.button(f"✅ Acknowledge: {a['tt']}", key=f"ack{a['tt']}", use_container_width=True)
        with c2:
            st.button(f"📞 Escalate: {a['tt']}", key=f"esc{a['tt']}", use_container_width=True)

    st.markdown("")
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📊</span><span class="sec-txt">Alert History — Last 7 Days</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    st.bar_chart({"🔥 Fire":[2,1,0,3,1,0,1],"🪖 PPE":[5,3,4,2,6,1,2]}, height=200)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3: PPE COMPLIANCE
# ════════════════════════════════════════════════════════════════════════════════
with page[3]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">🪖</span><span class="sec-txt">PPE Compliance Dashboard</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #064e3b, #059669, #10b981); border: 2px solid #059669; border-radius: 22px; padding: 30px; text-align: center; margin-bottom: 22px;">
        <div style="font-size: 4rem !important; font-weight: 900 !important; color: #fff; line-height: 1; text-shadow: 0 0 30px rgba(16,185,129,0.5);">91%</div>
        <div style="font-size: 0.9rem !important; font-weight: 700 !important; color: rgba(255,255,255,0.85); margin-top: 6px;">Overall PPE Compliance</div>
        <div style="font-size: 0.72rem !important; font-weight: 800 !important; color: rgba(255,255,255,0.55); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.12em;">Target: 95%</div>
    </div>
    """, unsafe_allow_html=True)

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("🪖 Helmet", "96%", delta=2)
    p2.metric("🦺 Safety Vest", "94%", delta=1)
    p3.metric("🧤 Gloves", "82%", delta=-5)
    p4.metric("👢 Safety Shoes", "88%", delta=-2)

    st.markdown("")
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📹</span><span class="sec-txt">Camera-wise PPE Score</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    for cam in get_cameras():
        sc = cam["ppe"]
        clr = "#10b981" if sc>=90 else "#f59e0b" if sc>=75 else "#ef4444"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; background:#111827; border:2px solid #1f2937; border-radius:10px; padding:11px 16px; margin-bottom:8px;">
            <div style="min-width:130px;"><span style="font-size:0.88rem !important; font-weight:900 !important;">{cam['name']}</span></div>
            <div style="flex:1;">
                <div class="prog-track" style="height:9px;">
                    <div class="prog-fill" style="width:{sc}%; background:linear-gradient(90deg,{clr},rgba(255,255,255,0.25));"></div>
                </div>
            </div>
            <div style="min-width:55px; text-align:right;"><span style="font-size:1rem !important; font-weight:900 !important; color:{clr};">{sc}%</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">⚠️</span><span class="sec-txt">Recent Violations</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    viol = [
        ("🪖","No Helmet Detected","Paint Shop","Ramesh Kumar","12 min ago"),
        ("🦺","No Safety Vest","Assembly Area","Unknown Worker","28 min ago"),
        ("🧤","No Gloves","Machine Hall A","Suresh Patil","45 min ago"),
        ("👢","Improper Shoes","Gate 1","Labour 007","1 hour ago"),
    ]
    for ic, tt, cm, pr, tm in viol:
        st.markdown(f"""
        <div class="alert-card war">
            <div class="a-icon">{ic}</div>
            <div>
                <div class="a-title">{tt}</div>
                <div class="a-msg">{cm} • {pr}</div>
                <div class="a-time">⏱ {tm}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("📋 Export PPE Report", use_container_width=True, type="primary"):
        st.success("✅ PPE Report exported!")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4: SHIFT REPORTS
# ════════════════════════════════════════════════════════════════════════════════
with page[4]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">🔄</span><span class="sec-txt">Shift Reports</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    s1, s2 = st.columns([1, 1])
    with s1:
        st.markdown("""
        <div class="info-card" style="text-align:center;">
            <div style="font-size:1.6rem !important; font-weight:900 !important; color:#3b82f6;">⏰ Morning Shift</div>
            <div style="font-size:0.82rem !important; font-weight:700 !important; color:#6b7280; margin-top:4px;">06:00 — 14:00</div>
            <div style="font-size:0.82rem !important; font-weight:700 !important; color:#9ca3af; margin-top:6px;">50% Complete</div>
            <div class="prog-track" style="margin-top:12px; height:10px;">
                <div class="prog-fill" style="width:50%; background:linear-gradient(90deg,#3b82f6,#60a5fa);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.selectbox("Select Report", ["Morning Shift — 27 Apr 2026","Afternoon Shift — 26 Apr 2026","Night Shift — 26 Apr 2026"])

    st.markdown("")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("👷 Total Workers", 47)
    s2.metric("🪖 PPE Violations", 3)
    s3.metric("🚨 Incidents", 0)
    s4.metric("⚙️ Downtime", "0.5h")

    st.markdown("")
    import pandas as pd
    df = pd.DataFrame({"Metric":["Total Workers","PPE Violations","Fire Alarms","Unauthorized Entry","Spill Incidents","Equipment Downtime"],"Value":[47,3,0,1,1,"0.5 hours"]})
    st.table(df)

    b1, b2, b3 = st.columns(3)
    with b1:
        st.button("📄 Generate PDF Report", use_container_width=True)
    with b2:
        st.button("📤 Export CSV", use_container_width=True)
    with b3:
        st.button("📧 Email to Manager", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 5: EQUIPMENT
# ════════════════════════════════════════════════════════════════════════════════
with page[5]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">⚙️</span><span class="sec-txt">Equipment Monitoring</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("🔧 Total Machines", 7)
    e2.metric("🟢 Running", 6)
    e3.metric("🔴 Maintenance", 1)
    e4.metric("📈 Avg Uptime", "94%")

    st.markdown("")
    equip_all = [
        ("Conveyor A","RUNNING",98,True,"8h 23m"),("Conveyor B","RUNNING",95,True,"6h 45m"),
        ("Robot Arm 1","RUNNING",100,True,"12h 00m"),("CNC Machine","MAINTENANCE",0,False,"0h 30m"),
        ("Furnace 1","RUNNING",92,True,"8h 10m"),("Compressor","RUNNING",88,True,"5h 15m"),
        ("Hydraulic Press","STOPPED",0,False,"3h 00m"),("AGV Robot","RUNNING",96,True,"4h 50m"),
    ]
    for nm, st3, up, ok, rt in equip_all:
        clr = "#10b981" if ok else "#ef4444"
        dot = "🟢" if ok else "🔴"
        scls = "tg" if ok else "tr"
        bw = up if ok else 100
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; background:#111827; border:2px solid #1f2937; border-radius:10px; padding:11px 16px; margin-bottom:7px;">
            <div style="min-width:150px;"><span style="font-size:0.9rem !important; font-weight:900 !important;">{dot} {nm}</span></div>
            <div style="min-width:105px;"><span class="{scls}" style="font-size:0.72rem !important; font-weight:800 !important;">{st3}</span></div>
            <div style="flex:1;">
                <div class="prog-track" style="height:7px;">
                    <div class="prog-fill" style="width:{bw}%; background:{clr};"></div>
                </div>
            </div>
            <div style="min-width:55px; text-align:right;"><span style="font-size:0.88rem !important; font-weight:900 !important; color:{clr};">{up}%</span></div>
            <div style="min-width:70px; text-align:right;"><span style="font-size:0.72rem !important; font-weight:700 !important; color:#374151;">{rt}</span></div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 6: NOTIFICATIONS
# ════════════════════════════════════════════════════════════════════════════════
with page[6]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📱</span><span class="sec-txt">Notification Settings</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-bottom:12px;">
        <div style="font-size:1rem !important; font-weight:900 !important; margin-bottom:12px;">📨 Telegram Alerts</div>
    """, unsafe_allow_html=True)
    tg = st.toggle("Enable Telegram Alerts", value=True)
    if tg:
        st.text_input("Bot Token", value="8751634203:AAEtay1...", disabled=True)
        st.text_input("Chat ID", value="8566322083")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-bottom:12px;">
        <div style="font-size:1rem !important; font-weight:900 !important; margin-bottom:12px;">📞 SMS Alerts</div>
    """, unsafe_allow_html=True)
    sm = st.toggle("Enable SMS Alerts", value=False)
    if sm:
        st.text_input("SMS API Key", type="password")
        st.text_input("Recipients", value="+91-98XXXXXXX")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card" style="margin-bottom:14px;">
        <div style="font-size:1rem !important; font-weight:900 !important; margin-bottom:12px;">💬 WhatsApp Business</div>
    """, unsafe_allow_html=True)
    wa = st.toggle("Enable WhatsApp", value=False)
    if wa:
        st.text_input("WhatsApp Business Number")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📋</span><span class="sec-txt">Alert Rules</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    rules = [
        ("🔥 Fire Detected", True, "All", "Critical"),
        ("🪖 PPE Violation", True, "All", "Warning"),
        ("🚗 Unauthorized Entry", True, "Telegram", "Warning"),
        ("🛢️ Spill Detected", True, "All", "Critical"),
        ("⚙️ Equipment Down", False, "Admin", "Info"),
        ("🔄 Shift Change", True, "Telegram", "Info"),
    ]
    for i, (nm, en, sn, sv) in enumerate(rules):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1:
            st.markdown(f"<b>{nm}</b>", unsafe_allow_html=True)
        with c2:
            st.toggle("", value=en, key=f"re{i}")
        with c3:
            st.markdown(f"<span style='font-size:0.72rem !important; font-weight:700 !important; color:#60a5fa;'>{sn}</span>", unsafe_allow_html=True)
        with c4:
            clrs = {"Critical":"#ef4444","Warning":"#f59e0b","Info":"#3b82f6"}
            st.markdown(f"<span style='color:{clrs[sv]} !important; font-weight:900 !important; font-size:0.82rem;'>{sv}</span>", unsafe_allow_html=True)

    st.markdown("")
    if st.button("💾 Save Notification Settings", use_container_width=True, type="primary"):
        st.success("✅ Settings saved!")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 7: SETTINGS
# ════════════════════════════════════════════════════════════════════════════════
with page[7]:
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">⚙️</span><span class="sec-txt">System Settings</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.text_input("🏭 Factory Name", value="Alpha Industries - Unit 1")
        st.text_input("🔖 Factory ID", value="FACT-001")
        st.text_input("🔑 License Key", value="FACTORY-XXXX-XXXX-XXXX-XXXX", disabled=True)
    with s2:
        st.selectbox("🌐 Language", ["English","Hindi","Hindi + English"])
        st.selectbox("🕐 Time Zone", ["IST (UTC+5:30)","UTC","EST (UTC-5)"])

    st.markdown("")
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">📹</span><span class="sec-txt">Camera Management</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)
    if st.button("➕ Add New Camera", use_container_width=True):
        st.info("Add camera form")

    for cam in get_cameras():
        with st.expander(f"📹 {cam['name']} (ID: #{cam['id']})"):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Name", value=cam["name"], key=f"cn{cam['id']}")
                st.text_input("RTSP URL", value=f"rtsp://192.168.1.{cam['id']}/stream", key=f"cr{cam['id']}")
            with c2:
                st.selectbox("Type", ["Dome","Bullet","PTZ"], key=f"ct{cam['id']}")
                st.selectbox("Location", ["Indoor","Outdoor"], key=f"cl{cam['id']}")
            sb1, sb2 = st.columns(2)
            with sb1:
                st.button(f"💾 Save #{cam['id']}", key=f"cs{cam['id']}", use_container_width=True)
            with sb2:
                st.button(f"🗑️ Delete #{cam['id']}", key=f"cd{cam['id']}", use_container_width=True)

    st.markdown("")
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">🔄</span><span class="sec-txt">Shift Configuration</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)
    for nm, st3, en in [("Morning","06:00–14:00",True),("Afternoon","14:00–22:00",True),("Night","22:00–06:00",True)]:
        sc1, sc2, sc3, sc4 = st.columns([2, 2, 2, 1])
        with sc1:
            st.markdown(f"<b>{nm}</b>", unsafe_allow_html=True)
        with sc2:
            st.text_input(f"Start ({nm})", value=st3.split("–")[0], key=f"ss{nm}")
        with sc3:
            st.text_input(f"End ({nm})", value=st3.split("–")[1], key=f"se{nm}")
        with sc4:
            st.toggle("Enable", value=en, key=f"se{nm}")

    st.markdown("")
    st.markdown("""
    <div class="sec-hdr"><span class="sec-icon">🛡️</span><span class="sec-txt">Safety Rules</span><span class="sec-line"></span></div>
    """, unsafe_allow_html=True)
    st.toggle("🔔 Auto-alert on Fire Detection", value=True)
    st.toggle("🔔 Auto-alert on PPE Violation", value=True)
    st.toggle("🔊 Voice Announcement on Fire", value=True)
    st.number_input("⏱ Alert Repeat Interval (minutes)", value=5, min_value=1, max_value=60)

    st.markdown("")
    sb1, sb2 = st.columns([1, 1])
    with sb1:
        if st.button("💾 Save All Settings", use_container_width=True, type="primary"):
            st.success("✅ Settings saved!")
    with sb2:
        if st.button("🔄 Restart All Services", use_container_width=True):
            with st.spinner("Restarting..."):
                time.sleep(2)
            st.success("✅ Services restarted!")

    st.markdown(f"""<div class="foot">🏭 AI24x7 Factory Edition v1.0.0 | © 2026 GOUP CONSULTANCY SERVICES LLP | FACT-001 | ACTIVE ✅ | Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}</div>""", unsafe_allow_html=True)
