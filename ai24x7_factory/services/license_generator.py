#!/usr/bin/env python3
"""
AI24x7 License Generator Tool
Simple web interface: Machine ID daalo → License Key bano → DB mein save karo
Port: 5060
"""
import asyncio, hashlib, datetime, sqlite3, json
from aiohttp import web

DB_PATH = "/opt/ai24x7-docker/factory/dashboard/factory_data.db"
LOG_FILE = "/var/log/ai24x7/license_tool.log"

def make_key(machine_id: str, days: int = 365) -> str:
    salt = 'AI24X7_SALT_2026_SECURE'
    key = hashlib.sha256((machine_id + salt).encode()).hexdigest()[:24].upper()
    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime('%Y%m%d')
    return 'AI24X7-' + '-'.join([key[i:i+4] for i in range(0,24,4)]) + '-' + expiry

def get_mac_id() -> str:
    import subprocess
    try:
        r = subprocess.run(['cat', '/sys/class/net/eth0/address'],
                         capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            mac = r.stdout.strip()
            return hashlib.sha256(mac.encode()).hexdigest()[:32].upper()
    except: pass
    try:
        r = subprocess.run(['ip', 'link', 'show'],
                         capture_output=True, text=True, timeout=5)
        for line in r.stdout.splitlines():
            parts = line.strip().split()
            if 'ether' in parts:
                mac = parts[1]
                return hashlib.sha256(mac.encode()).hexdigest()[:32].upper()
    except: pass
    return 'UNKNOWN'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS license_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        machine_id TEXT UNIQUE,
        license_key TEXT,
        client_name TEXT,
        plan TEXT DEFAULT 'monthly',
        payment_status TEXT DEFAULT 'active',
        payment_due_date TEXT,
        max_cameras INTEGER DEFAULT 4,
        is_locked INTEGER DEFAULT 0,
        lock_reason TEXT,
        activated_at TEXT,
        last_payment_check TEXT
    )""")
    conn.commit()
    conn.close()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI24x7 License Generator</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,sans-serif; background:#0a0a1a; color:#e0e0e0; min-height:100vh; }

.header { background:linear-gradient(135deg,#0f0f2a,#1a1a3a); border-bottom:2px solid #00f0ff33; padding:20px 40px; display:flex; align-items:center; gap:16px; }
.logo { font-size:28px; font-weight:900; background:linear-gradient(90deg,#00f0ff,#ff00aa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.tagline { color:#00f0ff88; font-size:13px; margin-top:2px; }

.container { max-width:900px; margin:40px auto; padding:0 20px; }

/* Cards */
.card { background:#111128; border:1px solid #00f0ff22; border-radius:16px; padding:28px; margin-bottom:24px; box-shadow:0 4px 24px #00000060; }
.card-title { font-size:18px; font-weight:700; color:#00f0ff; margin-bottom:20px; display:flex; align-items:center; gap:8px; }

/* Current Machine */
.this-machine { background:linear-gradient(135deg,#0f2a1f,#0a1a15); border-color:#00ff8833; }
.machine-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.machine-box { background:#0a1a10; border:1px solid #00ff8822; border-radius:10px; padding:16px; text-align:center; }
.machine-label { font-size:11px; color:#00ff8888; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px; }
.machine-value { font-size:14px; color:#00ffaa; font-family:monospace; word-break:break-all; }
.copy-btn { background:#00ff8822; border:1px solid #00ff8844; color:#00ffaa; border-radius:6px; padding:4px 12px; font-size:12px; cursor:pointer; margin-top:8px; }
.copy-btn:hover { background:#00ff8833; }

/* Form */
.form-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }
.form-group { display:flex; flex-direction:column; gap:6px; }
.form-group label { font-size:12px; color:#8888cc; text-transform:uppercase; letter-spacing:0.5px; }
.form-group input, .form-group select { background:#0a0a20; border:1px solid #333366; border-radius:8px; padding:10px 14px; color:#e0e0e0; font-size:14px; outline:none; transition:border 0.2s; }
.form-group input:focus, .form-group select:focus { border-color:#00f0ff55; }
.form-group input.large { font-family:monospace; font-size:13px; letter-spacing:0.5px; }

.btn { background:linear-gradient(135deg,#00f0ff22,#00f0ff11); border:1px solid #00f0ff55; color:#00f0ff; border-radius:10px; padding:12px 24px; font-size:15px; font-weight:600; cursor:pointer; transition:all 0.2s; }
.btn:hover { background:linear-gradient(135deg,#00f0ff44,#00f0ff22); border-color:#00f0ff; transform:translateY(-1px); box-shadow:0 4px 16px #00f0ff33; }
.btn-generate { background:linear-gradient(135deg,#00f0ff,#0099cc); color:#000; font-weight:700; width:100%; margin-top:16px; font-size:16px; }
.btn-generate:hover { background:linear-gradient(135deg,#33f5ff,#00bbee); }

/* Generated Key */
.key-result { background:#0a0a20; border:2px solid #00f0ff44; border-radius:12px; padding:24px; margin-top:16px; display:none; text-align:center; }
.key-result.show { display:block; animation:pop 0.3s ease; }
@keyframes pop { 0%{transform:scale(0.95);opacity:0} 100%{transform:scale(1);opacity:1} }
.key-label { font-size:11px; color:#00f0ff88; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px; }
.key-value { font-size:20px; font-family:'Courier New',monospace; color:#00f0ff; letter-spacing:2px; font-weight:700; background:#00f0ff11; padding:12px 20px; border-radius:8px; display:inline-block; border:1px solid #00f0ff33; word-break:break-all; }
.key-actions { margin-top:16px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
.btn-copy { background:#00f0ff22; border:1px solid #00f0ff55; color:#00f0ff; border-radius:8px; padding:10px 24px; font-size:14px; cursor:pointer; }
.btn-copy:hover { background:#00f0ff33; }
.btn-save { background:#00ff8822; border:1px solid #00ff8855; color:#00ffaa; border-radius:8px; padding:10px 24px; font-size:14px; cursor:pointer; }
.btn-save:hover { background:#00ff8833; }
.saved-msg { color:#00ffaa; font-size:14px; margin-top:12px; animation:fade 2s forwards; }
@keyframes fade { 0%,60%{opacity:1} 100%{opacity:0} }

/* Clients Table */
.table-wrap { overflow-x:auto; }
table { width:100%; border-collapse:collapse; }
th { text-align:left; padding:10px 14px; font-size:11px; color:#8888cc; text-transform:uppercase; letter-spacing:0.5px; border-bottom:1px solid #00f0ff22; }
td { padding:12px 14px; font-size:13px; border-bottom:1px solid #ffffff08; }
tr:hover { background:#ffffff06; }
.status-active { color:#00ffaa; font-weight:600; }
.status-suspended { color:#ff4466; font-weight:600; }
.status-expiring { color:#ffaa00; font-weight:600; }
.key-cell { font-family:monospace; font-size:12px; color:#00f0ff88; }
.actions { display:flex; gap:6px; }
.action-btn { background:#ffffff0a; border:1px solid #ffffff22; color:#aaa; border-radius:5px; padding:3px 10px; font-size:11px; cursor:pointer; }
.action-btn:hover { background:#ffffff18; }

/* Stats */
.stats { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }
.stat { background:#111128; border:1px solid #00f0ff22; border-radius:12px; padding:20px; text-align:center; }
.stat-num { font-size:32px; font-weight:900; background:linear-gradient(90deg,#00f0ff,#ff00aa); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.stat-label { font-size:11px; color:#888; text-transform:uppercase; letter-spacing:1px; margin-top:4px; }

/* Toast */
.toast { position:fixed; bottom:30px; right:30px; background:#111128; border:1px solid #00f0ff44; color:#00f0ff; padding:14px 24px; border-radius:10px; font-size:14px; display:none; z-index:100; box-shadow:0 4px 20px #00000080; }
.toast.show { display:block; animation:slide 0.3s ease; }
@keyframes slide { from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1} }
</style>
</head>
<body>

<div class="header">
  <div class="logo">AI24x7</div>
  <div>
    <div class="tagline">License Generator — Factory Edition</div>
  </div>
  <div style="margin-left:auto; font-size:13px; color:#00f0ff88;">
    Server: 43.242.224.231
  </div>
</div>

<div class="container">

  <!-- Stats -->
  <div class="stats" id="stats"></div>

  <!-- This Machine -->
  <div class="card this-machine">
    <div class="card-title">💻 This Server Machine</div>
    <div class="machine-grid">
      <div class="machine-box">
        <div class="machine-label">Machine ID (MAC-based)</div>
        <div class="machine-value" id="this-machine-id">Loading...</div>
        <button class="copy-btn" onclick="copyText('this-machine-id')">📋 Copy</button>
      </div>
      <div class="machine-box">
        <div class="machine-label">Your Key (This Machine)</div>
        <div class="machine-value" id="this-machine-key" style="font-size:12px;">—</div>
        <button class="copy-btn" onclick="copyText('this-machine-key')">📋 Copy</button>
      </div>
    </div>
  </div>

  <!-- Generate New License -->
  <div class="card">
    <div class="card-title">🔑 Generate New License</div>
    <div class="form-grid">
      <div class="form-group" style="grid-column:span 2;">
        <label>Machine ID</label>
        <input class="large" type="text" id="mid" placeholder="38FBDDE984330E50C02382E647C576B7" />
      </div>
      <div class="form-group">
        <label>Plan</label>
        <select id="plan">
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
          <option value="lifetime">Lifetime</option>
        </select>
      </div>
      <div class="form-group">
        <label>Max Cameras</label>
        <select id="max_cams">
          <option value="4">4 Cameras</option>
          <option value="8">8 Cameras</option>
          <option value="16">16 Cameras</option>
          <option value="50">50 Cameras</option>
          <option value="999">Unlimited</option>
        </select>
      </div>
      <div class="form-group">
        <label>Client Name</label>
        <input type="text" id="client_name" placeholder="Factory Name / Company" />
      </div>
      <div class="form-group">
        <label>Payment Due</label>
        <input type="date" id="due_date" />
      </div>
    </div>
    <button class="btn btn-generate" onclick="generate()">⚡ Generate License Key</button>

    <div class="key-result" id="key-result">
      <div class="key-label">Your Generated License Key</div>
      <div class="key-value" id="generated-key"></div>
      <div class="key-actions">
        <button class="btn-copy" onclick="copyKey()">📋 Copy Key</button>
        <button class="btn-save" onclick="saveToDB()">💾 Save to Database</button>
      </div>
      <div class="saved-msg" id="saved-msg" style="display:none;">✅ Saved to database!</div>
    </div>
  </div>

  <!-- All Licenses -->
  <div class="card">
    <div class="card-title">📋 All Licenses</div>
    <div class="table-wrap">
      <table id="clients-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Client Name</th>
            <th>Machine ID</th>
            <th>License Key</th>
            <th>Plan</th>
            <th>Cameras</th>
            <th>Payment Due</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="clients-body"></tbody>
      </table>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let currentKey = '';

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

function copyText(id) {
  const text = document.getElementById(id).textContent;
  navigator.clipboard.writeText(text).then(() => toast('Copied: ' + text));
}

function copyKey() {
  navigator.clipboard.writeText(currentKey).then(() => toast('Key copied!'));
}

async function generate() {
  const mid = document.getElementById('mid').value.trim();
  if (!mid) { toast('Machine ID is required!'); return; }
  const plan = document.getElementById('plan').value;
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({machine_id: mid, plan})
  });
  const data = await res.json();
  if (data.key) {
    currentKey = data.key;
    document.getElementById('generated-key').textContent = data.key;
    document.getElementById('key-result').classList.add('show');
    document.getElementById('saved-msg').style.display = 'none';
    toast('Key generated!');
  }
}

async function saveToDB() {
  const mid = document.getElementById('mid').value.trim();
  const client_name = document.getElementById('client_name').value.trim() || 'Unnamed Client';
  const plan = document.getElementById('plan').value;
  const max_cams = parseInt(document.getElementById('max_cams').value);
  const due_date = document.getElementById('due_date').value;
  if (!currentKey) return;
  const res = await fetch('/api/save', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({machine_id: mid, license_key: currentKey, client_name, plan, max_cameras: max_cams, payment_due_date: due_date})
  });
  const data = await res.json();
  if (data.success) {
    document.getElementById('saved-msg').style.display = 'block';
    loadClients();
    loadStats();
  } else {
    toast('Error: ' + (data.error || 'Unknown error'));
  }
}

async function loadClients() {
  const res = await fetch('/api/clients');
  const clients = await res.json();
  const tbody = document.getElementById('clients-body');
  tbody.innerHTML = clients.map((c,i) => {
    const status = c.is_locked ? 'suspended' : (new Date(c.payment_due_date) < new Date() ? 'expiring' : 'active');
    const statusClass = 'status-' + status;
    const statusLabel = status.charAt(0).toUpperCase() + status.slice(1);
    const daysLeft = Math.ceil((new Date(c.payment_due_date) - new Date()) / 86400000);
    const dueDisplay = daysLeft > 0 ? `${daysLeft}d left` : 'OVERDUE';
    return `<tr>
      <td>${i+1}</td>
      <td><b>${c.client_name || '—'}</b></td>
      <td style="font-family:monospace;font-size:11px;color:#8888cc">${c.machine_id}</td>
      <td class="key-cell">${c.license_key}</td>
      <td>${c.plan}</td>
      <td>${c.max_cameras}</td>
      <td><span style="color:${daysLeft<7?'#ffaa00':'#888'}">${c.payment_due_date} (${dueDisplay})</span></td>
      <td><span class="${statusClass}">● ${statusLabel}</span></td>
      <td class="actions">
        <button class="action-btn" onclick="revoke('${c.machine_id}')">Revoke</button>
        <button class="action-btn" onclick="suspend('${c.machine_id}')">Suspend</button>
      </td>
    </tr>`;
  }).join('');
}

async function loadStats() {
  const res = await fetch('/api/stats');
  const s = await res.json();
  document.getElementById('stats').innerHTML = `
    <div class="stat"><div class="stat-num">${s.total}</div><div class="stat-label">Total</div></div>
    <div class="stat"><div class="stat-num">${s.active}</div><div class="stat-label">Active</div></div>
    <div class="stat"><div class="stat-num">${s.expiring_soon}</div><div class="stat-label">Expiring 7d</div></div>
    <div class="stat"><div class="stat-num">${s.suspended}</div><div class="stat-label">Suspended</div></div>
  `;
}

async function loadThisMachine() {
  const res = await fetch('/api/this_machine');
  const data = await res.json();
  document.getElementById('this-machine-id').textContent = data.machine_id;
  document.getElementById('this-machine-key').textContent = data.license_key;
}

async function revoke(mid) {
  if (!confirm('Revoke license for this machine?')) return;
  await fetch('/api/revoke', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({machine_id:mid})});
  loadClients(); loadStats();
}

async function suspend(mid) {
  await fetch('/api/suspend', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({machine_id:mid})});
  loadClients(); loadStats();
}

loadClients();
loadStats();
loadThisMachine();
</script>
</body>
</html>"""

# API Routes
routes = web.RouteTableDef()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@routes.get('/')
async def index(request):
    return web.Response(text=HTML, content_type='text/html')

@routes.get('/api/this_machine')
async def this_machine(request):
    mid = get_mac_id()
    key = make_key(mid)
    return web.json_response({'machine_id': mid, 'license_key': key})

@routes.post('/api/generate')
async def api_generate(request):
    data = await request.json()
    mid = data.get('machine_id', '').strip()
    plan = data.get('plan', 'monthly')
    if not mid or len(mid) < 8:
        return web.json_response({'error': 'Invalid Machine ID'}, status=400)
    days = 365 if plan == 'yearly' else (3650 if plan == 'lifetime' else 30)
    key = make_key(mid, days)
    return web.json_response({'key': key, 'machine_id': mid, 'plan': plan})

@routes.post('/api/save')
async def api_save(request):
    data = await request.json()
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("""INSERT OR REPLACE INTO license_clients 
            (machine_id, license_key, client_name, plan, payment_due_date, max_cameras, payment_status, activated_at, last_payment_check)
            VALUES (?, ?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'))
        """, (data['machine_id'], data['license_key'], data.get('client_name','Unnamed'),
              data.get('plan','monthly'), data.get('payment_due_date',''), data.get('max_cameras',4)))
        conn.commit()
        conn.close()
        return web.json_response({'success': True})
    except Exception as e:
        return web.json_response({'success': False, 'error': str(e)}, status=500)

@routes.get('/api/clients')
async def api_clients(request):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM license_clients ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return web.json_response(rows)

@routes.get('/api/stats')
async def api_stats(request):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM license_clients")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM license_clients WHERE is_locked=0 AND payment_status='active'")
    active = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM license_clients WHERE is_locked=1")
    suspended = c.fetchone()[0]
    conn.close()
    import datetime as dt
    exp_soon = 0  # simplified
    return web.json_response({'total': total, 'active': active, 'suspended': suspended, 'expiring_soon': exp_soon})

@routes.post('/api/revoke')
async def api_revoke(request):
    data = await request.json()
    mid = data.get('machine_id', '')
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE license_clients SET is_locked=1, lock_reason='admin_revoked' WHERE machine_id=?", (mid,))
    conn.commit()
    conn.close()
    return web.json_response({'success': True})

@routes.post('/api/suspend')
async def api_suspend(request):
    data = await request.json()
    mid = data.get('machine_id', '')
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE license_clients SET is_locked=1, lock_reason='payment_due' WHERE machine_id=?", (mid,))
    conn.commit()
    conn.close()
    return web.json_response({'success': True})

async def main():
    init_db()
    print("License Generator starting on port 5060...")
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5060)
    await site.start()
    print("License Generator: http://43.242.224.231:5060")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
