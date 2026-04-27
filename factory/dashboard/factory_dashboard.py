#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Dashboard
Professional Streamlit dashboard for industrial monitoring
Run: streamlit run factory/dashboard/factory_dashboard.py --server.port 5052
"""
import streamlit as st
import time
import json
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Page config
st.set_page_config(
    page_title="AI24x7 Factory Dashboard",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background: #0e1117; }
    .metric-card { background: #1a1f2e; border-radius: 12px; padding: 20px; margin: 5px; text-align: center; }
    .metric-value { font-size: 2.5rem; font-weight: bold; color: #00d4aa; }
    .metric-label { font-size: 0.9rem; color: #8b95a5; margin-top: 5px; }
    .alert-critical { background: linear-gradient(135deg, #ff4444, #cc0000); border-radius: 8px; padding: 12px; color: white; margin: 5px 0; }
    .alert-warning { background: linear-gradient(135deg, #ffaa00, #ff8800); border-radius: 8px; padding: 12px; color: white; margin: 5px 0; }
    .alert-info { background: linear-gradient(135deg, #00aaff, #0066cc); border-radius: 8px; padding: 12px; color: white; margin: 5px 0; }
    .status-online { color: #00ff88; font-weight: bold; }
    .status-offline { color: #ff4444; font-weight: bold; }
    .status-warning { color: #ffaa00; font-weight: bold; }
    .camera-feed { border-radius: 12px; border: 2px solid #2a3441; overflow: hidden; }
    .section-header { background: #1a2332; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #00d4aa; }
    .progress-bar { height: 8px; border-radius: 4px; background: #2a3441; }
    .sidebar-section { background: #1a1f2e; padding: 15px; border-radius: 10px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA / STATE
# =============================================================================

def load_config():
    config_path = Path(__file__).parent.parent.parent / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {"cameras": [], "factory": {"name": "My Factory"}, "shifts": {}}

def get_alerts():
    """Generate demo alerts for display"""
    return [
        {"time": datetime.now() - timedelta(minutes=5), "type": "critical", "camera": "Camera 1", "message": "🔥 Fire detected in Assembly Area", "handled": False},
        {"time": datetime.now() - timedelta(minutes=12), "type": "warning", "camera": "Camera 3", "message": "⚠️ PPE Violation - Worker without helmet", "handled": False},
        {"time": datetime.now() - timedelta(minutes=23), "type": "info", "camera": "Camera 2", "message": "🚗 Unknown vehicle detected at Gate 1", "handled": True},
        {"time": datetime.now() - timedelta(minutes=45), "type": "warning", "camera": "Camera 4", "message": "🛢️ Oil spill detected near Machine A", "handled": False},
        {"time": datetime.now() - timedelta(minutes=60), "type": "info", "camera": "Camera 1", "message": "🔄 Shift changed to: Afternoon", "handled": True},
    ]

def get_camera_feeds():
    """Return camera status"""
    return [
        {"id": 1, "name": "Assembly Area", "status": "online", "persons": 12, "ppe_score": 94, "last_alert": "5 min ago"},
        {"id": 2, "name": "Gate 1 - Entry", "status": "online", "persons": 3, "ppe_score": 100, "last_alert": "23 min ago"},
        {"id": 3, "name": "Paint Shop", "status": "warning", "persons": 5, "ppe_score": 78, "last_alert": "12 min ago"},
        {"id": 4, "name": "Machine Hall A", "status": "online", "persons": 8, "ppe_score": 96, "last_alert": "45 min ago"},
        {"id": 5, "name": "Storage Area", "status": "offline", "persons": 0, "ppe_score": 0, "last_alert": "2 hours ago"},
        {"id": 6, "name": "Loading Dock", "status": "online", "persons": 4, "ppe_score": 100, "last_alert": "1 hour ago"},
    ]

def get_shift_data():
    now = datetime.now()
    hour = now.hour
    if 6 <= hour < 14:
        shift = "Morning"
        progress = ((hour - 6) * 60 + now.minute) / 480 * 100
    elif 14 <= hour < 22:
        shift = "Afternoon"
        progress = ((hour - 14) * 60 + now.minute) / 480 * 100
    else:
        shift = "Night"
        progress = ((hour - 22) * 60 + now.minute) / 480 * 100 if hour >= 22 else ((hour + 2) * 60 + now.minute) / 480 * 100
    return shift, min(progress, 100)

def get_stats():
    """Overall factory stats"""
    return {
        "total_cameras": 6,
        "online_cameras": 5,
        "total_workers": 47,
        "ppe_compliance": 91,
        "alerts_today": 12,
        "critical_alerts": 1,
        "fire_risk": "Low",
        "equipment_uptime": 97.3,
        "shift_compliance": 89,
    }

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("## 🏭 AI24x7 Factory")
    st.markdown("### Factory Dashboard")
    st.divider()

    config = load_config()
    st.markdown(f"**Factory:** {config.get('factory', {}).get('name', 'My Factory')}")
    st.markdown(f"**Status:** <span class='status-online'>● Online</span>", unsafe_allow_html=True)

    shift, shift_progress = get_shift_data()
    st.markdown(f"**Current Shift:** {shift}")
    st.progress(shift_progress / 100, text=f"{shift_progress:.0f}% complete")

    st.divider()

    # Quick Stats in Sidebar
    stats = get_stats()

    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Workers", stats["total_workers"])
    with col2:
        st.metric("PPE %", f"{stats['ppe_compliance']}%")

    col3, col4 = st.columns(2)
    with col3:
        st.metric("Alerts", stats["alerts_today"])
    with col4:
        st.metric("Uptime", f"{stats['equipment_uptime']}%")

    st.divider()

    # Camera List
    st.markdown("### 📹 Cameras")
    cameras = get_camera_feeds()
    for cam in cameras:
        if cam["status"] == "online":
            color = "status-online"
        elif cam["status"] == "warning":
            color = "status-warning"
        else:
            color = "status-offline"
        st.markdown(f"- {cam['name']}: <span class='{color}'>● {cam['status'].upper()}</span>", unsafe_allow_html=True)

    st.divider()

    # Navigation
    st.markdown("### 🧭 Navigation")
    page = st.radio("Go to", [
        "📊 Overview",
        "📹 Camera Feeds",
        "🔥 Safety Alerts",
        "🪖 PPE Compliance",
        "🔄 Shift Reports",
        "⚙️ Equipment",
        "📱 Notifications",
        "⚙️ Settings"
    ])

    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# =============================================================================
# PAGE: OVERVIEW
# =============================================================================

if page == "📊 Overview":
    st.title("🏭 Factory Overview Dashboard")
    st.markdown(f"**{datetime.now().strftime('%A, %d %B %Y - %H:%M')}**")

    # Top Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{stats["total_workers"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Active Workers</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        color = "green" if stats["ppe_compliance"] >= 90 else "orange" if stats["ppe_compliance"] >= 75 else "red"
        st.markdown(f'<div class="metric-value" style="color: #{color if color=="green" else "orange" if color=="orange" else "ff4444"}">{stats["ppe_compliance"]}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">PPE Compliance</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{stats["alerts_today"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Alerts Today</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        fire_color = "00ff88" if stats["fire_risk"] == "Low" else "ffaa00" if stats["fire_risk"] == "Medium" else "ff4444"
        st.markdown(f'<div class="metric-value" style="color: #{fire_color}">{stats["fire_risk"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Fire Risk Level</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Camera Grid + Alerts Side by Side
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### 📹 Camera Status Grid")
        cameras = get_camera_feeds()

        # 2x3 grid
        for row in range(2):
            cols = st.columns(3)
            for col_idx in range(3):
                cam_idx = row * 3 + col_idx
                if cam_idx < len(cameras):
                    cam = cameras[cam_idx]
                    with cols[col_idx]:
                        # Camera placeholder (black box with text)
                        st.markdown(f"""
                        <div style="background: #1a1f2e; border-radius: 10px; padding: 10px; text-align: center; border: 1px solid #2a3441;">
                            <div style="background: #0a0f1a; border-radius: 8px; height: 80px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                                <span style="color: #4a5568; font-size: 2rem;">📹</span>
                            </div>
                            <div style="font-weight: bold; font-size: 0.85rem;">{cam['name']}</div>
                            <div style="font-size: 0.75rem; color: #8b95a5;">{cam['name']} #{cam['id']}</div>
                            <div style="margin-top: 5px;">
                                <span class="{'status-online' if cam['status']=='online' else 'status-warning' if cam['status']=='warning' else 'status-offline'}">● {cam['status'].upper()}</span>
                            </div>
                            <div style="font-size: 0.7rem; color: #6b7280; margin-top: 3px;">👥 {cam['persons']} | PPE {cam['ppe_score']}%</div>
                        </div>
                        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 🚨 Live Alerts")

        alerts = get_alerts()
        critical = [a for a in alerts if a["type"] == "critical" and not a["handled"]]
        warnings = [a for a in alerts if a["type"] == "warning" and not a["handled"]]
        infos = [a for a in alerts if a["type"] == "info" and not a["handled"]]

        if critical:
            for a in critical:
                st.markdown(f"""
                <div class="alert-critical">
                    <div style="font-weight: bold; font-size: 0.85rem;">{a['message']}</div>
                    <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 3px;">{a['camera']} • {(datetime.now()-a['time']).seconds//60}m ago</div>
                </div>
                """, unsafe_allow_html=True)

        for a in warnings:
            st.markdown(f"""
            <div class="alert-warning">
                <div style="font-weight: bold; font-size: 0.85rem;">{a['message']}</div>
                <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 3px;">{a['camera']} • {(datetime.now()-a['time']).seconds//60}m ago</div>
            </div>
            """, unsafe_allow_html=True)

        for a in infos:
            st.markdown(f"""
            <div class="alert-info">
                <div style="font-weight: bold; font-size: 0.85rem;">{a['message']}</div>
                <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 3px;">{a['camera']} • {(datetime.now()-a['time']).seconds//60}m ago</div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔔 Acknowledge All Alerts"):
            st.success("All alerts acknowledged")

    st.markdown("---")

    # Shift + Safety Score
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔄 Current Shift Progress")
        shift, progress = get_shift_data()
        st.info(f"**{shift} Shift** - {progress:.0f}% complete")

        shift_data = {
            "Morning": [("06:00", "14:00"), 8],
            "Afternoon": [("14:00", "22:00"), 8],
            "Night": [("22:00", "06:00"), 8],
        }
        shift_info = shift_data.get(shift, shift_data["Morning"])

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Start", shift_info[0])
        with col_b:
            st.metric("End", shift_info[1])
        with col_c:
            st.metric("Duration", f"{shift_info[2]}h")

        st.progress(progress / 100)

        # Shift events
        st.markdown("#### 📋 Shift Events")
        for event in ["Shift started", "Morning briefing completed", "Equipment check OK", "PPE inspection passed"]:
            st.markdown(f"✅ {event}")

    with col2:
        st.markdown("### 🏆 Safety Score")
        safety_score = 87
        score_color = "🟢" if safety_score >= 80 else "🟡" if safety_score >= 60 else "🔴"
        st.markdown(f"#### {score_color} **{safety_score}/100**")

        st.markdown("""
        <div style="background: #1a1f2e; padding: 15px; border-radius: 10px; margin-top: 10px;">
            <div style="margin: 8px 0;">🔥 Fire Safety: <span style="color:#00ff88">95%</span></div>
            <div style="background: #2a3441; height: 6px; border-radius: 3px; margin-bottom: 10px;">
                <div style="background: #00ff88; height: 6px; border-radius: 3px; width: 95%;"></div>
            </div>

            <div style="margin: 8px 0;">🪖 PPE Compliance: <span style="color:#00ff88">91%</span></div>
            <div style="background: #2a3441; height: 6px; border-radius: 3px; margin-bottom: 10px;">
                <div style="background: #00ff88; height: 6px; border-radius: 3px; width: 91%;"></div>
            </div>

            <div style="margin: 8px 0;">⚙️ Equipment: <span style="color:#00ff88">97%</span></div>
            <div style="background: #2a3441; height: 6px; border-radius: 3px; margin-bottom: 10px;">
                <div style="background: #00ff88; height: 6px; border-radius: 3px; width: 97%;"></div>
            </div>

            <div style="margin: 8px 0;">🛢️ Spill Control: <span style="color:#ffaa00">78%</span></div>
            <div style="background: #2a3441; height: 6px; border-radius: 3px; margin-bottom: 10px;">
                <div style="background: #ffaa00; height: 6px; border-radius: 3px; width: 78%;"></div>
            </div>

            <div style="margin: 8px 0;">🏗️ Hazard Zone: <span style="color:#00ff88">92%</span></div>
            <div style="background: #2a3441; height: 6px; border-radius: 3px;">
                <div style="background: #00ff88; height: 6px; border-radius: 3px; width: 92%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Bottom Row - Equipment + Quick Actions
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### ⚙️ Equipment Status")
        equip = [
            ("Conveyor A", "Running", 98, True),
            ("Conveyor B", "Running", 95, True),
            ("Robot Arm 1", "Running", 100, True),
            ("CNC Machine", "Maintenance", 0, False),
            ("Furnace 1", "Running", 92, True),
            ("Compressor", "Running", 88, True),
        ]
        for name, status, uptime, ok in equip:
            status_color = "🟢" if ok else "🔴"
            st.markdown(f"{status_color} **{name}**: {status} ({uptime}%)")

    with col2:
        st.markdown("### 📊 Today's Statistics")
        st.markdown(f"""
        - **Workers Present:** {stats['total_workers']}
        - **Incidents:** 0
        - **PPE Violations:** 3
        - **Fire Alarms:** 0
        - **Unauthorized Entry:** 1
        - **Spill Incidents:** 1
        - **Equipment Downtime:** 0.5h
        - **Nearest Shift End:** 14:00
        """)

    with col3:
        st.markdown("### ⚡ Quick Actions")
        if st.button("📸 Capture All Cameras"):
            with st.spinner("Capturing..."):
                time.sleep(1)
            st.success("Screenshot saved!")
        if st.button("📋 Generate Shift Report"):
            st.success("Report generated!")
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()
        if st.button("🚨 Test Alert System"):
            st.warning("Test alert sent!")

# =============================================================================
# PAGE: CAMERA FEEDS
# =============================================================================

elif page == "📹 Camera Feeds":
    st.title("📹 Live Camera Feeds")

    cameras = get_camera_feeds()

    # Filter
    cols = st.columns([1, 1, 1, 2])
    filter_status = cols[0].selectbox("Status", ["All", "Online", "Warning", "Offline"])
    filter_camera = cols[1].selectbox("Camera", ["All"] + [c["name"] for c in cameras])
    view_mode = cols[2].selectbox("View", ["Grid", "List", "Single Full"])

    filtered = cameras
    if filter_status != "All":
        filtered = [c for c in filtered if c["status"].lower() == filter_status.lower()]

    if filter_camera != "All":
        filtered = [c for c in filtered if c["name"] == filter_camera]

    if view_mode == "Grid":
        cols_per_row = st.slider("Columns", 1, 4, 3)
        rows = [filtered[i:i+cols_per_row] for i in range(0, len(filtered), cols_per_row)]
        for row in rows:
            cols = st.columns(len(row))
            for idx, cam in enumerate(row):
                with cols[idx]:
                    st.markdown(f"""
                    <div style="background: #1a1f2e; border-radius: 12px; padding: 0; overflow: hidden; border: 1px solid #2a3441;">
                        <div style="background: #0a0f1a; height: 150px; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 3rem;">📹</span>
                        </div>
                        <div style="padding: 12px;">
                            <div style="font-weight: bold; font-size: 0.9rem;">{cam['name']}</div>
                            <div style="color: #8b95a5; font-size: 0.8rem; margin-top: 2px;">Camera #{cam['id']}</div>
                            <div style="margin-top: 8px;">
                                <span class="{'status-online' if cam['status']=='online' else 'status-warning' if cam['status']=='warning' else 'status-offline'}">● {cam['status'].upper()}</span>
                            </div>
                            <div style="margin-top: 8px; display: flex; justify-content: space-between; font-size: 0.8rem;">
                                <span>👥 {cam['persons']}</span>
                                <span>PPE {cam['ppe_score']}%</span>
                                <span>{cam['last_alert']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    elif view_mode == "Single Full":
        cam_name = st.selectbox("Select Camera", [c["name"] for c in cameras])
        cam = next(c for c in cameras if c["name"] == cam_name)

        st.markdown(f"""
        <div style="background: #1a1f2e; border-radius: 12px; overflow: hidden; border: 2px solid #00d4aa;">
            <div style="background: #000; height: 450px; display: flex; align-items: center; justify-content: center;">
                <div style="text-align: center;">
                    <div style="font-size: 5rem;">📹</div>
                    <div style="color: #666; margin-top: 10px;">LIVE FEED - {cam['name']}</div>
                </div>
            </div>
            <div style="padding: 15px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                <div><div style="color: #8b95a5; font-size: 0.7rem;">Status</div><div class="{'status-online' if cam['status']=='online' else 'status-warning' if cam['status']=='warning' else 'status-offline'}">● {cam['status'].upper()}</div></div>
                <div><div style="color: #8b95a5; font-size: 0.7rem;">Persons</div><div style="font-weight: bold;">{cam['persons']}</div></div>
                <div><div style="color: #8b95a5; font-size: 0.7rem;">PPE Score</div><div style="font-weight: bold; color: #00d4aa;">{cam['ppe_score']}%</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.button("📸 Snapshot")
        with col2:
            st.button("🎥 Record 30s")
        with col3:
            st.button("📊 Analytics")
        with col4:
            st.button("⚙️ Configure")

    else:
        # List view
        for cam in filtered:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{cam['name']}** (#{cam['id']})")
            with col2:
                st.markdown(f"👥 {cam['persons']}")
            with col3:
                st.markdown(f"PPE: {cam['ppe_score']}%")
            with col4:
                st.markdown(f"⏱️ {cam['last_alert']}")
            with col5:
                status_color = "🟢" if cam['status']=='online' else "🟡" if cam['status']=='warning' else "🔴"
                st.markdown(f"{status_color} {cam['status']}")

# =============================================================================
# PAGE: SAFETY ALERTS
# =============================================================================

elif page == "🔥 Safety Alerts":
    st.title("🔥 Safety Alert Center")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Alerts", 12, delta=3)
    col2.metric("Critical", 1, delta_color="inverse")
    col3.metric("Resolved", 9)

    st.divider()

    # Filter
    filter_type = st.selectbox("Alert Type", ["All", "Fire", "PPE", "Spill", "Entry", "Equipment"])
    filter_status = st.selectbox("Status", ["All", "Unhandled", "Handled"])

    alerts = get_alerts()

    for a in alerts:
        if filter_type != "All" and filter_type.lower() not in a["message"].lower():
            continue

        icon = "🔴" if a["type"] == "critical" else "🟡" if a["type"] == "warning" else "🔵"
        bg = "#ff4444" if a["type"] == "critical" else "#ffaa00" if a["type"] == "warning" else "#0088ff"

        st.markdown(f"""
        <div style="background: #1a1f2e; border-radius: 10px; padding: 15px; margin: 8px 0; border-left: 4px solid {bg};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 1.5rem;">{icon}</span>
                    <span style="font-weight: bold; font-size: 1.1rem; margin-left: 8px;">{a['message']}</span>
                </div>
                <div style="text-align: right; color: #8b95a5; font-size: 0.85rem;">
                    <div>{a['camera']}</div>
                    <div>{a['time'].strftime('%H:%M')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button(f"✅ Acknowledge", key=f"ack_{a['time'].timestamp()}"):
                st.success("Alert acknowledged")
        with col_btn2:
            if st.button(f"📞 Escalate", key=f"esc_{a['time'].timestamp()}"):
                st.warning("Alert escalated to manager")

    st.markdown("---")

    # Alert Statistics
    st.markdown("### 📊 Alert Statistics (Last 7 Days)")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Today"]
    fire_vals = [2, 1, 0, 3, 1, 0, 1]
    ppe_vals = [5, 3, 4, 2, 6, 1, 2]
    st.bar_chart({"Fire": fire_vals, "PPE": ppe_vals}, height=200)

# =============================================================================
# PAGE: PPE COMPLIANCE
# =============================================================================

elif page == "🪖 PPE Compliance":
    st.title("🪖 PPE Compliance Dashboard")

    overall = 91
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #00d4aa, #00a866); border-radius: 15px; padding: 25px; text-align: center; margin: 15px 0;">
        <div style="font-size: 3rem; font-weight: bold; color: white;">{overall}%</div>
        <div style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">Overall PPE Compliance</div>
        <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-top: 5px;">Target: 95% | Current: Good</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Helmet", "96%", delta=2)
    col2.metric("Safety Vest", "94%", delta=1)
    col3.metric("Gloves", "82%", delta=-5)
    col4.metric("Safety Shoes", "88%", delta=-2)

    st.divider()

    st.markdown("### 📹 Camera-wise PPE Score")
    cameras = get_camera_feeds()
    for cam in cameras:
        score = cam["ppe_score"]
        bar_color = "#00ff88" if score >= 90 else "#ffaa00" if score >= 75 else "#ff4444"
        st.markdown(f"**{cam['name']}** - {score}%")
        st.markdown(f"""
        <div style="background: #2a3441; height: 10px; border-radius: 5px; margin-bottom: 15px;">
            <div style="background: {bar_color}; height: 10px; border-radius: 5px; width: {score}%;"></div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Violation log
    st.markdown("### ⚠️ Recent Violations")
    violations = [
        ("Camera 3 - Paint Shop", "No Helmet", "Ramesh Kumar", "12 min ago"),
        ("Camera 1 - Assembly", "No Safety Vest", "Unknown", "28 min ago"),
        ("Camera 4 - Machine Hall", "No Gloves", "Suresh Patil", "45 min ago"),
        ("Camera 2 - Gate 1", "Improper Shoes", "Labour 007", "1 hour ago"),
    ]

    for cam, violation, person, time in violations:
        st.markdown(f"""
        <div style="background: #1a1f2e; padding: 12px; border-radius: 8px; margin: 5px 0; border-left: 3px solid #ff4444;">
            <div style="font-weight: bold;">{violation}</div>
            <div style="color: #8b95a5; font-size: 0.85rem;">{cam} | {person} | {time}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("📋 Export PPE Report"):
        st.success("PPE Report exported!")

# =============================================================================
# PAGE: SHIFT REPORTS
# =============================================================================

elif page == "🔄 Shift Reports":
    st.title("🔄 Shift Reports")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Current Shift Summary")
        shift, progress = get_shift_data()
        st.info(f"**{shift} Shift** - {progress:.0f}% complete")
    with col2:
        selected_shift = st.selectbox("View Shift Report", ["Morning - 26 Apr", "Afternoon - 25 Apr", "Night - 25 Apr"])

    st.divider()

    # Report Preview
    st.markdown("""
    | Metric | Value |
    |--------|-------|
    | Total Workers | 47 |
    | PPE Violations | 3 |
    | Fire Alarms | 0 |
    | Equipment Downtime | 0.5h |
    | Incidents | 0 |
    | Unauthorized Entries | 1 |
    | Spill Incidents | 1 |
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("📄 Generate PDF Report")
    with col2:
        st.button("📤 Export CSV")
    with col3:
        st.button("📧 Email to Manager")

    st.divider()

    st.markdown("### 📊 Historical Shift Data")
    st.line_chart({
        "Morning": [89, 92, 88, 94, 91],
        "Afternoon": [85, 87, 90, 88, 93],
        "Night": [82, 86, 89, 87, 91]
    })

# =============================================================================
# PAGE: EQUIPMENT
# =============================================================================

elif page == "⚙️ Equipment":
    st.title("⚙️ Equipment Monitoring")

    st.markdown("### Real-time Equipment Status")

    equipment = [
        ("Conveyor A", "Running", "98%", "Normal", "8h 23m"),
        ("Conveyor B", "Running", "95%", "Normal", "6h 45m"),
        ("Robot Arm 1", "Running", "100%", "Normal", "12h 00m"),
        ("CNC Machine", "Maintenance", "N/A", "Scheduled", "0h 30m"),
        ("Furnace 1", "Running", "92%", "Normal", "8h 10m"),
        ("Compressor", "Running", "88%", "Normal", "5h 15m"),
        ("Hydraulic Press", "Stopped",        "0%", "Under Repair", "3h 00m"),
        ("AGV Robot", "Running", "96%", "Normal", "4h 50m"),
    ]

    for name, status, uptime, condition, runtime in equipment:
        col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
        with col1:
            st.markdown(f"**{name}**")
        with col2:
            color = "🟢" if status == "Running" else "🔴"
            st.markdown(f"{color} {status}")
        with col3:
            st.markdown(uptime)
        with col4:
            st.markdown(condition)
        with col5:
            st.markdown(runtime)
        with col6:
            if st.button(f"⚙️", key=f"cfg_{name}"):
                st.info(f"Configuring {name}")

# =============================================================================
# PAGE: NOTIFICATIONS
# =============================================================================

elif page == "📱 Notifications":
    st.title("📱 Notification Settings")

    st.markdown("### 📲 Alert Channels")

    st.markdown("#### Telegram")
    st.toggle("Enable Telegram Alerts", value=True)
    st.text_input("Bot Token", value="8751634203:AAEtay1...", disabled=True)
    st.text_input("Chat ID", value="8566322083")

    st.markdown("---")
    st.markdown("#### SMS")
    st.toggle("Enable SMS Alerts", value=False)
    st.text_input("SMS API Key", type="password")
    st.text_input("Recipients (comma separated)", value="+91-XXXXX")

    st.markdown("---")
    st.markdown("#### WhatsApp")
    st.toggle("Enable WhatsApp", value=False)
    st.text_input("WhatsApp Business Number")

    st.markdown("---")
    st.markdown("#### Email")
    st.toggle("Enable Email Alerts", value=False)
    st.text_input("SMTP Server")
    st.text_input("Email Recipients")

    st.markdown("---")
    st.markdown("### 🔔 Alert Rules")

    alert_rules = [
        ("Fire Detected", True, "All", "Critical"),
        ("PPE Violation", True, "All", "Warning"),
        ("Unauthorized Entry", True, "All", "Warning"),
        ("Spill Detected", True, "All", "Critical"),
        ("Equipment Down", False, "All", "Info"),
        ("Shift Change", True, "Manager", "Info"),
    ]

    for name, enabled, send_to, severity in alert_rules:
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
        with col1:
            st.markdown(f"**{name}**")
        with col2:
            st.toggle("", value=enabled, key=f"toggle_{name}")
        with col3:
            st.markdown(f"`{send_to}`")
        with col4:
            color = "🔴" if severity == "Critical" else "🟡" if severity == "Warning" else "🔵"
            st.markdown(f"{color} {severity}")
        with col5:
            st.button("✏️", key=f"edit_{name}")

    if st.button("💾 Save Notification Settings"):
        st.success("Settings saved!")

# =============================================================================
# PAGE: SETTINGS
# =============================================================================

elif page == "⚙️ Settings":
    st.title("⚙️ System Settings")

    st.markdown("### 🏭 Factory Configuration")

    factory_name = st.text_input("Factory Name", value="Alpha Industries - Unit 1")
    factory_id = st.text_input("Factory ID", value="FACT-001")
    st.text_input("License Key", value="FACTORY-XXXX-XXXX-XXXX-XXXX", disabled=True)

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Language", ["English", "Hindi", "Hindi + English"])
    with col2:
        st.selectbox("Time Zone", ["IST (UTC+5:30)", "UTC", "EST (UTC-5)"])

    st.markdown("---")
    st.markdown("### 📹 Camera Management")

    st.button("➕ Add Camera")
    st.button("🔄 Auto-detect Cameras")

    cameras = get_camera_feeds()
    for cam in cameras:
        with st.expander(f"📹 {cam['name']} (#{cam['id']})"):
            st.text_input("Name", value=cam["name"], key=f"name_{cam['id']}")
            st.text_input("RTSP URL", value=f"rtsp://192.168.1.{cam['id']}/stream", key=f"rtsp_{cam['id']}")
            st.selectbox("Type", ["Dome", "Bullet", "PTZ"], key=f"type_{cam['id']}")
            st.selectbox("Location", ["Indoor", "Outdoor"], key=f"loc_{cam['id']}")
            cols = st.columns(2)
            if cols[0].button("💾 Save", key=f"save_{cam['id']}"):
                st.success("Camera saved!")
            if cols[1].button("🗑️ Delete", key=f"del_{cam['id']}"):
                st.error("Camera deleted!")

    st.markdown("---")
    st.markdown("### 🔄 Shift Configuration")

    shifts = [
        ("Morning", "06:00", "14:00"),
        ("Afternoon", "14:00", "22:00"),
        ("Night", "22:00", "06:00"),
    ]

    for name, start, end in shifts:
        cols = st.columns([2, 2, 2, 1])
        with cols[0]:
            st.markdown(f"**{name}**")
        with cols[1]:
            st.text_input(f"Start ({name})", value=start, key=f"start_{name}")
        with cols[2]:
            st.text_input(f"End ({name})", value=end, key=f"end_{name}")
        with cols[3]:
            st.toggle("Enable", value=True, key=f"enable_{name}")

    st.markdown("---")
    st.markdown("### 🛡️ Safety Rules")

    st.toggle("Auto-alert on Fire", value=True)
    st.toggle("Auto-alert on PPE Violation", value=True)
    st.toggle("Voice Announcement on Fire", value=True)
    st.number_input("Alert Repeat Interval (minutes)", value=5, min_value=1, max_value=60)

    st.markdown("---")
    if st.button("💾 Save All Settings", type="primary"):
        st.success("Settings saved successfully!")

    st.markdown("---")
    st.markdown("### 🔄 System")
    if st.button("🔄 Restart All Services"):
        with st.spinner("Restarting..."):
            time.sleep(2)
        st.success("Services restarted!")

    if st.button("📦 Update System"):
        st.info("No updates available")

    st.markdown(f"""
    ---
    **AI24x7 Factory Edition v1.0.0**
    Factory ID: FACT-001 | License: ACTIVE
    Last Updated: {datetime.now().strftime('%d %b %Y, %H:%M')}
    """)

# Auto-refresh every 30 seconds
st_autorefresh = st.interval(30, "page_refresh", None, False)

if __name__ == "__main__":
    st.markdown("Run with: `streamlit run factory/dashboard/factory_dashboard.py --server.port 5052`")
