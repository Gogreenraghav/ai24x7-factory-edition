# AI24x7 Factory Edition 🏭

**Complete CCTV AI Surveillance System** — Fire Detection, PPE Compliance, ANPR, Face Recognition, Hindi+English Voice Alerts, Shift Reports, Equipment Monitoring.

## 🚀 Quick Start

### Docker (Recommended — Offline Capable)
```bash
# Download offline tarball from server:
# scp root@43.242.224.231:/opt/ai24x7-docker/ai24x7-factory-offline.tar .

# On any machine with Docker:
docker load -i ai24x7-factory-offline.tar
docker run -d --name ai24x7-factory --network host \
  -v ./data:/data \
  ai24x7-factory:latest
```

### Or build from source:
```bash
git clone https://github.com/Gogreenraghav/ai24x7-factory-edition.git
cd ai24x7-factory-edition
docker compose up -d
```

## 📦 What's Inside

| Service | Port | Description |
|---------|------|-------------|
| Factory Dashboard | 5052 | Streamlit UI — **Day/Night Theme** |
| CCTV API | 5050 | AI-powered CCTV analysis (Qwen3VL-8B) |
| License Server | 5053 | License validation & plans |
| Camera API | 5054 | Real-time stream processing |
| Payment Server | 5055 | Stripe payment integration |
| AI Server | 8080 | Local LLM inference |

## 🎨 Features

- 📊 **Dashboard** — 8 tabs: Overview, Camera Feeds, Safety Alerts, PPE Compliance, Shift Reports, Equipment, Notifications, Settings
- 🌙 **Day/Night Theme** — One-click toggle
- 🗄️ **SQLite Database** — Cameras, alerts, workers, violations, equipment, shifts
- 🔥 **Fire Detection** — Color-based + AI
- 🪖 **PPE Compliance** — Helmet, vest, gloves, shoes
- 🔄 **Shift Reports** — Auto-generated
- 📱 **Telegram Alerts** — Instant notifications
- 💳 **Stripe Payments** — Factory Lite/Pro/Enterprise plans

## 💰 Plans

| Plan | Cameras | Price/mo |
|------|---------|---------|
| Factory Lite | 4 | ₹2,999 |
| Factory Pro | 16 | ₹9,999 |
| Enterprise | Unlimited | ₹24,999 |

## 🌐 Access URLs

- Dashboard: `http://YOUR_IP:5052`
- API Docs: `http://YOUR_IP:5050/docs`
- License: `http://YOUR_IP:5053`
- Payment: `http://YOUR_IP:5055`

## 🔧 Offline Deployment

For air-gapped environments:
1. Download `ai24x7-factory-offline.tar` (514MB)
2. Transfer to offline machine
3. `docker load -i ai24x7-factory-offline.tar`
4. `docker compose up -d`

## 📁 Data Volumes

```yaml
./data/models      # AI models (GGUF)
./data/db          # SQLite databases
./data/logs        # Application logs
./data/config      # Configuration
./data/captures    # Snapshots
```

## 🔐 Security

- Change all tokens in `.env` before deployment
- Use Stripe LIVE keys in production
- Restrict port 5053 (License Server) to internal network

## 📞 Support

**GOUP CONSULTANCY SERVICES LLP**  
© 2026 — All rights reserved
