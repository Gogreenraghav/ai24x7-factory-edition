#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Dashboard Database
SQLite database for real data storage
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_FILE = Path(__file__).parent / "factory_data.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    
    # ── Cameras ──────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rtsp_url TEXT,
            status TEXT DEFAULT 'online' CHECK(status IN ('online','warning','offline')),
            ppe_score INTEGER DEFAULT 100,
            persons INTEGER DEFAULT 0,
            last_alert TEXT,
            location TEXT,
            cam_type TEXT DEFAULT 'Dome',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Alerts ─────────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER,
            event_type TEXT NOT NULL,
            confidence REAL,
            message TEXT,
            severity TEXT DEFAULT 'info' CHECK(severity IN ('critical','warning','info','success')),
            acknowledged INTEGER DEFAULT 0,
            acknowledged_by TEXT,
            acknowledged_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (camera_id) REFERENCES cameras(id)
        )
    """)

    # ── Workers ────────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            employee_id TEXT UNIQUE,
            department TEXT,
            ppe_status TEXT DEFAULT 'compliant',
            last_seen TEXT,
            face_encoding BLOB,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── PPE Violations ────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ppe_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER,
            worker_name TEXT,
            violation_type TEXT,
            image_data BLOB,
            acknowledged INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (camera_id) REFERENCES cameras(id)
        )
    """)

    # ── Equipment ─────────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'Running',
            uptime_percent REAL DEFAULT 100,
            runtime_today TEXT,
            condition TEXT DEFAULT 'Normal',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Shift Reports ─────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shift_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift_name TEXT NOT NULL,
            shift_date DATE NOT NULL,
            total_workers INTEGER DEFAULT 0,
            ppe_violations INTEGER DEFAULT 0,
            incidents INTEGER DEFAULT 0,
            fire_alarms INTEGER DEFAULT 0,
            unauthorized_entry INTEGER DEFAULT 0,
            spill_incidents INTEGER DEFAULT 0,
            equipment_downtime TEXT DEFAULT '0h',
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── Daily Stats ───────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            total_alerts INTEGER DEFAULT 0,
            critical_alerts INTEGER DEFAULT 0,
            ppe_score_avg INTEGER DEFAULT 0,
            fire_risk TEXT DEFAULT 'Low',
            top_violations TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # ── System Config ─────────────────────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables created!")

def seed_demo_data():
    """Seed with realistic demo data"""
    conn = get_db()

    # Check if already seeded
    if conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0] > 0:
        print("Data already seeded, skipping.")
        conn.close()
        return

    # Seed cameras
    cameras = [
        (1, "Assembly Area", "rtsp://192.168.1.10/stream1", "online", 94, 12, "5 min ago", "Indoor"),
        (2, "Gate 1 - Entry", "rtsp://192.168.1.11/stream1", "online", 100, 3, "23 min ago", "Outdoor"),
        (3, "Paint Shop", "rtsp://192.168.1.12/stream1", "warning", 78, 5, "12 min ago", "Indoor"),
        (4, "Machine Hall A", "rtsp://192.168.1.13/stream1", "online", 96, 8, "45 min ago", "Indoor"),
        (5, "Storage Area", "rtsp://192.168.1.14/stream1", "offline", 0, 0, "2 hours ago", "Indoor"),
        (6, "Loading Dock", "rtsp://192.168.1.15/stream1", "online", 100, 4, "1 hour ago", "Outdoor"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO cameras (id, name, rtsp_url, status, ppe_score, persons, last_alert, location) VALUES (?,?,?,?,?,?,?,?)",
        cameras
    )

    # Seed alerts
    now = datetime.now()
    alerts = [
        (1, "fire", 0.94, "Assembly Area — Fire detected, confidence 94%", "critical", 0),
        (3, "ppe_violation", 0.87, "Paint Shop — No helmet detected", "warning", 0),
        (2, "unknown_vehicle", 0.82, "Gate 1 — Unknown vehicle at gate", "info", 0),
        (4, "spill", 0.79, "Machine Hall A — Oil spill near Machine B", "warning", 0),
        (0, "shift_change", 1.0, "Shift changed to Afternoon — 14:00 to 22:00", "success", 1),
        (1, "ppe_violation", 0.85, "Assembly Area — Worker without safety vest", "warning", 0),
        (3, "fire_smoke", 0.91, "Paint Shop — Smoke detected in Zone B", "critical", 0),
        (6, "unauthorized_entry", 0.78, "Loading Dock — Unrecognized person", "info", 0),
    ]
    for cam_id, etype, conf, msg, sev, ack in alerts:
        ts = (now - timedelta(minutes=conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] * 5)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(
            "INSERT INTO alerts (camera_id, event_type, confidence, message, severity, acknowledged, created_at) VALUES (?,?,?,?,?,?,?)",
            (cam_id, etype, conf, msg, sev, ack, ts)
        )

    # Seed equipment
    equip = [
        ("Conveyor A", "Running", 98, "8h 23m", "Normal"),
        ("Conveyor B", "Running", 95, "6h 45m", "Normal"),
        ("Robot Arm 1", "Running", 100, "12h 00m", "Normal"),
        ("CNC Machine", "Maintenance", 0, "0h 30m", "Scheduled"),
        ("Furnace 1", "Running", 92, "8h 10m", "Normal"),
        ("Compressor", "Running", 88, "5h 15m", "Normal"),
        ("Hydraulic Press", "Stopped", 0, "3h 00m", "Repair"),
        ("AGV Robot", "Running", 96, "4h 50m", "Normal"),
    ]
    conn.executemany(
        "INSERT INTO equipment (name, status, uptime_percent, runtime_today, condition) VALUES (?,?,?,?,?)",
        equip
    )

    # Seed PPE violations
    violations = [
        (3, "Ramesh Kumar", "no_helmet"),
        (1, "Unknown Worker", "no_safety_vest"),
        (4, "Suresh Patil", "no_gloves"),
        (2, "Labour 007", "improper_shoes"),
    ]
    for cam_id, worker, vtype in violations:
        conn.execute(
            "INSERT INTO ppe_violations (camera_id, worker_name, violation_type, created_at) VALUES (?,?,?,?)",
            (cam_id, worker, vtype, (now - timedelta(minutes=conn.execute("SELECT COUNT(*) FROM ppe_violations").fetchone()[0] * 15)).strftime('%Y-%m-%d %H:%M:%S'))
        )

    # Seed shift reports
    today = datetime.now().date()
    reports = [
        ("Morning", (today - timedelta(days=1)).isoformat(), 45, 2, 0, 0, 1, 0, "0h", "Normal day"),
        ("Afternoon", (today - timedelta(days=1)).isoformat(), 42, 4, 0, 0, 2, 1, "0.5h", "Minor spill incident"),
        ("Night", (today - timedelta(days=1)).isoformat(), 38, 1, 0, 0, 0, 0, "0h", "Quiet night shift"),
        ("Morning", today.isoformat(), 47, 3, 0, 0, 1, 1, "0.5h", "In progress"),
    ]
    conn.executemany(
        "INSERT INTO shift_reports (shift_name, shift_date, total_workers, ppe_violations, incidents, fire_alarms, unauthorized_entry, spill_incidents, equipment_downtime, notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
        reports
    )

    # Seed daily stats
    stats = [
        ((today - timedelta(days=i)).isoformat(), 10+i, 1, 88+i%5, "Low", "No helmet,Spill") 
        for i in range(1, 8)
    ]
    conn.executemany(
        "INSERT INTO daily_stats (date, total_alerts, critical_alerts, ppe_score_avg, fire_risk) VALUES (?,?,?,?,?)",
        [(s[0], s[1], s[2], s[3], s[4]) for s in stats]
    )
    # Today's stats
    conn.execute(
        "INSERT OR IGNORE INTO daily_stats (date, total_alerts, critical_alerts, ppe_score_avg, fire_risk) VALUES (?,?,?,?,?)",
        (today.isoformat(), 12, 1, 91, "Low")
    )

    # Seed config
    config = [
        ("factory_name", "Alpha Industries - Unit 1"),
        ("factory_id", "FACT-001"),
        ("license_key", "FACTORY-XXXX-XXXX-XXXX-XXXX"),
        ("timezone", "IST"),
        ("language", "English"),
        ("current_shift", "Morning"),
    ]
    conn.executemany("INSERT OR IGNORE INTO config (key, value) VALUES (?,?)", config)

    conn.commit()
    conn.close()
    print("✅ Demo data seeded!")

# ─── QUERY FUNCTIONS ─────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_db()
    stats = {
        "workers": conn.execute("SELECT SUM(persons) FROM cameras WHERE status != 'offline'").fetchone()[0] or 0,
        "ppe": int(conn.execute("SELECT AVG(ppe_score) FROM cameras WHERE status != 'offline'").fetchone()[0] or 0),
        "alerts_today": conn.execute("SELECT COUNT(*) FROM alerts WHERE DATE(created_at) = DATE('now')").fetchone()[0],
        "critical": conn.execute("SELECT COUNT(*) FROM alerts WHERE severity='critical' AND acknowledged=0 AND DATE(created_at) = DATE('now')").fetchone()[0],
        "cameras_online": conn.execute("SELECT COUNT(*) FROM cameras WHERE status='online'").fetchone()[0],
        "cameras_total": conn.execute("SELECT COUNT(*) FROM cameras").fetchone()[0],
        "fire_risk": "Low",
        "uptime": conn.execute("SELECT AVG(uptime_percent) FROM equipment WHERE status='Running'").fetchone()[0] or 0,
    }
    conn.close()
    return stats

def get_all_cameras():
    conn = get_db()
    rows = conn.execute("SELECT * FROM cameras ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_alerts(limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT a.*, c.name as camera_name FROM alerts a LEFT JOIN cameras c ON a.camera_id=c.id ORDER BY a.created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_equipment():
    conn = get_db()
    rows = conn.execute("SELECT * FROM equipment ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ppe_violations(limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT p.*, c.name as camera_name FROM ppe_violations p LEFT JOIN cameras c ON p.camera_id=c.id ORDER BY p.created_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_shift_reports(limit=5):
    conn = get_db()
    rows = conn.execute("SELECT * FROM shift_reports ORDER BY shift_date DESC, shift_name LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_daily_stats(days=7):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM daily_stats ORDER BY date DESC LIMIT ?", (days,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def acknowledge_alert(alert_id):
    conn = get_db()
    conn.execute("UPDATE alerts SET acknowledged=1, acknowledged_at=datetime('now') WHERE id=?", (alert_id,))
    conn.commit()
    conn.close()

def get_config(key, default=""):
    conn = get_db()
    row = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else default

def set_config(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?,?,datetime('now'))", (key, value))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_demo_data()
    print(f"Database ready: {DB_FILE}")
    print(f"Stats: {get_dashboard_stats()}")
