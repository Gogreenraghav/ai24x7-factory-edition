# AI24x7 Factory Edition 🏭

**Ready-Made Industrial AI Surveillance System**

> One-command install: `curl -fsSL https://raw.githubusercontent.com/Gogreenraghav/ai24x7-factory-edition/main/install.sh | bash`

AI-powered 24/7 factory monitoring with PPE compliance, fire detection, equipment monitoring, and automatic shift reports. **No technical knowledge required.**

---

## ⚡ Quick Install (5 Minutes)

```bash
# One command - everything automated!
curl -fsSL https://raw.githubusercontent.com/Gogreenraghav/ai24x7-factory-edition/main/install.sh | bash
```

The installer will:
- ✅ Detect your GPU (NVIDIA automatically)
- ✅ Install all dependencies
- ✅ Download AI models
- ✅ Configure cameras (wizard-style)
- ✅ Setup license key
- ✅ Configure alerts (Telegram, SMS)
- ✅ Install as system service (auto-start on boot)

---

## 🎯 What It Does

### Safety Features
| Feature | Description |
|---------|-------------|
| 🔥 Fire Detection | Detect fire/smoke in 2-3 seconds |
| 🪖 PPE Compliance | Check helmet, vest, gloves, shoes |
| 🏃 Fall Detection | Worker fall detection + alert |
| 🛢️ Spill Detection | Oil/chemical spill on floor |
| ⛔ Danger Zones | Restricted area monitoring |

### Operations
| Feature | Description |
|---------|-------------|
| 🚗 ANPR | Vehicle number plate recognition |
| ⚙️ Equipment Monitor | Machine running/stopped status |
| 📦 Production Count | Auto item counting via camera |
| 🔄 Shift Reports | Auto PDF reports at shift end |

### Alerts
| Channel | Status |
|---------|--------|
| 📱 SMS | Damini/Fast2SMS |
| 💬 WhatsApp | Business API |
| ✈️ Telegram | Bot alerts |
| 🔊 Voice | Hindi/English TTS announcements |

---

## 💰 Pricing

| Plan | Cameras | Price/Month |
|------|---------|-------------|
| Factory Lite | 4 | ₹2,999 |
| Factory Pro | 16 | ₹9,999 |
| Enterprise | Unlimited | ₹24,999 |

**Demo mode available without license key.**

---

## 🔐 License System

Every installation requires a license key:

```
Format: FACTORY-XXXX-XXXX-XXXX-XXXX
Hardware-bound: MAC + CPU ID
Cloud validated: license.go-up.in:5053
Grace period: 24 hours offline
```

Get license: https://ai24x7.cloud/license

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | None (CPU) | **NVIDIA RTX 3060 12GB** |
| RAM | 8GB | 16GB |
| Storage | 100GB | 500GB SSD |
| OS | Ubuntu 20.04+ / Windows 10+ | Ubuntu 22.04 LTS |
| Cameras | Any IP camera with RTSP | Hikvision/Dahua |

---

## 📋 Module Structure

```
ai24x7-factory/
├── factory/
│   ├── main.py              # Entry point
│   ├── license_client.py     # License protection ⚠️
│   ├── config.py            # Configuration
│   ├── safety/
│   │   ├── fire_detector.py  # 🔥 Fire/smoke
│   │   ├── ppe_detector.py   # 🪖 PPE compliance
│   │   └── fall_detector.py  # 🏃 Fall detection
│   ├── operations/
│   │   ├── anpr_camera.py    # 🚗 Number plates
│   │   ├── equipment_monitor.py  # ⚙️ Machine status
│   │   └── shift_manager.py  # 🔄 Shift tracking
│   ├── alerts/
│   │   ├── sms_alerts.py     # 📱 SMS
│   │   ├── telegram_alerts.py # ✈️ Telegram
│   │   └── tts_announcer.py # 🔊 Voice
│   └── reporting/
│       └── shift_report.py   # 📊 PDF reports
├── install.sh                # ⬆️ ONE-CLICK INSTALL
├── config.json              # Camera config
└── .env                    # License key
```

---

## 🚀 Usage

```bash
# After installation:
systemctl status ai24x7-factory    # Check status
systemctl restart ai24x7-factory   # Restart

# View logs:
journalctl -u ai24x7-factory -f

# Dashboard:
# Open: http://YOUR_IP:5052
```

---

## 🔧 Add Cameras

Edit `config.json`:

```bash
nano /opt/ai24x7-factory/config.json
systemctl restart ai24x7-factory
```

---

## 📖 Full Documentation

**Spec Document:** [AI24x7 Factory Edition - Complete Spec](https://docs.google.com/document/d/1Bls5HqGfUoY97JByLvEagDaYKgHeiM180ALqiVocCJ0/edit)

---

## 🏭 For Manufacturing

- Manufacturing plants
- Steel factories
- Chemical plants
- Textile mills
- Food processing
- Warehouses
- Construction sites

---

**Owner: GOUP CONSULTANCY SERVICES LLP**
**AI Assistant: Claude (Powered by AI24x7)**
**Version: 1.0.0**
