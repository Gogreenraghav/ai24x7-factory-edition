#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Professional Dashboard v2.0
Clean, modern, human-designed look
Run: streamlit run factory/dashboard/factory_dashboard.py --server.port 5052
"""
import streamlit as st
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# ─── Page Config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI24x7 Factory Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS - Professional Design System ─────────────────────────────
st.markdown("""
<style>
    /* ── Reset & Base ── */
    .stApp { background: #0f1117; color: #e8eaf0; }
    
    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1a1d2e; }
    ::-webkit-scrollbar-thumb { background: #3d4255; border-radius: 3px; }
    
    /* ── Header Bar ── */
    .top-bar {
        background: linear-gradient(135deg, #1a1d2e 0%, #0f1117 100%);
        border-bottom: 1px solid #2a2f45;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -1rem -1rem 1.5rem -1rem;
    }
    .brand { display: flex; align-items: center; gap: 12px; }
    .brand-icon { font-size: 1.8rem; }
    .brand-name { font-size: 1.3rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
    .brand-sub { font-size: 0.72rem; color: #6b7280; font-weight: 400; }
    .live-badge {
        background: #10b981; color: white; padding: 4px 12px; border-radius: 20px;
        font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
    
    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #13151f;
        border-right: 1px solid #1f2335;
        padding: 0;
    }
    .sidebar-section {
        padding: 12px 16px;
        border-bottom: 1px solid #1f2335;
    }
    .sidebar-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #4b5563;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* ── Metric Cards ── */
    .metric-wrap {
        background: #161a26;
        border: 1px solid #1f2438;
        border-radius: 14px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.2s;
    }
    .metric-wrap:hover { border-color: #2d3555; transform: translateY(-1px); }
    .metric-wrap::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        border-radius: 14px 14px 0 0;
    }
    .metric-wrap.green::before { background: linear-gradient(90deg, #10b981, #059669); }
    .metric-wrap.blue::before { background: linear-gradient(90deg, #3b82f6, #2563eb); }
    .metric-wrap.orange::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .metric-wrap.red::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .metric-wrap.purple::before { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
    
    .metric-number {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 4px;
        font-variant-numeric: tabular-nums;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-icon {
        position: absolute;
        top: 14px;
        right: 16px;
        font-size: 1.4rem;
        opacity: 0.3;
    }
    .metric-delta {
        font-size: 0.72rem;
        margin-top: 4px;
    }
    .metric-delta.up { color: #10b981; }
    .metric-delta.down { color: #ef4444; }
    
    /* ── Status Indicators ── */
    .status-dot { display: inline-flex; align-items: center; gap: 5px; font-size: 0.78rem; }
    .status-dot::before { content: ''; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
    .status-online { color: #10b981; }
    .status-warning { color: #f59e0b; }
    .status-offline { color: #6b7280; }
    
    /* ── Alert Cards ── */
    .alert-card {
        background: #161a26;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 8px;
        border-left: 3px solid;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .alert-card.critical { border-color: #ef4444; }
    .alert-card.warning { border-color: #f59e0b; }
    .alert-card.info { border-color: #3b82f6; }
    .alert-card.success { border-color: #10b981; }
    .alert-icon { font-size: 1.2rem; flex-shrink: 0; }
    .alert-body { flex: 1; }
    .alert-title { font-weight: 600; font-size: 0.88rem; margin-bottom: 2px; }
    .alert-meta { font-size: 0.72rem; color: #6b7280; }
    
    /* ── Camera Cards ── */
    .cam-card {
        background: #161a26;
        border: 1px solid #1f2438;
        border-radius: 14px;
        overflow: hidden;
        transition: all 0.2s;
    }
    .cam-card:hover { border-color: #2d3555; }
    .cam-thumb {
        background: linear-gradient(135deg, #0d0f18, #161a26);
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        position: relative;
    }
    .cam-thumb .cam-overlay {
        position: absolute;
        bottom: 6px; left: 8px;
        background: rgba(0,0,0,0.7);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.68rem;
    }
    .cam-body { padding: 12px; }
    .cam-name { font-weight: 600; font-size: 0.88rem; margin-bottom: 4px; }
    .cam-meta { display: flex; justify-content: space-between; align-items: center; }
    .cam-meta span { font-size: 0.72rem; color: #6b7280; }
    
    /* ── Progress Bars ── */
    .progress-row { margin-bottom: 10px; }
    .progress-label { display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 5px; }
    .progress-label span:first-child { color: #9ca3af; }
    .progress-label span:last-child { font-weight: 600; color: #e5e7eb; }
    .progress-track { height: 6px; background: #1f2438; border-radius: 3px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }
    
    /* ── Section Headers ── */
    .section-title {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #4b5563;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: #1f2438;
    }
    
    /* ── Info Cards ── */
    .info-card {
        background: #161a26;
        border: 1px solid #1f2438;
        border-radius: 12px;
        padding: 16px;
    }
    .info-card-title { font-weight: 600; font-size: 0.9rem; margin-bottom: 12px; }
    
    /* ── Shift Badge ── */
    .shift-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #1a2332;
        border: 1px solid #2d3555;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    
    /* ── Table rows ── */
    .data-table { width: 100%; border-collapse: collapse; }
    .data-table th {
        text-align: left;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #4b5563;
        padding: 8px 12px;
        border-bottom: 1px solid #1f2438;
        font-weight: 600;
    }
    .data-table td {
        padding: 10px 12px;
        font-size: 0.84rem;
        border-bottom: 1px solid #1a1d2e;
        color: #d1d5db;
    }
    .data-table tr:last-child td { border-bottom: none; }
    .data-table tr:hover td { background: #1a1d2e; }
    
    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.15s;
    }
    
    /* ── Select box ── */
    .stSelectbox > div > div { background: #161a26; border-color: #2d3555; }
    
    /* ── Columns spacing ── */
    [data-testid="stHorizontalBlock"] { gap: 12px; }
    
    /* ── Divider ── */
    hr { border-color: #1f2438; margin: 1rem 0; }
    
    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 20px;
        font-size: 0.7rem;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

# ─── Data Helpers ────────────────────────────────────────────────────────

def get_stats():
    return {
        "workers": 47,
        "ppe_compliance": 91,
        "alerts_today": 12,
        "critical": 1,
        "cameras_online": 5,
        "cameras_total": 6,
        "fire_risk": "Low",
        "equipment_uptime": 97.3,
        "shift": "Morning",
    }

def get_cameras():
    return [
        {"id": 1, "name": "Assembly Area", "status": "online", "persons": 12, "ppe_score": 94, "last": "5 min ago"},
        {"id": 2, "name": "Gate 1 - Entry", "status": "online", "persons": 3, "ppe_score": 100, "last": "23 min ago"},
        {"id": 3, "name": "Paint Shop", "status": "warning", "persons": 5, "ppe_score": 78, "last": "12 min ago"},
        {"id": 4, "name": "Machine Hall A", "status": "online", "persons": 8, "ppe_score": 96, "last": "45 min ago"},
        {"id": 5, "name": "Storage Area", "status": "offline", "persons": 0, "ppe_score": 0, "last": "2 hours ago"},
        {"id": 6, "name": "Loading Dock", "status": "online", "persons": 4, "ppe_score": 100, "last": "1 hour ago"},
    ]

def get_alerts():
    now = datetime.now()
    return [
        {"type": "critical", "icon": "🔥", "title": "Fire Detected", "msg": "Assembly Area — confidence 94%", "time": "5 min ago"},
        {"type": "warning", "icon": "🪖", "title": "PPE Violation", "msg": "Paint Shop — Worker without helmet", "time": "12 min ago"},
        {"type": "info", "icon": "🚗", "title": "Unknown Vehicle", "msg": "Gate 1 — Unrecognized vehicle", "time": "23 min ago"},
        {"type": "warning", "icon": "🛢️", "title": "Spill Detected", "msg": "Machine Hall A — Oil spill near Machine B", "time": "45 min ago"},
        {"type": "success", "icon": "🔄", "title": "Shift Changed", "msg": "Now: Afternoon Shift", "time": "1 hour ago"},
    ]

def get_safety_scores():
    return [
        ("Fire Safety", 95, "#10b981"),
        ("PPE Compliance", 91, "#10b981"),
        ("Equipment", 97, "#10b981"),
        ("Spill Control", 78, "#f59e0b"),
        ("Hazard Zone", 92, "#10b981"),
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

# ─── Top Bar ─────────────────────────────────────────────────────────────
col_logo, col_title, col_right = st.columns([1, 3, 2])

with col_logo:
    st.markdown("🏭", unsafe_allow_html=False)

with col_title:
    st.markdown("""
    <div class="brand">
        <div>
            <div class="brand-name">AI24x7 Factory Edition</div>
            <div class="brand-sub">Industrial AI Surveillance System — v1.0</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    now = datetime.now()
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:flex-end; gap:12px; margin-top:4px;">
        <span class="live-badge">● LIVE</span>
        <span style="font-size:0.8rem; color:#6b7280;">{now.strftime('%d %b %Y, %H:%M')}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── Sidebar Navigation ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏭 Navigation")
    
    # Quick status
    stats = get_stats()
    shift = stats["shift"]
    shift_times = {"Morning": "06:00–14:00", "Afternoon": "14:00–22:00", "Night": "22:00–06:00"}
    
    st.markdown(f"""
    <div class="shift-badge" style="width:100%; justify-content:center;">
        ⏰ {shift} Shift · {shift_times.get(shift,'06:00–14:00')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    nav_options = [
        "📊 Overview",
        "📹 Camera Feeds",
        "🔥 Safety Alerts",
        "🪖 PPE Compliance",
        "🔄 Shift Reports",
        "⚙️ Equipment",
        "📱 Notifications",
        "⚙️ Settings",
    ]
    
    selected = st.radio("Navigate", nav_options, label_visibility="collapsed")
    
    st.markdown("")
    st.markdown("""<div class="sidebar-label">Quick Stats</div>""", unsafe_allow_html=True)
    
    # Quick stats in sidebar
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Workers", stats["workers"])
    with col_s2:
        st.metric("PPE", f"{stats['ppe_compliance']}%")
    
    col_s3, col_s4 = st.columns(2)
    with col_s3:
        st.metric("Alerts", stats["alerts_today"])
    with col_s4:
        st.metric("Uptime", f"{stats['equipment_uptime']}%")
    
    st.markdown("")
    st.markdown("""<div class="sidebar-label">Camera Status</div>""", unsafe_allow_html=True)
    
    cameras = get_cameras()
    for cam in cameras:
        color = "status-online" if cam["status"] == "online" else "status-warning" if cam["status"] == "warning" else "status-offline"
        dot = "🟢" if cam["status"] == "online" else "🟡" if cam["status"] == "warning" else "⚫"
        st.markdown(f"{dot} <span class='{color}'>{cam['name']}</span>", unsafe_allow_html=True)
    
    st.markdown("")
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# ─── PAGE: OVERVIEW ───────────────────────────────────────────────────────
if selected == "📊 Overview":
    stats = get_stats()
    
    # Top metric cards row
    st.markdown("""<div class="section-title">Key Metrics</div>""", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class="metric-wrap green">
            <div class="metric-icon">👷</div>
            <div class="metric-number" style="color:#10b981;">{stats['workers']}</div>
            <div class="metric-label">Active Workers</div>
            <div class="metric-delta up">▲ 3 from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m2:
        st.markdown(f"""
        <div class="metric-wrap blue">
            <div class="metric-icon">🪖</div>
            <div class="metric-number" style="color:#3b82f6;">{stats['ppe_compliance']}%</div>
            <div class="metric-label">PPE Compliance</div>
            <div class="metric-delta up">▲ 2% from last week</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m3:
        st.markdown(f"""
        <div class="metric-wrap orange">
            <div class="metric-icon">🔔</div>
            <div class="metric-number" style="color:#f59e0b;">{stats['alerts_today']}</div>
            <div class="metric-label">Alerts Today</div>
            <div class="metric-delta down">▲ 3 new</div>
        </div>
        """, unsafe_allow_html=True)
    
    with m4:
        fire_color = "#10b981" if stats["fire_risk"] == "Low" else "#f59e0b" if stats["fire_risk"] == "Medium" else "#ef4444"
        fire_icon = "🟢" if stats["fire_risk"] == "Low" else "🟡" if stats["fire_risk"] == "Medium" else "🔴"
        st.markdown(f"""
        <div class="metric-wrap green">
            <div class="metric-icon">🔥</div>
            <div class="metric-number" style="color:{fire_color};">{fire_icon} {stats['fire_risk']}</div>
            <div class="metric-label">Fire Risk</div>
            <div class="metric-delta up">All sensors normal</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Camera Grid + Alerts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""<div class="section-title">📹 Camera Grid</div>""", unsafe_allow_html=True)
        
        cams = get_cameras()
        rows = [cams[i:i+3] for i in range(0, len(cams), 3)]
        for row in rows:
            cols_cam = st.columns(3)
            for idx, cam in enumerate(row):
                with cols_cam[idx]:
                    dot = "🟢" if cam["status"] == "online" else "🟡" if cam["status"] == "warning" else "🔴"
                    status_color = "#10b981" if cam["status"] == "online" else "#f59e0b" if cam["status"] == "warning" else "#6b7280"
                    
                    st.markdown(f"""
                    <div class="cam-card">
                        <div class="cam-thumb">
                            📹
                            <div class="cam-overlay">
                                <span style="color:{status_color};">{dot} {cam['status'].upper()}</span>
                            </div>
                        </div>
                        <div class="cam-body">
                            <div class="cam-name">{cam['name']}</div>
                            <div class="cam-meta">
                                <span>👥 {cam['persons']}</span>
                                <span style="color:{'#10b981' if cam['ppe_score']>=90 else '#f59e0b' if cam['ppe_score']>=75 else '#ef4444'};">PPE {cam['ppe_score']}%</span>
                                <span>{cam['last']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""<div class="section-title">🚨 Live Alerts</div>""", unsafe_allow_html=True)
        
        alerts = get_alerts()
        for a in alerts:
            icon = {"critical": "🔥", "warning": "🪖", "info": "🚗", "success": "✅"}.get(a["type"], "⚠️")
            st.markdown(f"""
            <div class="alert-card {a['type']}">
                <div class="alert-icon">{icon}</div>
                <div class="alert-body">
                    <div class="alert-title">{a['title']}</div>
                    <div class="alert-meta">{a['msg']}</div>
                    <div class="alert-meta">{a['time']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Safety Scores + Equipment
    col_eq, col_safety = st.columns([1, 1])
    
    with col_eq:
        st.markdown("""<div class="section-title">⚙️ Equipment Status</div>""", unsafe_allow_html=True)
        
        equip = get_equipment()
        for name, status, uptime, ok in equip:
            dot = "🟢" if ok else "🔴"
            status_txt = "Running" if ok else "Maintenance"
            bar_color = "#10b981" if ok else "#ef4444"
            bar_width = uptime if ok else 0
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:0.85rem;">{dot} {name}</span>
                <span style="font-size:0.78rem; color:#6b7280;">{status_txt} {uptime}%</span>
            </div>
            <div class="progress-track" style="margin-bottom:14px;">
                <div class="progress-fill" style="width:{bar_width}%; background:{bar_color};"></div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_safety:
        st.markdown("""<div class="section-title">🏆 Safety Score</div>""", unsafe_allow_html=True)
        
        scores = get_safety_scores()
        for name, score, color in scores:
            st.markdown(f"""
            <div class="progress-row">
                <div class="progress-label">
                    <span>{name}</span>
                    <span style="color:{color};">{score}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width:{score}%; background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("""
        <div style="background:#0f2922; border:1px solid #065f46; border-radius:12px; padding:16px; text-align:center;">
            <div style="font-size:2rem; font-weight:800; color:#10b981;">87<span style="font-size:1rem;">/100</span></div>
            <div style="font-size:0.78rem; color:#6b7280; margin-top:4px;">Overall Safety Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("""<div class="section-title">⚡ Quick Actions</div>""", unsafe_allow_html=True)
    
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("📸 Snapshot All Cameras", use_container_width=True):
            with st.spinner("Capturing..."):
                time.sleep(1.2)
            st.success("Saved!")
    with qa2:
        if st.button("📋 Shift Report", use_container_width=True):
            st.info("Report generated!")
    with qa3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with qa4:
        if st.button("🚨 Test Alert", use_container_width=True):
            st.warning("Test alert sent to Telegram!")

# ─── PAGE: CAMERA FEEDS ──────────────────────────────────────────────────
elif selected == "📹 Camera Feeds":
    st.title("📹 Live Camera Feeds")
    
    cameras = get_cameras()
    
    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
    filter_status = col_f1.selectbox("Filter by Status", ["All", "Online", "Warning", "Offline"])
    filter_cam = col_f2.selectbox("Camera", ["All"] + [c["name"] for c in cameras])
    view_mode = col_f3.selectbox("View", ["Grid", "List"])
    
    filtered = cameras
    if filter_status != "All":
        filtered = [c for c in filtered if c["status"].lower() == filter_status.lower()]
    if filter_cam != "All":
        filtered = [c for c in filtered if c["name"] == filter_cam]
    
    if view_mode == "Grid":
        rows2 = [filtered[i:i+3] for i in range(0, len(filtered), 3)]
        for row2 in rows2:
            cols_g = st.columns(3)
            for idx2, cam in enumerate(row2):
                with cols_g[idx2]:
                    dot = "🟢" if cam["status"] == "online" else "🟡" if cam["status"] == "warning" else "🔴"
                    sc = "#10b981" if cam["status"] == "online" else "#f59e0b" if cam["status"] == "warning" else "#6b7280"
                    ppc = "#10b981" if cam["ppe_score"] >= 90 else "#f59e0b" if cam["ppe_score"] >= 75 else "#ef4444"
                    
                    st.markdown(f"""
                    <div class="cam-card" style="cursor:pointer;">
                        <div class="cam-thumb" style="height:160px; font-size:3.5rem;">
                            📹
                            <div style="position:absolute; top:8px; right:8px; background:rgba(0,0,0,0.7); padding:3px 8px; border-radius:4px;">
                                <span style="color:{sc}; font-size:0.72rem; font-weight:600;">{dot} {cam['status'].upper()}</span>
                            </div>
                            <div style="position:absolute; bottom:8px; right:8px; background:rgba(0,0,0,0.7); padding:2px 8px; border-radius:4px;">
                                <span style="font-size:0.72rem;">{cam['id']:02d}</span>
                            </div>
                        </div>
                        <div class="cam-body">
                            <div class="cam-name">{cam['name']}</div>
                            <div class="cam-meta" style="margin-top:8px;">
                                <span>👥 {cam['persons']} workers</span>
                                <span style="color:{ppc}; font-weight:600;">PPE {cam['ppe_score']}%</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns(2)
                    with b1:
                        st.button(f"📸 Snapshot #{cam['id']}", key=f"snap_{cam['id']}", use_container_width=True)
                    with b2:
                        st.button(f"📊 Analytics #{cam['id']}", key=f"ana_{cam['id']}", use_container_width=True)
    else:
        st.markdown("""
        <table class="data-table">
            <thead>
                <tr>
                    <th>#</th><th>Camera</th><th>Status</th><th>Workers</th>
                    <th>PPE Score</th><th>Last Alert</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)
        
        for cam in filtered:
            dot = "🟢" if cam["status"] == "online" else "🟡" if cam["status"] == "warning" else "🔴"
            sc = "#10b981" if cam["status"] == "online" else "#f59e0b" if cam["status"] == "warning" else "#6b7280"
            ppc = "#10b981" if cam["ppe_score"] >= 90 else "#f59e0b" if cam["ppe_score"] >= 75 else "#ef4444"
            st.markdown(f"""
                <tr>
                    <td>{cam['id']}</td>
                    <td><b>{cam['name']}</b></td>
                    <td style="color:{sc};">{dot} {cam['status'].capitalize()}</td>
                    <td>{cam['persons']}</td>
                    <td style="color:{ppc}; font-weight:600;">{cam['ppe_score']}%</td>
                    <td>{cam['last']}</td>
                    <td>
                        <button style="background:#1f2937; color:#e5e7eb; border:none; padding:4px 10px; border-radius:6px; font-size:0.75rem; cursor:pointer;">📸</button>
                        <button style="background:#1f2937; color:#e5e7eb; border:none; padding:4px 10px; border-radius:6px; font-size:0.75rem; cursor:pointer;">📊</button>
                    </td>
                </tr>
            """, unsafe_allow_html=True)
        st.markdown("</tbody></table>", unsafe_allow_html=True)

# ─── PAGE: SAFETY ALERTS ─────────────────────────────────────────────────
elif selected == "🔥 Safety Alerts":
    st.title("🔥 Safety Alert Center")
    
    stats = get_stats()
    a1, a2, a3 = st.columns(3)
    a1.metric("Total Alerts", stats["alerts_today"], delta=3)
    a2.metric("Critical", stats["critical"], delta_color="inverse")
    a3.metric("Resolved", stats["alerts_today"] - stats["critical"])
    
    st.markdown("")
    
    ft = st.selectbox("Filter by Type", ["All", "Fire", "PPE", "Spill", "Entry", "Equipment"])
    fs = st.selectbox("Status", ["All", "Unhandled", "Handled"])
    
    alerts = get_alerts()
    for a in alerts:
        if ft != "All" and ft.lower() not in a["title"].lower():
            continue
        
        icon = {"critical": "🔥", "warning": "🪖", "info": "🚗", "success": "✅"}.get(a["type"], "⚠️")
        ac = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#3b82f6", "success": "#10b981"}.get(a["type"], "#6b7280")
        
        st.markdown(f"""
        <div class="alert-card {a['type']}">
            <div class="alert-icon">{icon}</div>
            <div class="alert-body">
                <div class="alert-title" style="color:{ac};">{a['title']}</div>
                <div class="alert-meta">{a['msg']}</div>
                <div class="alert-meta">{a['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cb1, cb2 = st.columns(2)
        with cb1:
            st.button(f"✅ Acknowledge", key=f"ack_{a['title']}", use_container_width=True)
        with cb2:
            st.button(f"📞 Escalate", key=f"esc_{a['title']}", use_container_width=True)
    
    st.markdown("")
    st.markdown("""<div class="section-title">📊 Alert History (7 Days)</div>""", unsafe_allow_html=True)
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fire_vals = [2, 1, 0, 3, 1, 0, 1]
    ppe_vals = [5, 3, 4, 2, 6, 1, 2]
    st.bar_chart({"🔥 Fire": fire_vals, "🪖 PPE": ppe_vals}, height=200)

# ─── PAGE: PPE COMPLIANCE ────────────────────────────────────────────────
elif selected == "🪖 PPE Compliance":
    st.title("🪖 PPE Compliance Dashboard")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #065f46, #10b981); border-radius: 16px; padding: 28px; text-align: center; margin-bottom: 24px;">
        <div style="font-size: 3rem; font-weight: 800; color: white;">91%</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 1rem;">Overall PPE Compliance — Target: 95%</div>
    </div>
    """, unsafe_allow_html=True)
    
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("🪖 Helmet", "96%", delta=2)
    p2.metric("🦺 Safety Vest", "94%", delta=1)
    p3.metric("🧤 Gloves", "82%", delta=-5)
    p4.metric("👢 Safety Shoes", "88%", delta=-2)
    
    st.markdown("")
    st.markdown("""<div class="section-title">📹 Camera-wise PPE Score</div>""", unsafe_allow_html=True)
    
    cameras = get_cameras()
    for cam in cameras:
        score = cam["ppe_score"]
        color = "#10b981" if score >= 90 else "#f59e0b" if score >= 75 else "#ef4444"
        st.markdown(f"**{cam['name']}** — {score}%", unsafe_allow_html=False)
        st.markdown(f"""
        <div class="progress-track" style="margin-bottom:16px;">
            <div class="progress-fill" style="width:{score}%; background:{color};"></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""<div class="section-title">⚠️ Recent Violations</div>""", unsafe_allow_html=True)
    
    violations = [
        ("🪖 No Helmet", "Camera 3 - Paint Shop", "Ramesh Kumar", "12 min ago"),
        ("🦺 No Safety Vest", "Camera 1 - Assembly", "Unknown Worker", "28 min ago"),
        ("🧤 No Gloves", "Camera 4 - Machine Hall", "Suresh Patil", "45 min ago"),
        ("👢 Improper Shoes", "Camera 2 - Gate 1", "Labour 007", "1 hour ago"),
    ]
    
    for vtype, cam, person, t in violations:
        st.markdown(f"""
        <div class="alert-card warning">
            <div class="alert-icon">{vtype}</div>
            <div class="alert-body">
                <div class="alert-title">{vtype}</div>
                <div class="alert-meta">{cam} • {person} • {t}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("📋 Export PPE Report", use_container_width=True):
        st.success("PPE Report exported!")

# ─── PAGE: SHIFT REPORTS ────────────────────────────────────────────────
elif selected == "🔄 Shift Reports":
    st.title("🔄 Shift Reports")
    
    col_sr1, col_sr2 = st.columns([1, 1])
    with col_sr1:
        st.markdown("""
        <div class="info-card">
            <div class="info-card-title">⏰ Current Shift Summary</div>
            <div style="font-size:1.5rem; font-weight:700; color:#3b82f6;">Morning Shift</div>
            <div style="font-size:0.85rem; color:#6b7280; margin-top:4px;">06:00 — 14:00 • 50% complete</div>
            <div class="progress-track" style="margin-top:12px;">
                <div class="progress-fill" style="width:50%; background:#3b82f6;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_sr2:
        st.selectbox("Select Shift Report", [
            "Morning Shift — 27 Apr 2026",
            "Afternoon Shift — 26 Apr 2026",
            "Night Shift — 26 Apr 2026",
        ])
    
    st.markdown("")
    st.markdown("""<div class="section-title">📊 Shift Metrics</div>""", unsafe_allow_html=True)
    
    sr1, sr2, sr3, sr4 = st.columns(4)
    sr1.metric("Total Workers", 47)
    sr2.metric("PPE Violations", 3)
    sr3.metric("Incidents", 0)
    sr4.metric("Equipment Downtime", "0.5h")
    
    st.markdown("")
    st.markdown("""
    <table class="data-table">
        <thead><tr><th>Metric</th><th>Value</th></tr></thead>
        <tbody>
            <tr><td>Total Workers</td><td>47</td></tr>
            <tr><td>PPE Violations</td><td>3</td></tr>
            <tr><td>Fire Alarms</td><td>0</td></tr>
            <tr><td>Unauthorized Entry</td><td>1</td></tr>
            <tr><td>Spill Incidents</td><td>1</td></tr>
            <tr><td>Equipment Downtime</td><td>0.5h</td></tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    
    col_pdf, col_csv, col_email = st.columns(3)
    with col_pdf:
        st.button("📄 Generate PDF Report", use_container_width=True)
    with col_csv:
        st.button("📤 Export CSV", use_container_width=True)
    with col_email:
        st.button("📧 Email to Manager", use_container_width=True)

# ─── PAGE: EQUIPMENT ─────────────────────────────────────────────────────
elif selected == "⚙️ Equipment":
    st.title("⚙️ Equipment Monitoring")
    
    equip = get_equipment()
    
    # Summary cards
    ec1, ec2, ec3, ec4 = st.columns(4)
    ec1.metric("Total Machines", len(equip))
    ec2.metric("Running", len([e for e in equip if e[3]]))
    ec3.metric("Maintenance", len([e for e in equip if not e[3]]))
    ec4.metric("Avg Uptime", f"{sum(e[2] for e in equip)/len(equip):.0f}%")
    
    st.markdown("")
    st.markdown("""
    <table class="data-table">
        <thead>
            <tr>
                <th>Equipment</th><th>Status</th><th>Uptime</th>
                <th>Condition</th><th>Runtime</th><th>Actions</th>
            </tr>
        </thead>
        <tbody>
    """, unsafe_allow_html=True)
    
    equip_data = [
        ("Conveyor A", "Running", "98%", "Normal", "8h 23m"),
        ("Conveyor B", "Running", "95%", "Normal", "6h 45m"),
        ("Robot Arm 1", "Running", "100%", "Normal", "12h 00m"),
        ("CNC Machine", "Maintenance", "N/A", "Scheduled", "0h 30m"),
        ("Furnace 1", "Running", "92%", "Normal", "8h 10m"),
        ("Compressor", "Running", "88%", "Normal", "5h 15m"),
        ("Hydraulic Press", "Stopped", "0%", "Repair", "3h 00m"),
        ("AGV Robot", "Running", "96%", "Normal", "4h 50m"),
    ]
    
    for name, status, uptime, cond, runtime in equip_data:
        dot = "🟢" if status == "Running" else "🔴"
        sc = "#10b981" if status == "Running" else "#ef4444"
        bar_color = "#10b981" if status == "Running" else "#ef4444"
        bar_w = int(uptime.replace("%","")) if "%" in uptime else 0
        
        st.markdown(f"""
            <tr>
                <td><b>{name}</b></td>
                <td style="color:{sc};">{dot} {status}</td>
                <td>
                    {uptime}
                    <div class="progress-track" style="margin-top:4px;">
                        <div class="progress-fill" style="width:{bar_w}%; background:{bar_color};"></div>
                    </div>
                </td>
                <td>{cond}</td>
                <td>{runtime}</td>
                <td>
                    <button style="background:#1f2937; color:#e5e7eb; border:none; padding:3px 8px; border-radius:5px; font-size:0.72rem; cursor:pointer;">⚙️</button>
                    <button style="background:#1f2937; color:#e5e7eb; border:none; padding:3px 8px; border-radius:5px; font-size:0.72rem; cursor:pointer;">📊</button>
                </td>
            </tr>
        """, unsafe_allow_html=True)
    
    st.markdown("</tbody></table>", unsafe_allow_html=True)

# ─── PAGE: NOTIFICATIONS ─────────────────────────────────────────────────
elif selected == "📱 Notifications":
    st.title("📱 Notification Settings")
    
    st.markdown("""<div class="section-title">Telegram</div>""", unsafe_allow_html=True)
    tg_en = st.toggle("Enable Telegram Alerts", value=True)
    if tg_en:
        st.text_input("Bot Token", value="8751634203:AAEtay1...", disabled=True)
        st.text_input("Chat ID", value="8566322083")
    
    st.markdown("")
    st.markdown("""<div class="section-title">SMS</div>""", unsafe_allow_html=True)
    sms_en = st.toggle("Enable SMS Alerts", value=False)
    if sms_en:
        st.text_input("SMS API Key", type="password")
        st.text_input("Recipients", value="+91-98XXXXXXX")
    
    st.markdown("")
    st.markdown("""<div class="section-title">WhatsApp</div>""", unsafe_allow_html=True)
    wa_en = st.toggle("Enable WhatsApp", value=False)
    if wa_en:
        st.text_input("WhatsApp Business Number")
    
    st.markdown("")
    st.markdown("""<div class="section-title">📋 Alert Rules</div>""", unsafe_allow_html=True)
    
    rules = [
        ("🔥 Fire Detected", True, "All", "Critical"),
        ("🪖 PPE Violation", True, "All", "Warning"),
        ("🚗 Unauthorized Entry", True, "All", "Warning"),
        ("🛢️ Spill Detected", True, "All", "Critical"),
        ("⚙️ Equipment Down", False, "Admin", "Info"),
        ("🔄 Shift Change", True, "Manager", "Info"),
    ]
    
    for name, en, send, sev in rules:
        col_r1, col_r2, col_r3, col_r4 = st.columns([3, 1, 1, 1])
        with col_r1:
            st.markdown(f"**{name}**", unsafe_allow_html=False)
        with col_r2:
            st.toggle("", value=en)
        with col_r3:
            st.markdown(f"`{send}`", unsafe_allow_html=False)
        with col_r4:
            colors = {"Critical": "#ef4444", "Warning": "#f59e0b", "Info": "#3b82f6"}
            st.markdown(f"<span style='color:{colors[sev]}; font-size:0.85rem;'>{sev}</span>", unsafe_allow_html=True)
    
    st.markdown("")
    if st.button("💾 Save Notification Settings", use_container_width=True, type="primary"):
        st.success("Settings saved!")

# ─── PAGE: SETTINGS ──────────────────────────────────────────────────────
elif selected == "⚙️ Settings":
    st.title("⚙️ System Settings")
    
    st.markdown("""<div class="section-title">🏭 Factory Configuration</div>""", unsafe_allow_html=True)
    
    s1, s2 = st.columns(2)
    with s1:
        factory_name = st.text_input("Factory Name", value="Alpha Industries - Unit 1")
        st.text_input("Factory ID", value="FACT-001")
    with s2:
        st.selectbox("Language", ["English", "Hindi", "Hindi + English"])
        st.selectbox("Time Zone", ["IST (UTC+5:30)", "UTC", "EST (UTC-5)"])
    
    st.markdown("")
    st.markdown("""<div class="section-title">📹 Camera Management</div>""", unsafe_allow_html=True)
    
    if st.button("➕ Add Camera", use_container_width=True):
        st.info("Add camera form would appear here")
    
    cameras = get_cameras()
    for cam in cameras:
        with st.expander(f"📹 {cam['name']} (ID: #{cam['id']})"):
            st.text_input("Name", value=cam["name"], key=f"name_{cam['id']}")
            st.text_input("RTSP URL", value=f"rtsp://192.168.1.{cam['id']}/stream", key=f"rtsp_{cam['id']}")
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("Type", ["Dome", "Bullet", "PTZ"], key=f"type_{cam['id']}")
            with c2:
                st.selectbox("Location", ["Indoor", "Outdoor"], key=f"loc_{cam['id']}")
            cb1, cb2 = st.columns(2)
            with cb1:
                st.button(f"💾 Save", key=f"save_{cam['id']}", use_container_width=True)
            with cb2:
                st.button(f"🗑️ Delete", key=f"del_{cam['id']}", use_container_width=True)
    
    st.markdown("")
    st.markdown("""<div class="section-title">🔄 Shift Configuration</div>""", unsafe_allow_html=True)
    
    shifts = [("Morning", "06:00", "14:00"), ("Afternoon", "14:00", "22:00"), ("Night", "22:00", "06:00")]
    for name, start, end in shifts:
        sc1, sc2, sc3, sc4 = st.columns([2, 2, 2, 1])
        with sc1:
            st.markdown(f"**{name}**", unsafe_allow_html=False)
        with sc2:
            st.text_input(f"Start ({name})", value=start, key=f"start_{name}")
        with sc3:
            st.text_input(f"End ({name})", value=end, key=f"end_{name}")
        with sc4:
            st.toggle("Enable", value=True, key=f"enable_{name}")
    
    st.markdown("")
    st.markdown("""<div class="section-title">🛡️ Safety Rules</div>""", unsafe_allow_html=True)
    
    st.toggle("🔔 Auto-alert on Fire", value=True)
    st.toggle("🔔 Auto-alert on PPE Violation", value=True)
    st.toggle("🔊 Voice Announcement on Fire", value=True)
    st.number_input("Alert Repeat Interval (minutes)", value=5, min_value=1, max_value=60)
    
    st.markdown("")
    col_save, col_restart = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save All Settings", use_container_width=True, type="primary"):
            st.success("Settings saved!")
    with col_restart:
        if st.button("🔄 Restart All Services", use_container_width=True):
            with st.spinner("Restarting..."):
                time.sleep(2)
            st.success("Services restarted!")
    
    st.markdown("")
    st.markdown(f"""
    <div class="footer">
        AI24x7 Factory Edition v1.0.0 • © 2026 GOUP CONSULTANCY SERVICES LLP<br>
        Factory ID: FACT-001 | License: ACTIVE | Last Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────
else:
    pass
