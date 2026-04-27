#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Dashboard v3.0
BOLD + MULTICOLOR — Professional Design
Run: streamlit run factory/dashboard/factory_dashboard.py --server.port 5052
"""
import streamlit as st
import time
from datetime import datetime

st.set_page_config(
    page_title="AI24x7 Factory Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── BOLD MULTICOLOR CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══ BASE ══════════════════════════════════════════════════════ */
.stApp { background: #0a0d14; color: #ffffff; font-family: 'Segoe UI', system-ui, sans-serif; }
.stApp::before { content: ''; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(ellipse at 20% 0%, rgba(59,130,246,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 100%, rgba(16,185,129,0.06) 0%, transparent 60%); pointer-events: none; z-index: 0; }
* { font-weight: 700 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #111827; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #3b82f6, #10b981); border-radius: 4px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #0d1117 !important; border-right: 2px solid #1f2937 !important; }
[data-testid="stSidebarNav"] { background: #0d1117; }

/* ── TOP BRAND BAR ── */
.top-brand { background: linear-gradient(135deg, #0d1117 0%, #111827 50%, #0f172a 100%); border-bottom: 2px solid #1f2937; padding: 20px 28px; margin: -1rem -1rem 2rem -1rem; display: flex; align-items: center; justify-content: space-between; }
.brand-left { display: flex; align-items: center; gap: 14px; }
.brand-icon { font-size: 2.4rem; filter: drop-shadow(0 0 12px rgba(59,130,246,0.5)); }
.brand-text {}
.brand-title { font-size: 1.5rem !important; font-weight: 900 !important; color: #fff !important; letter-spacing: -0.03em; line-height: 1.1 !important; }
.brand-sub { font-size: 0.72rem !important; font-weight: 600 !important; color: #6b7280 !important; letter-spacing: 0.08em; text-transform: uppercase; }
.brand-right { display: flex; align-items: center; gap: 16px; }
.live-pill { background: linear-gradient(135deg, #10b981, #059669); color: white !important; padding: 6px 18px; border-radius: 30px; font-size: 0.78rem !important; font-weight: 800 !important; letter-spacing: 0.1em; text-transform: uppercase; box-shadow: 0 0 20px rgba(16,185,129,0.4); animation: glow 2s ease-in-out infinite alternate; }
@keyframes glow { from{box-shadow:0 0 10px rgba(16,185,129,0.3)} to{box-shadow:0 0 25px rgba(16,185,129,0.6)} }
.clock { font-size: 0.9rem !important; font-weight: 700 !important; color: #9ca3af !important; font-variant-numeric: tabular-nums; }

/* ── SECTION HEADERS ── */
.section-hdr { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; margin-top: 8px; }
.section-hdr-icon { font-size: 1.1rem; }
.section-hdr-text { font-size: 0.7rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.15em; color: #6b7280 !important; flex: 1; }
.section-hdr-line { height: 1px; flex: 2; background: linear-gradient(90deg, #1f2937, transparent); }

/* ── METRIC CARDS ── */
.metric-card { background: #111827; border-radius: 16px; padding: 20px 22px 18px; border: 2px solid #1f2937; position: relative; overflow: hidden; transition: all 0.3s; }
.metric-card:hover { border-color: #374151; transform: translateY(-3px); box-shadow: 0 12px 40px rgba(0,0,0,0.4); }
.metric-card::after { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0; }
.metric-card.green::after { background: linear-gradient(90deg, #10b981, #34d399, #10b981); }
.metric-card.blue::after { background: linear-gradient(90deg, #3b82f6, #60a5fa, #3b82f6); }
.metric-card.orange::after { background: linear-gradient(90deg, #f59e0b, #fbbf24, #f59e0b); }
.metric-card.red::after { background: linear-gradient(90deg, #ef4444, #f87171, #ef4444); }
.metric-card.purple::after { background: linear-gradient(90deg, #8b5cf6, #a78bfa, #8b5cf6); }
.metric-inner { display: flex; justify-content: space-between; align-items: flex-start; }
.metric-num { font-size: 2.4rem !important; font-weight: 900 !important; line-height: 1 !important; margin-bottom: 6px; letter-spacing: -0.03em; }
.metric-lbl { font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.1em; color: #6b7280 !important; }
.metric-icon { font-size: 1.8rem; opacity: 0.25; }
.metric-delta { font-size: 0.72rem !important; font-weight: 700 !important; margin-top: 6px; }
.delta-up { color: #10b981 !important; }
.delta-down { color: #ef4444 !important; }
.delta-neutral { color: #9ca3af !important; }

/* ── CAMERA CARDS ── */
.cam-card { background: #111827; border: 2px solid #1f2937; border-radius: 14px; overflow: hidden; transition: all 0.25s; }
.cam-card:hover { border-color: #374151; transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.4); }
.cam-thumb { background: linear-gradient(135deg, #0d1117, #111827); height: 110px; display: flex; align-items: center; justify-content: center; font-size: 2.8rem; position: relative; }
.cam-overlay { position: absolute; bottom: 0; left: 0; right: 0; padding: 5px 10px; background: linear-gradient(transparent, rgba(0,0,0,0.85)); display: flex; justify-content: space-between; align-items: center; }
.cam-id { font-size: 0.65rem !important; font-weight: 800 !important; color: rgba(255,255,255,0.5) !important; }
.cam-body { padding: 12px 14px; }
.cam-name { font-size: 0.9rem !important; font-weight: 800 !important; margin-bottom: 8px; color: #f9fafb !important; }
.cam-meta { display: flex; justify-content: space-between; align-items: center; }
.cam-meta span { font-size: 0.72rem !important; font-weight: 700 !important; color: #9ca3af !important; }
.cam-badge { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 0.65rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.05em; }
.cam-badge.online { background: rgba(16,185,129,0.15); color: #34d399 !important; border: 1px solid rgba(16,185,129,0.3); }
.cam-badge.warning { background: rgba(245,158,11,0.15); color: #fbbf24 !important; border: 1px solid rgba(245,158,11,0.3); }
.cam-badge.offline { background: rgba(107,114,128,0.15); color: #9ca3af !important; border: 1px solid rgba(107,114,128,0.3); }

/* ── ALERT CARDS ── */
.alert-card { background: #111827; border-radius: 12px; padding: 14px 16px; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 12px; transition: all 0.2s; border: 2px solid; }
.alert-card:hover { transform: translateX(3px); }
.alert-card.critical { border-color: rgba(239,68,68,0.4); border-left: 4px solid #ef4444; }
.alert-card.warning { border-color: rgba(245,158,11,0.4); border-left: 4px solid #f59e0b; }
.alert-card.info { border-color: rgba(59,130,246,0.4); border-left: 4px solid #3b82f6; }
.alert-card.success { border-color: rgba(16,185,129,0.4); border-left: 4px solid #10b981; }
.alert-icon { font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }
.alert-title { font-size: 0.9rem !important; font-weight: 800 !important; color: #f9fafb !important; margin-bottom: 3px; }
.alert-msg { font-size: 0.8rem !important; font-weight: 600 !important; color: #9ca3af !important; }
.alert-time { font-size: 0.72rem !important; font-weight: 700 !important; color: #6b7280 !important; margin-top: 2px; }

/* ── PROGRESS BARS ── */
.prog-row { margin-bottom: 12px; }
.prog-label { display: flex; justify-content: space-between; margin-bottom: 6px; }
.prog-label-left { font-size: 0.82rem !important; font-weight: 700 !important; color: #d1d5db !important; }
.prog-label-right { font-size: 0.82rem !important; font-weight: 900 !important; }
.prog-track { height: 8px; background: #1f2937; border-radius: 4px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 4px; transition: width 1.2s cubic-bezier(0.4,0,0.2,1); }

/* ── INFO CARDS ── */
.info-card { background: #111827; border: 2px solid #1f2937; border-radius: 14px; padding: 18px; }
.info-card-title { font-size: 1rem !important; font-weight: 900 !important; color: #f9fafb !important; margin-bottom: 10px; }

/* ── TABLES ── */
.stTable { background: #111827 !important; border-radius: 12px !important; overflow: hidden !important; border: 2px solid #1f2937 !important; }
[data-testid="stTable"] table { width: 100%; border-collapse: collapse; }
[data-testid="stTable"] th { background: #0d1117 !important; font-size: 0.68rem !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; color: #6b7280 !important; padding: 12px 16px !important; border-bottom: 2px solid #1f2937 !important; }
[data-testid="stTable"] td { font-size: 0.85rem !important; font-weight: 700 !important; color: #e5e7eb !important; padding: 12px 16px !important; border-bottom: 1px solid #1a1d2e !important; }
[data-testid="stTable"] tr:last-child td { border-bottom: none !important; }
[data-testid="stTable"] tr:hover td { background: #1a2332 !important; }

/* ── EXPANDER / DETAILS ── */
.streamlit-expanderHeader { background: #111827 !important; border: 2px solid #1f2937 !important; border-radius: 10px !important; font-size: 0.88rem !important; font-weight: 800 !important; }
.streamlit-expanderContent { background: #0d1117 !important; border: 2px solid #1f2937 !important; border-top: none !important; border-radius: 0 0 10px 10px !important; }

/* ── BUTTONS ── */
.stButton > button { border-radius: 10px !important; font-weight: 800 !important; font-size: 0.82rem !important; transition: all 0.2s !important; border: 2px solid !important; padding: 0.4rem 1rem !important; }
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; }

/* ── TOGGLES ── */
.switch { position: relative; display: inline-block; width: 44px; height: 24px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #1f2937; transition: .3s; border-radius: 24px; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }

/* ── DIVIDER ── */
hr { border: none; border-top: 2px solid #1f2937 !important; margin: 1.2rem 0 !important; }

/* ── COLUMNS GAP ── */
[data-testid="stHorizontalBlock"] > div { gap: 12px !important; }

/* ── NAVIGATION PILLS ── */
.nav-pill { display: inline-flex; align-items: center; gap: 6px; background: #1a1d2e; border: 2px solid #2d3555; border-radius: 10px; padding: 10px 18px; font-size: 0.85rem !important; font-weight: 800 !important; transition: all 0.2s; cursor: pointer; }
.nav-pill:hover, .nav-pill.active { background: linear-gradient(135deg, #1e3a5f, #1a2332); border-color: #3b82f6; color: #60a5fa !important; }

/* ── FOOTER ── */
.footer-txt { text-align: center; font-size: 0.7rem !important; font-weight: 600 !important; color: #374151 !important; padding: 20px 0; }

/* ── STATUS DOTS ── */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.dot-green { background: #10b981; box-shadow: 0 0 6px rgba(16,185,129,0.5); }
.dot-yellow { background: #f59e0b; box-shadow: 0 0 6px rgba(245,158,11,0.5); }
.dot-red { background: #ef4444; box-shadow: 0 0 6px rgba(239,68,68,0.5); }
.dot-gray { background: #6b7280; }
.status-txt { font-size: 0.8rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.05em; }
.txt-green { color: #10b981 !important; }
.txt-yellow { color: #f59e0b !important; }
.txt-red { color: #ef4444 !important; }
.txt-blue { color: #3b82f6 !important; }
.txt-gray { color: #9ca3af !important; }
.txt-white { color: #f9fafb !important; }
.txt-bold { font-weight: 900 !important; }

/* ── SHIFT BADGE ── */
.shift-badge { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #1e3a5f, #1a2332); border: 2px solid #3b82f6; border-radius: 10px; padding: 8px 16px; font-size: 0.88rem !important; font-weight: 900 !important; box-shadow: 0 0 15px rgba(59,130,246,0.2); }

/* ── SCORE BIG ── */
.score-big { background: linear-gradient(135deg, #064e3b, #065f46, #10b981); border-radius: 16px; padding: 24px; text-align: center; border: 2px solid #059669; }
.score-big-num { font-size: 3rem !important; font-weight: 900 !important; color: #fff !important; line-height: 1 !important; text-shadow: 0 0 20px rgba(16,185,129,0.5); }

/* ── EQUIP ROW ── */
.equip-row { display: flex; align-items: center; padding: 10px 0; border-bottom: 1px solid #1a1d2e; }
.equip-row:last-child { border-bottom: none; }
.equip-name { font-size: 0.88rem !important; font-weight: 800 !important; flex: 1; }
.equip-status { font-size: 0.75rem !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 0.05em; }
.equip-bar { flex: 2; margin: 0 12px; }

/* ── BIG CALLOUT ── */
.callout { background: linear-gradient(135deg, #1e3a5f, #0f172a); border: 2px solid #3b82f6; border-radius: 14px; padding: 20px; text-align: center; }
.callout-num { font-size: 2.5rem !important; font-weight: 900 !important; color: #fff !important; }
.callout-lbl { font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.1em; color: #60a5fa !important; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────

def get_stats():
    return {
        "workers": 47, "ppe": 91, "alerts": 12, "critical": 1,
        "cam_online": 5, "cam_total": 6, "fire_risk": "Low",
        "uptime": 97.3, "shift": "Morning",
    }

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
        {"type":"critical","icon":"🔥","title":"Fire Detected!","msg":"Assembly Area — confidence 94%","time":"5 min ago"},
        {"type":"warning","icon":"🪖","title":"PPE Violation","msg":"Paint Shop — No helmet detected","time":"12 min ago"},
        {"type":"info","icon":"🚗","title":"Unknown Vehicle","msg":"Gate 1 — Unrecognized vehicle at gate","time":"23 min ago"},
        {"type":"warning","icon":"🛢️","title":"Spill Detected","msg":"Machine Hall A — Oil spill near Machine B","time":"45 min ago"},
        {"type":"success","icon":"🔄","title":"Shift Changed","msg":"Now: Afternoon Shift — 14:00 to 22:00","time":"1 hour ago"},
    ]

def get_safety_scores():
    return [
        ("🔥 Fire Safety", 95, "#10b981"),
        ("🪖 PPE Compliance", 91, "#10b981"),
        ("⚙️ Equipment", 97, "#10b981"),
        ("🛢️ Spill Control", 78, "#f59e0b"),
        ("🏗️ Hazard Zone", 92, "#10b981"),
    ]

def get_equipment():
    return [
        ("Conveyor A", "Running", 98, True),
        ("Conveyor B", "Running", 95, True),
        ("Robot Arm 1", "Running", 100, True),
        ("CNC Machine", "Maintenance", 0, False),
        ("Furnace 1", "Running", 92, True),
        ("Compressor", "Running", 88, True),
    ]

# ─── TOP BRAND BAR ─────────────────────────────────────────────────────────
col_b1, col_b2, col_b3 = st.columns([1, 4, 2])

with col_b1:
    st.markdown("🏭", unsafe_allow_html=False)

with col_b2:
    st.markdown("""
    <div class="brand-text">
        <div class="brand-title">AI24x7 Factory Edition</div>
        <div class="brand-sub">Industrial AI Surveillance System — v1.0</div>
    </div>
    """, unsafe_allow_html=True)

with col_b3:
    now = datetime.now()
    st.markdown(f"""
    <div class="brand-right">
        <span class="live-pill">● LIVE</span>
        <span class="clock">{now.strftime('%d %b %Y · %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""<hr style="margin: 0.5rem 0 1.5rem;">""", unsafe_allow_html=True)

# ─── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 Navigation", unsafe_allow_html=False)
    
    stats = get_stats()
    
    # Shift badge
    st.markdown(f"""
    <div class="shift-badge" style="width:100%; justify-content:center;">
        ⏰ <span class="txt-blue">Morning Shift</span> · 06:00–14:00
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    nav = st.radio("Go to", [
        "📊 Overview",
        "📹 Camera Feeds",
        "🔥 Safety Alerts",
        "🪖 PPE Compliance",
        "🔄 Shift Reports",
        "⚙️ Equipment",
        "📱 Notifications",
        "⚙️ Settings",
    ], label_visibility="collapsed")
    
    st.markdown("""<hr>""", unsafe_allow_html=True)
    st.markdown("""<div class="section-hdr-text" style="margin-bottom:10px;">⚡ Quick Stats</div>""", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Workers", stats["workers"])
        st.metric("PPE", f"{stats['ppe']}%")
    with c2:
        st.metric("Alerts", stats["alerts"])
        st.metric("Uptime", f"{stats['uptime']}%")
    
    st.markdown("""<hr><div class="section-hdr-text" style="margin-bottom:8px;">📹 Cameras</div>""", unsafe_allow_html=True)
    
    for cam in get_cameras():
        dot = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "⚫"
        tc = "txt-green" if cam["status"]=="online" else "txt-yellow" if cam["status"]=="warning" else "txt-gray"
        st.markdown(f"{dot} <span class='{tc}' style='font-size:0.8rem !important;'>{cam['name']}</span>", unsafe_allow_html=True)
    
    st.markdown("")
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
if nav == "📊 Overview":
    stats = get_stats()
    
    # ── Top Metric Cards
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📊</span><span class="section-hdr-text">Key Metrics</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div class="metric-card green">
            <div class="metric-inner">
                <div>
                    <div class="metric-num txt-green">47</div>
                    <div class="metric-lbl">Active Workers</div>
                    <div class="metric-delta delta-up">▲ +3 from yesterday</div>
                </div>
                <div class="metric-icon">👷</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="metric-card blue">
            <div class="metric-inner">
                <div>
                    <div class="metric-num txt-blue">91%</div>
                    <div class="metric-lbl">PPE Compliance</div>
                    <div class="metric-delta delta-up">▲ +2% this week</div>
                </div>
                <div class="metric-icon">🪖</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="metric-card orange">
            <div class="metric-inner">
                <div>
                    <div class="metric-num txt-yellow">12</div>
                    <div class="metric-lbl">Alerts Today</div>
                    <div class="metric-delta delta-down">▲ 3 critical</div>
                </div>
                <div class="metric-icon">🔔</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="metric-card green">
            <div class="metric-inner">
                <div>
                    <div class="metric-num txt-green">🟢 Low</div>
                    <div class="metric-lbl">Fire Risk Level</div>
                    <div class="metric-delta delta-up">All sensors OK</div>
                </div>
                <div class="metric-icon">🔥</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Camera Grid + Alerts
    col_grid, col_alerts = st.columns([2, 1])
    
    with col_grid:
        st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📹</span><span class="section-hdr-text">Camera Grid</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
        
        cams = get_cameras()
        rows = [cams[i:i+3] for i in range(0, len(cams), 3)]
        for r in rows:
            cols_c = st.columns(3)
            for idx, cam in enumerate(r):
                with cols_c[idx]:
                    dot_icon = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
                    badge_cls = "online" if cam["status"]=="online" else "warning" if cam["status"]=="warning" else "offline"
                    ppc = "#10b981" if cam["ppe"]>=90 else "#f59e0b" if cam["ppe"]>=75 else "#ef4444"
                    
                    st.markdown(f"""
                    <div class="cam-card">
                        <div class="cam-thumb">
                            📹
                            <div class="cam-overlay">
                                <span class="cam-id">#{cam['id']:02d}</span>
                                <span class="cam-badge {badge_cls}">{dot_icon} {cam['status'].upper()}</span>
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
    
    with col_alerts:
        st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">🚨</span><span class="section-hdr-text">Live Alerts</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
        
        for a in get_alerts():
            icon_map = {"critical":"🔥","warning":"🪖","info":"🚗","success":"✅"}
            icon = icon_map.get(a["type"], "⚠️")
            type_cls = a["type"]
            
            st.markdown(f"""
            <div class="alert-card {type_cls}">
                <div class="alert-icon">{icon}</div>
                <div>
                    <div class="alert-title">{a['title']}</div>
                    <div class="alert-msg">{a['msg']}</div>
                    <div class="alert-time">⏱ {a['time']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Safety Score + Equipment
    col_safety, col_equip = st.columns([1, 1])
    
    with col_safety:
        st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">🏆</span><span class="section-hdr-text">Safety Score</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
        
        for name, score, color in get_safety_scores():
            st.markdown(f"""
            <div class="prog-row">
                <div class="prog-label">
                    <span class="prog-label-left">{name}</span>
                    <span class="prog-label-right" style="color:{color} !important;">{score}%</span>
                </div>
                <div class="prog-track">
                    <div class="prog-fill" style="width:{score}%; background:linear-gradient(90deg,{color},transparent);"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("""
        <div class="score-big">
            <div class="score-big-num">87<span style="font-size:1.5rem !important;">/100</span></div>
            <div class="callout-lbl">Overall Safety Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_equip:
        st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">⚙️</span><span class="section-hdr-text">Equipment Status</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
        """, unsafe_allow_html=True)
        
        for name, status, uptime, ok in get_equipment():
            dot_cls = "dot-green" if ok else "dot-red"
            status_cls = "txt-green" if ok else "txt-red"
            bar_color = "#10b981" if ok else "#ef4444"
            bar_w = uptime if ok else 100
            
            st.markdown(f"""
            <div class="equip-row">
                <span class="equip-name">{'🟢' if ok else '🔴'} {name}</span>
                <div class="equip-bar">
                    <div class="prog-track" style="height:6px;">
                        <div class="prog-fill" style="width:{bar_w}%; background:{bar_color};"></div>
                    </div>
                </div>
                <span class="equip-status {status_cls}">{uptime if ok else 'DOWN'}%</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Quick Actions
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">⚡</span><span class="section-hdr-text">Quick Actions</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
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
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    with qa4:
        if st.button("🚨 Test Alert", use_container_width=True):
            st.warning("🚨 Test alert sent to Telegram!")

# ─── QUICK ACTION: Footer ───────────────────────────────────────────────
    st.markdown(f"""
    <hr>
    <div class="footer-txt">
        AI24x7 Factory Edition v1.0.0 &nbsp;|&nbsp; © 2026 GOUP CONSULTANCY SERVICES LLP
        &nbsp;|&nbsp; Factory ID: FACT-001 &nbsp;|&nbsp; License: ACTIVE
        &nbsp;|&nbsp; Last Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: CAMERA FEEDS
# ════════════════════════════════════════════════════════════════════════════
elif nav == "📹 Camera Feeds":
    st.title("📹 Live Camera Feeds")
    
    cameras = get_cameras()
    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
    fs = col_f1.selectbox("Filter Status", ["All", "Online", "Warning", "Offline"])
    fc = col_f2.selectbox("Camera", ["All"] + [c["name"] for c in cameras])
    vm = col_f3.selectbox("View Mode", ["Grid", "List"])
    
    filtered = cameras
    if fs != "All":
        filtered = [c for c in filtered if c["status"].lower() == fs.lower()]
    if fc != "All":
        filtered = [c for c in filtered if c["name"] == fc]
    
    if vm == "Grid":
        rows2 = [filtered[i:i+3] for i in range(0, len(filtered), 3)]
        for row3 in rows2:
            cols_g = st.columns(3)
            for idx3, cam in enumerate(row3):
                with cols_g[idx3]:
                    badge_cls = "online" if cam["status"]=="online" else "warning" if cam["status"]=="warning" else "offline"
                    dot_icon = "🟢" if cam["status"]=="online" else "🟡" if cam["status"]=="warning" else "🔴"
                    ppc = "#10b981" if cam["ppe"]>=90 else "#f59e0b" if cam["ppe"]>=75 else "#ef4444"
                    
                    st.markdown(f"""
                    <div class="cam-card">
                        <div class="cam-thumb" style="height:150px; font-size:3.5rem;">
                            📹
                            <div style="position:absolute; top:8px; right:8px;">
                                <span class="cam-badge {badge_cls}">{dot_icon} {cam['status'].upper()}</span>
                            </div>
                            <div style="position:absolute; bottom:8px; left:8px;">
                                <span class="cam-id">CAM {cam['id']:02d}</span>
                            </div>
                        </div>
                        <div class="cam-body">
                            <div class="cam-name">{cam['name']}</div>
                            <div class="cam-meta" style="margin-top:8px;">
                                <span>👥 {cam['persons']} workers</span>
                                <span style="color:{ppc}; font-weight:900 !important;">PPE {cam['ppe']}%</span>
                                <span>{cam['last']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        st.button(f"📸 Snapshot #{cam['id']}", key=f"sn_{cam['id']}", use_container_width=True)
                    with b2:
                        st.button(f"📊 Analytics #{cam['id']}", key=f"an_{cam['id']}", use_container_width=True)
    else:
        # List view
        import pandas as pd
        df = pd.DataFrame(filtered)
        df.columns = ["ID", "Camera Name", "Status", "Workers", "PPE %", "Last Alert"]
        st.table(df)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SAFETY ALERTS
# ════════════════════════════════════════════════════════════════════════════
elif nav == "🔥 Safety Alerts":
    st.title("🔥 Safety Alert Center")
    
    a1, a2, a3 = st.columns(3)
    a1.metric("🔴 Total Alerts", 12, delta=3)
    a2.metric("🚨 Critical", 1, delta_color="inverse")
    a3.metric("✅ Resolved", 9)
    
    st.markdown("")
    
    ft = st.selectbox("Filter by Type", ["All", "Fire", "PPE", "Spill", "Entry", "Equipment"])
    fstat = st.selectbox("Status", ["All", "Unhandled", "Handled"])
    
    for a in get_alerts():
        if ft != "All" and ft.lower() not in a["title"].lower():
            continue
        icon_map = {"critical":"🔥","warning":"🪖","info":"🚗","success":"✅"}
        type_cls = a["type"]
        st.markdown(f"""
        <div class="alert-card {type_cls}">
            <div class="alert-icon">{icon_map.get(a['type'],'⚠️')}</div>
            <div>
                <div class="alert-title">{a['title']}</div>
                <div class="alert-msg">{a['msg']}</div>
                <div class="alert-time">⏱ {a['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cb1, cb2 = st.columns(2)
        with cb1:
            st.button(f"✅ Acknowledge: {a['title']}", key=f"ack_{a['title']}", use_container_width=True)
        with cb2:
            st.button(f"📞 Escalate: {a['title']}", key=f"esc_{a['title']}", use_container_width=True)
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📊</span><span class="section-hdr-text">Alert History — Last 7 Days</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fire_vals = [2, 1, 0, 3, 1, 0, 1]
    ppe_vals = [5, 3, 4, 2, 6, 1, 2]
    st.bar_chart({"🔥 Fire": fire_vals, "🪖 PPE": ppe_vals}, height=200)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: PPE COMPLIANCE
# ════════════════════════════════════════════════════════════════════════════
elif nav == "🪖 PPE Compliance":
    st.title("🪖 PPE Compliance Dashboard")
    
    # Big overall score
    st.markdown("""
    <div style="background: linear-gradient(135deg, #064e3b, #059669, #10b981); border-radius: 20px; padding: 32px; text-align: center; margin-bottom: 24px; border: 2px solid #059669; box-shadow: 0 8px 40px rgba(16,185,129,0.2);">
        <div style="font-size: 4rem !important; font-weight: 900 !important; color: #fff !important; line-height: 1 !important; text-shadow: 0 0 30px rgba(16,185,129,0.5);">91%</div>
        <div style="font-size: 1rem !important; font-weight: 700 !important; color: rgba(255,255,255,0.85) !important; margin-top: 8px;">Overall PPE Compliance</div>
        <div style="font-size: 0.8rem !important; font-weight: 700 !important; color: rgba(255,255,255,0.6) !important; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em;">Target: 95%</div>
    </div>
    """, unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("🪖 Helmet", "96%", delta=2)
    p2.metric("🦺 Safety Vest", "94%", delta=1)
    p3.metric("🧤 Gloves", "82%", delta=-5)
    p4.metric("👢 Safety Shoes", "88%", delta=-2)
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📹</span><span class="section-hdr-text">Camera-wise PPE Score</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    for cam in get_cameras():
        score = cam["ppe"]
        color = "#10b981" if score >= 90 else "#f59e0b" if score >= 75 else "#ef4444"
        
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:16px; margin-bottom:12px; background:#111827; border:2px solid #1f2937; border-radius:10px; padding:12px 16px;">
            <div style="min-width:120px;">
                <span style="font-size:0.88rem !important; font-weight:900 !important;">{cam['name']}</span>
            </div>
            <div style="flex:1;">
                <div class="prog-track" style="height:10px;">
                    <div class="prog-fill" style="width:{score}%; background:linear-gradient(90deg,{color},rgba(255,255,255,0.3));"></div>
                </div>
            </div>
            <div style="min-width:60px; text-align:right;">
                <span style="font-size:1rem !important; font-weight:900 !important; color:{color};">{score}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">⚠️</span><span class="section-hdr-text">Recent Violations</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    violations = [
        ("🪖 No Helmet Detected", "Paint Shop", "Ramesh Kumar", "12 min ago"),
        ("🦺 No Safety Vest", "Assembly Area", "Unknown Worker", "28 min ago"),
        ("🧤 No Gloves", "Machine Hall A", "Suresh Patil", "45 min ago"),
        ("👢 Improper Shoes", "Gate 1", "Labour 007", "1 hour ago"),
    ]
    
    for vtype, cam, person, t in violations:
        st.markdown(f"""
        <div class="alert-card warning">
            <div class="alert-icon">{vtype.split()[0]}</div>
            <div>
                <div class="alert-title">{vtype}</div>
                <div class="alert-msg">{cam} • {person}</div>
                <div class="alert-time">⏱ {t}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("📋 Export PPE Report", use_container_width=True, type="primary"):
        st.success("✅ PPE Report exported!")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SHIFT REPORTS
# ════════════════════════════════════════════════════════════════════════════
elif nav == "🔄 Shift Reports":
    st.title("🔄 Shift Reports")
    
    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        st.markdown("""
        <div class="info-card" style="text-align:center;">
            <div style="font-size:1.5rem !important; font-weight:900 !important; color:#3b82f6 !important;">⏰ Morning Shift</div>
            <div style="font-size:0.85rem !important; font-weight:700 !important; color:#6b7280 !important; margin-top:4px;">06:00 — 14:00</div>
            <div style="font-size:0.82rem !important; font-weight:700 !important; color:#9ca3af !important; margin-top:6px;">50% Complete</div>
            <div class="prog-track" style="margin-top:12px; height:10px;">
                <div class="prog-fill" style="width:50%; background:linear-gradient(90deg,#3b82f6,#60a5fa);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_s2:
        st.selectbox("Select Shift Report", [
            "Morning Shift — 27 Apr 2026",
            "Afternoon Shift — 26 Apr 2026",
            "Night Shift — 26 Apr 2026",
        ])
    
    st.markdown("")
    
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("👷 Total Workers", 47)
    s2.metric("🪖 PPE Violations", 3)
    s3.metric("🚨 Incidents", 0)
    s4.metric("⚙️ Downtime", "0.5h")
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📋</span><span class="section-hdr-text">Shift Metrics Table</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    import pandas as pd
    shift_df = pd.DataFrame({
        "Metric": ["Total Workers", "PPE Violations", "Fire Alarms", "Unauthorized Entry", "Spill Incidents", "Equipment Downtime"],
        "Value": [47, 3, 0, 1, 1, "0.5 hours"],
    })
    st.table(shift_df)
    
    b1, b2, b3 = st.columns(3)
    with b1:
        st.button("📄 Generate PDF Report", use_container_width=True)
    with b2:
        st.button("📤 Export CSV", use_container_width=True)
    with b3:
        st.button("📧 Email to Manager", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: EQUIPMENT
# ════════════════════════════════════════════════════════════════════════════
elif nav == "⚙️ Equipment":
    st.title("⚙️ Equipment Monitoring")
    
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("🔧 Total Machines", 7)
    e2.metric("🟢 Running", 6)
    e3.metric("🔴 Maintenance", 1)
    e4.metric("📈 Avg Uptime", "94%")
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📋</span><span class="section-hdr-text">All Equipment</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    equip_data = [
        ("Conveyor A", "Running", 98, True, "8h 23m"),
        ("Conveyor B", "Running", 95, True, "6h 45m"),
        ("Robot Arm 1", "Running", 100, True, "12h 00m"),
        ("CNC Machine", "Maintenance", 0, False, "0h 30m"),
        ("Furnace 1", "Running", 92, True, "8h 10m"),
        ("Compressor", "Running", 88, True, "5h 15m"),
        ("Hydraulic Press", "Stopped", 0, False, "3h 00m"),
        ("AGV Robot", "Running", 96, True, "4h 50m"),
    ]
    
    for name, status, uptime, ok, runtime in equip_data:
        bar_color = "#10b981" if ok else "#ef4444"
        bar_w = uptime if ok else 100
        dot = "🟢" if ok else "🔴"
        status_cls = "txt-green" if ok else "txt-red"
        status_txt = "RUNNING" if ok else "MAINTENANCE"
        
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:16px; background:#111827; border:2px solid #1f2937; border-radius:10px; padding:12px 16px; margin-bottom:8px;">
            <div style="min-width:140px;">
                <span style="font-size:0.92rem !important; font-weight:900 !important;">{dot} {name}</span>
            </div>
            <div style="min-width:100px;">
                <span class="{status_cls}" style="font-size:0.75rem !important; font-weight:800 !important;">{status_txt}</span>
            </div>
            <div style="flex:1;">
                <div class="prog-track" style="height:8px;">
                    <div class="prog-fill" style="width:{bar_w}%; background:{bar_color};"></div>
                </div>
            </div>
            <div style="min-width:60px; text-align:right;">
                <span style="font-size:0.85rem !important; font-weight:900 !important; color:{bar_color};">{uptime}%</span>
            </div>
            <div style="min-width:70px; text-align:right;">
                <span style="font-size:0.75rem !important; font-weight:700 !important; color:#6b7280 !important;">{runtime}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: NOTIFICATIONS
# ════════════════════════════════════════════════════════════════════════════
elif nav == "📱 Notifications":
    st.title("📱 Notification Settings")
    
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📱</span><span class="section-hdr-text">Alert Channels</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    # Telegram
    st.markdown("""
    <div class="info-card" style="margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
            <span style="font-size:1.5rem;">📨</span>
            <span style="font-size:1rem !important; font-weight:900 !important;">Telegram Alerts</span>
        </div>
    """, unsafe_allow_html=True)
    tg_en = st.toggle("Enable Telegram Alerts", value=True, key="tg_toggle")
    if tg_en:
        st.text_input("Bot Token", value="8751634203:AAEtay1...", disabled=True, key="tg_token")
        st.text_input("Chat ID", value="8566322083", key="tg_chat")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # SMS
    st.markdown("""
    <div class="info-card" style="margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
            <span style="font-size:1.5rem;">📞</span>
            <span style="font-size:1rem !important; font-weight:900 !important;">SMS Alerts</span>
        </div>
    """, unsafe_allow_html=True)
    sms_en = st.toggle("Enable SMS Alerts", value=False, key="sms_toggle")
    if sms_en:
        st.text_input("SMS API Key", type="password", key="sms_key")
        st.text_input("Recipients", value="+91-98XXXXXXX", key="sms_recip")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # WhatsApp
    st.markdown("""
    <div class="info-card" style="margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
            <span style="font-size:1.5rem;">💬</span>
            <span style="font-size:1rem !important; font-weight:900 !important;">WhatsApp Business</span>
        </div>
    """, unsafe_allow_html=True)
    wa_en = st.toggle("Enable WhatsApp", value=False, key="wa_toggle")
    if wa_en:
        st.text_input("WhatsApp Business Number", key="wa_num")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📋</span><span class="section-hdr-text">Alert Rules</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    rules = [
        ("🔥 Fire Detected", True, "All Channels", "Critical"),
        ("🪖 PPE Violation", True, "All Channels", "Warning"),
        ("🚗 Unauthorized Entry", True, "Telegram", "Warning"),
        ("🛢️ Spill Detected", True, "All Channels", "Critical"),
        ("⚙️ Equipment Down", False, "Admin Only", "Info"),
        ("🔄 Shift Change", True, "Telegram", "Info"),
    ]
    
    for i, (name, en, send, sev) in enumerate(rules):
        col_r1, col_r2, col_r3, col_r4 = st.columns([3, 1, 1, 1])
        with col_r1:
            st.markdown(f"<b>{name}</b>", unsafe_allow_html=True)
        with col_r2:
            st.toggle("Enable", value=en, key=f"rule_en_{i}")
        with col_r3:
            st.markdown(f"<span style='font-size:0.75rem !important; font-weight:700 !important; color:#60a5fa;'>{send}</span>", unsafe_allow_html=True)
        with col_r4:
            colors = {"Critical":"#ef4444","Warning":"#f59e0b","Info":"#3b82f6"}
            st.markdown(f"<span style='color:{colors[sev]} !important; font-weight:900 !important; font-size:0.82rem;'>{sev}</span>", unsafe_allow_html=True)
    
    st.markdown("")
    if st.button("💾 Save Notification Settings", use_container_width=True, type="primary"):
        st.success("✅ Settings saved successfully!")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ════════════════════════════════════════════════════════════════════════════
elif nav == "⚙️ Settings":
    st.title("⚙️ System Settings")
    
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">🏭</span><span class="section-hdr-text">Factory Configuration</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    s1, s2 = st.columns(2)
    with s1:
        factory_name = st.text_input("🏭 Factory Name", value="Alpha Industries - Unit 1")
        st.text_input("🔖 Factory ID", value="FACT-001")
        st.text_input("🔑 License Key", value="FACTORY-XXXX-XXXX-XXXX-XXXX", disabled=True)
    with s2:
        st.selectbox("🌐 Language", ["English", "Hindi", "Hindi + English"])
        st.selectbox("🕐 Time Zone", ["IST (UTC+5:30)", "UTC", "EST (UTC-5)"])
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">📹</span><span class="section-hdr-text">Camera Management</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    if st.button("➕ Add New Camera", use_container_width=True):
        st.info("Add camera form would appear here")
    
    for cam in get_cameras():
        with st.expander(f"📹 {cam['name']} (ID: #{cam['id']})"):
            st.text_input("Camera Name", value=cam["name"], key=f"cname_{cam['id']}")
            st.text_input("RTSP URL", value=f"rtsp://192.168.1.{cam['id']}/stream", key=f"crtsp_{cam['id']}")
            cc1, cc2 = st.columns(2)
            with cc1:
                st.selectbox("Type", ["Dome", "Bullet", "PTZ"], key=f"ctype_{cam['id']}")
            with cc2:
                st.selectbox("Location", ["Indoor", "Outdoor"], key=f"cloc_{cam['id']}")
            cs1, cs2 = st.columns(2)
            with cs1:
                st.button(f"💾 Save #{cam['id']}", key=f"csave_{cam['id']}", use_container_width=True)
            with cs2:
                st.button(f"🗑️ Delete #{cam['id']}", key=f"cdel_{cam['id']}", use_container_width=True)
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">🔄</span><span class="section-hdr-text">Shift Configuration</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    for name, start, end in [("Morning","06:00","14:00"),("Afternoon","14:00","22:00"),("Night","22:00","06:00")]:
        ss1, ss2, ss3, ss4 = st.columns([2, 2, 2, 1])
        with ss1:
            st.markdown(f"<b>{name}</b>", unsafe_allow_html=True)
        with ss2:
            st.text_input(f"Start", value=start, key=f"st_start_{name}")
        with ss3:
            st.text_input(f"End", value=end, key=f"st_end_{name}")
        with ss4:
            st.toggle("Enable", value=True, key=f"st_en_{name}")
    
    st.markdown("")
    st.markdown("""<div class="section-hdr"><span class="section-hdr-icon">🛡️</span><span class="section-hdr-text">Safety Rules</span><span class="section-hdr-line"></span></div>""", unsafe_allow_html=True)
    
    st.toggle("🔔 Auto-alert on Fire Detection", value=True)
    st.toggle("🔔 Auto-alert on PPE Violation", value=True)
    st.toggle("🔊 Voice Announcement on Fire", value=True)
    st.number_input("⏱ Alert Repeat Interval (minutes)", value=5, min_value=1, max_value=60)
    
    st.markdown("")
    
    sc1, sc2 = st.columns([1, 1])
    with sc1:
        if st.button("💾 Save All Settings", use_container_width=True, type="primary"):
            st.success("✅ Settings saved!")
    with sc2:
        if st.button("🔄 Restart All Services", use_container_width=True):
            with st.spinner("Restarting services..."):
                time.sleep(2)
            st.success("✅ Services restarted!")
    
    st.markdown("")
    st.markdown(f"""
    <hr>
    <div class="footer-txt">
        🏭 AI24x7 Factory Edition v1.0.0
        &nbsp;|&nbsp; © 2026 GOUP CONSULTANCY SERVICES LLP
        <br>
        Factory ID: FACT-001 &nbsp;|&nbsp; License: ACTIVE ✅
        &nbsp;|&nbsp; Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}
    </div>
    """, unsafe_allow_html=True)
