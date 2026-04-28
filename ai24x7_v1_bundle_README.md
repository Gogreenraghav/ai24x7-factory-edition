# AI24x7 Factory Edition — Installer Bundle

## Quick Deploy
```bash
# Download the self-extracting installer (1.4 MB)
wget http://43.242.224.231/ai24x7_v1.run

# Run on any Ubuntu 20.04+ machine
chmod +x ai24x7_v1.run
sudo ./ai24x7_v1.run
```

## What it installs
- Redis Server (bundled, 2.6MB binary)
- Factory Dashboard (Streamlit, port 5052)
- Smart Layer API (4-layer CCTV system, port 5056)
- License Server v3.0 with enforcement (port 5053)
- License Client (auto-activation)
- Pre-configured SQLite database
- Systemd auto-start service

## Systemd Service
```bash
sudo systemctl restart ai24x7   # Restart all
sudo systemctl stop ai24x7       # Stop all
sudo journalctl -u ai24x7 -f     # View logs
```

## Ports
| Port | Service |
|------|---------|
| 5052 | Factory Dashboard |
| 5053 | License Server |
| 5056 | Smart Layer API |
| 5057 | License Admin Panel |
| 6379 | Redis Queue |

## License
(c) 2026 GOUP CONSULTANCY SERVICES LLP
Admin Key: AI24x7-ADMIN-2026