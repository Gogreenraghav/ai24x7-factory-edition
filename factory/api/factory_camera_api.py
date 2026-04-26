#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Camera API
Real RTSP stream connection and AI analysis
Run: python3 factory_camera_api.py
Port: 5054
"""
import cv2, time, json, hashlib, uuid, threading, sqlite3, requests
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request
import numpy as np

app = Flask(__name__)

# Config
CONFIG_FILE = Path(__file__).parent.parent / "config.json"
DB_FILE = Path(__file__).parent.parent / "camera_events.db"
FRAME_SKIP = 3  # Process every 3rd frame
CONFIDENCE_THRESHOLD = 0.65

# Camera configs loaded from config.json
cameras = {}
active_streams = {}
stream_threads = {}
frame_buffers = {}

# ─── Load Config ────────────────────────────────────────────
def load_config():
    global cameras
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            data = json.load(f)
            cameras = {c["id"]: c for c in data.get("cameras", [])}
            print(f"📹 Loaded {len(cameras)} cameras from config")
    else:
        # Demo cameras
        cameras = {
            1: {"id": 1, "name": "Assembly Area", "rtsp": "rtsp://demo:demo@192.168.1.10/stream1", "enabled": True},
            2: {"id": 2, "name": "Gate 1 Entry", "rtsp": "rtsp://demo:demo@192.168.1.11/stream1", "enabled": True},
        }
        print("⚠️ Using demo camera config (no config.json found)")

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"cameras": list(cameras.values())}, f, indent=2)

# ─── DB Setup ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS camera_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER, event_type TEXT, confidence REAL,
            frame_data BLOB, annotated_frame BLOB,
            detected_at TEXT DEFAULT (datetime('now')),
            acknowledged INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS camera_stats (
            camera_id INTEGER PRIMARY KEY,
            name TEXT, total_frames INTEGER DEFAULT 0,
            fps_avg REAL DEFAULT 0, last_fps REAL DEFAULT 0,
            uptime_seconds INTEGER DEFAULT 0, last_seen TEXT,
            status TEXT DEFAULT 'offline'
        )
    """)
    conn.commit()
    conn.close()

# ─── Stream Handler ─────────────────────────────────────────
def get_frame_from_stream(cam_id):
    """Get latest frame from buffer (non-blocking)"""
    if cam_id in frame_buffers and len(frame_buffers[cam_id]) > 0:
        return frame_buffers[cam_id][-1]
    return None

def stream_reader(cam_id, rtsp_url):
    """Background thread: read RTSP stream"""
    global active_streams, frame_buffers
    
    print(f"[Cam {cam_id}] Connecting to {rtsp_url[:50]}...")
    
    # Try multiple backends
    backends = [
        lambda: cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG),
        lambda: cv2.VideoCapture(rtsp_url),
    ]
    
    cap = None
    for backend_fn in backends:
        try:
            cap = backend_fn()
            if cap.isOpened():
                break
        except:
            continue
    
    if not cap or not cap.isOpened():
        print(f"[Cam {cam_id}] ❌ Could not open stream")
        active_streams[cam_id] = "error"
        return
    
    active_streams[cam_id] = "running"
    fps_counter = 0
    fps_timer = time.time()
    fps_current = 0
    frame_count = 0
    
    print(f"[Cam {cam_id}] ✅ Stream connected")
    
    while active_streams.get(cam_id) == "running":
        ret, frame = cap.read()
        if not ret:
            print(f"[Cam {cam_id}] ⚠️ Stream ended, reconnecting...")
            active_streams[cam_id] = "reconnecting"
            time.sleep(3)
            # Try reconnect
            for backend_fn in backends:
                cap = backend_fn()
                if cap.isOpened():
                    active_streams[cam_id] = "running"
                    print(f"[Cam {cam_id}] ✅ Reconnected")
                    break
            if active_streams.get(cam_id) != "running":
                break
            continue
        
        frame_count += 1
        fps_counter += 1
        
        # Calculate FPS
        elapsed = time.time() - fps_timer
        if elapsed >= 1.0:
            fps_current = fps_counter / elapsed
            fps_counter = 0
            fps_timer = time.time()
        
        # Keep frame in buffer (last 5)
        if cam_id not in frame_buffers:
            frame_buffers[cam_id] = []
        frame_buffers[cam_id].append(frame.copy())
        if len(frame_buffers[cam_id]) > 5:
            frame_buffers[cam_id].pop(0)
        
        # Update stats
        update_camera_stats(cam_id, fps_current, frame_count)
        
        # Small delay to prevent CPU overload
        time.sleep(0.01)
    
    cap.release()
    active_streams[cam_id] = "stopped"
    print(f"[Cam {cam_id}] Stream stopped")

def update_camera_stats(cam_id, fps, total_frames):
    conn = sqlite3.connect(DB_FILE)
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO camera_stats (camera_id, name, total_frames, fps_avg, last_fps, last_seen, status, uptime_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(camera_id) DO UPDATE SET
            total_frames=total_frames+1,
            fps_avg=(fps_avg+?)/2,
            last_fps=?,
            last_seen=?,
            status='online',
            uptime_seconds=uptime_seconds+1
    """, (cam_id, cameras.get(cam_id, {}).get("name", f"Camera {cam_id}"),
          total_frames, fps, fps, now, fps, now))
    conn.commit()
    conn.close()

# ─── Detection Engine ───────────────────────────────────────
def analyze_frame(frame, cam_id):
    """
    AI Analysis on frame
    Returns: list of detections {type, confidence, bbox}
    
    NOTE: This is the integration point for AI models.
    Replace this with actual AI detection:
    - Fire: YOLOv8 fire model
    - PPE: YOLOv8 PPE model  
    - Fall: YOLOv8 fall detection
    - Face: face_recognition library
    """
    detections = []
    
    # Color-based fire detection (fallback until AI model is trained)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Fire color range
    fire_lower = np.array([0, 100, 100])
    fire_upper = np.array([30, 255, 255])
    mask = cv2.inRange(hsv, fire_lower, fire_upper)
    
    if cv2.countNonZero(mask) > 500:
        # Found fire-like colors
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1000:
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append({
                    "type": "fire",
                    "confidence": min(0.95, 0.5 + area / 50000),
                    "bbox": [int(x), int(y), int(w), int(h)]
                })
    
    # Motion detection (for person/vehicle)
    # (Integration point for actual person detection model)
    
    return detections

def start_camera(cam_id):
    """Start a camera stream in background thread"""
    if cam_id not in cameras:
        return False, "Camera not found"
    
    if active_streams.get(cam_id) == "running":
        return True, "Already running"
    
    cam = cameras[cam_id]
    if not cam.get("enabled", True):
        return False, "Camera disabled"
    
    active_streams[cam_id] = "starting"
    t = threading.Thread(target=stream_reader, args=(cam_id, cam["rtsp"]), daemon=True)
    t.start()
    stream_threads[cam_id] = t
    
    return True, "Starting..."

def stop_camera(cam_id):
    """Stop a camera stream"""
    if active_streams.get(cam_id) in ("running", "reconnecting"):
        active_streams[cam_id] = "stopped"
        return True
    return False

# ─── REST API Endpoints ─────────────────────────────────────

@app.route("/")
def root():
    return jsonify({"service":"AI24x7 Camera API v1.0","version":"1.0.0","cameras":len(cameras)})

@app.route("/health")
def health():
    return jsonify({"status":"ok","active_streams":len([v for v in active_streams.values() if v=="running"])})

# GET all cameras
@app.route("/cameras")
def list_cameras():
    result = []
    for cid, cam in cameras.items():
        result.append({
            "id": cid,
            "name": cam.get("name", f"Camera {cid}"),
            "rtsp": cam.get("rtsp", ""),
            "enabled": cam.get("enabled", True),
            "status": active_streams.get(cid, "stopped"),
            "fps": get_camera_fps(cid),
        })
    return jsonify(result)

# GET single camera
@app.route("/cameras/<int:cam_id>")
def get_camera(cam_id):
    if cam_id not in cameras:
        return jsonify({"error":"Camera not found"}), 404
    cam = cameras[cam_id]
    return jsonify({
        "id": cid,
        "name": cam.get("name"),
        "rtsp": cam.get("rtsp"),
        "enabled": cam.get("enabled"),
        "status": active_streams.get(cam_id, "stopped"),
        "fps": get_camera_fps(cam_id),
    })

def get_camera_fps(cam_id):
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute("SELECT last_fps FROM camera_stats WHERE camera_id=?", (cam_id,)).fetchone()
    conn.close()
    return row[0] if row else 0.0

# POST add camera
@app.route("/cameras", methods=["POST"])
def add_camera():
    data = request.json
    cam_id = len(cameras) + 1
    cameras[cam_id] = {
        "id": cam_id,
        "name": data.get("name", f"Camera {cam_id}"),
        "rtsp": data.get("rtsp", ""),
        "enabled": data.get("enabled", True),
    }
    save_config()
    return jsonify({"id": cam_id, "status": "added"}), 201

# POST update camera
@app.route("/cameras/<int:cam_id>", methods=["PUT"])
def update_camera(cam_id):
    if cam_id not in cameras:
        return jsonify({"error":"Camera not found"}), 404
    data = request.json
    cameras[cam_id].update({k: v for k, v in data.items() if k in ("name", "rtsp", "enabled")})
    save_config()
    return jsonify({"id": cam_id, "status": "updated"})

# DELETE camera
@app.route("/cameras/<int:cam_id>", methods=["DELETE"])
def delete_camera(cam_id):
    stop_camera(cam_id)
    if cam_id in cameras:
        del cameras[cam_id]
        save_config()
    return jsonify({"status": "deleted"})

# ─── Stream Control ─────────────────────────────────────────
@app.route("/stream/<int:cam_id>/start", methods=["POST"])
def start_stream(cam_id):
    success, msg = start_camera(cam_id)
    return jsonify({"camera_id": cam_id, "success": success, "message": msg})

@app.route("/stream/<int:cam_id>/stop", methods=["POST"])
def stop_stream(cam_id):
    success = stop_camera(cam_id)
    return jsonify({"camera_id": cam_id, "success": success})

# ─── Frame & Analysis ────────────────────────────────────────
@app.route("/stream/<int:cam_id>/frame")
def get_frame(cam_id):
    """Get latest JPEG frame from camera"""
    frame = get_frame_from_stream(cam_id)
    if frame is None:
        return jsonify({"error": "No frame available"}), 503
    
    # Encode to JPEG
    ret, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    if not ret:
        return jsonify({"error": "Encoding failed"}), 500
    
    return app.response_class(jpeg.tobytes(), mimetype="image/jpeg")

@app.route("/stream/<int:cam_id>/analyze", methods=["POST"])
def analyze_stream(cam_id):
    """Analyze current frame for safety events"""
    frame = get_frame_from_stream(cam_id)
    if frame is None:
        return jsonify({"error": "No frame available", "detections": []}), 503
    
    detections = analyze_frame(frame, cam_id)
    
    # Save event if detections found
    if detections:
        save_event(cam_id, detections, frame)
    
    return jsonify({
        "camera_id": cam_id,
        "timestamp": datetime.now().isoformat(),
        "detections": detections,
        "count": len(detections)
    })

def save_event(cam_id, detections, frame):
    """Save detection event to DB"""
    conn = sqlite3.connect(DB_FILE)
    
    # Encode frame (thumbnail)
    ret, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
    frame_data = jpeg.tobytes() if ret else None
    
    # Best detection
    best = max(detections, key=lambda d: d["confidence"])
    
    conn.execute("""
        INSERT INTO camera_events (camera_id, event_type, confidence, frame_data)
        VALUES (?, ?, ?, ?)
    """, (cam_id, best["type"], best["confidence"], frame_data))
    conn.commit()
    conn.close()

# ─── Events Log ─────────────────────────────────────────────
@app.route("/events")
def get_events():
    limit = request.args.get("limit", 50, type=int)
    cam_id = request.args.get("camera_id", type=int)
    event_type = request.args.get("type")
    
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT id, camera_id, event_type, confidence, detected_at, acknowledged FROM camera_events WHERE 1=1"
    params = []
    if cam_id:
        query += " AND camera_id=?"
        params.append(cam_id)
    if event_type:
        query += " AND event_type=?"
        params.append(event_type)
    query += " ORDER BY detected_at DESC LIMIT ?"
    params.append(limit)
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return jsonify([{
        "id": r[0], "camera_id": r[1], "type": r[2],
        "confidence": r[3], "at": r[4], "acknowledged": bool(r[5])
    } for r in rows])

@app.route("/events/<int:event_id>/acknowledge", methods=["POST"])
def ack_event(event_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE camera_events SET acknowledged=1 WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "acknowledged"})

# ─── Statistics ─────────────────────────────────────────────
@app.route("/stats")
def get_stats():
    conn = sqlite3.connect(DB_FILE)
    cameras_stats = conn.execute("SELECT * FROM camera_stats").fetchall()
    conn.close()
    return jsonify([{
        "camera_id": r[0], "name": r[1], "total_frames": r[2],
        "fps_avg": r[3], "last_fps": r[4], "uptime_seconds": r[5],
        "last_seen": r[6], "status": r[7]
    } for r in cameras_stats])

# ─── Telegram Alert Integration ──────────────────────────────
def send_telegram_alert(cam_id, event_type, confidence):
    """Send alert via Telegram"""
    BOT_TOKEN = "8751634203:AAEtay1djJH_Do7i_ZkBaX7CGXW6SPmAXTY"
    CHAT_ID = "8566322083"
    
    cam_name = cameras.get(cam_id, {}).get("name", f"Camera {cam_id}")
    emoji = {"fire": "🔥", "ppe_violation": "🪖", "fall": "🚨", "spill": "🛢️"}.get(event_type, "⚠️")
    
    message = f"{emoji} *AI24x7 Alert*\n\n*Event:* {event_type}\n*Camera:* {cam_name}\n*Confidence:* {confidence:.0%}\n*Time:* {datetime.now().strftime('%H:%M:%S')}"
    
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"
        }, timeout=10)
    except:
        pass

# ─── Init ──────────────────────────────────────────────────
load_config()
init_db()

# Auto-start enabled cameras
for cam_id, cam in cameras.items():
    if cam.get("enabled", True):
        threading.Timer(2.0, lambda cid=cam_id: start_camera(cid)).start()

if __name__ == "__main__":
    print("=" * 50)
    print("  AI24x7 Factory Camera API v1.0")
    print("  Port: 5054")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5054, debug=False, threaded=True)
