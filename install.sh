#!/bin/bash
# =============================================================================
# AI24x7 FACTORY EDITION - ONE-CLICK INSTALL
# =============================================================================
# Usage: curl -fsSL https://raw.githubusercontent.com/Gogreenraghav/ai24x7-factory-edition/main/install.sh | bash
# Or:   bash <(curl -fsSL https://raw.githubusercontent.com/Gogreenraghav/ai24x7-factory-edition/main/install.sh)
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Config
REPO="https://github.com/Gogreenraghav/ai24x7-factory-edition.git"
BRANCH="main"
INSTALL_DIR="/opt/ai24x7-factory"
LOG_FILE="/var/log/ai24x7-factory-install.log"
LICENSE_SERVER="http://43.242.224.231:5053"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
    echo "[$(date)] $1" >> "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "[$(date)] SUCCESS: $1" >> "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    echo "[$(date)] WARN: $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    echo "[$(date)] ERROR: $1" >> "$LOG_FILE"
}

header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}  🏭  AI24x7 FACTORY EDITION - INSTALLER${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        warn "Root privileges recommended. Retrying with sudo..."
        exec sudo bash "$0" "$@"
    fi
}

# =============================================================================
# SYSTEM CHECK
# =============================================================================

check_system() {
    header
    echo -e "${BOLD}🔍 Checking System Requirements...${NC}"
    echo ""

    # OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS="$ID"
        VER="$VERSION_ID"
        log "OS: $PRETTY_NAME"
    else
        OS="unknown"
        warn "Cannot detect OS"
    fi

    # Python
    if command -v python3 &> /dev/null; then
        PYVER=$(python3 --version 2>&1)
        log "$PYVER ✅"
    else
        error "Python3 not found. Installing..."
        if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
            apt-get update && apt-get install -y python3 python3-pip python3-venv
        elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
            yum install -y python3 python3-pip
        else
            error "Unsupported OS. Please install Python 3.10+ manually."
            exit 1
        fi
    fi

    # RAM
    RAM_TOTAL=$(free -m | awk '/^Mem:/{print $2}')
    RAM_FREE=$(free -m | awk '/^Mem:/{print $7}')
    log "RAM: ${RAM_TOTAL}MB total, ${RAM_FREE}MB free"

    if [[ $RAM_TOTAL -lt 4096 ]]; then
        warn "RAM < 4GB. Performance may be slow."
    fi

    # Disk
    DISK_AVAIL=$(df -h / | awk 'NR==2 {print $4}')
    log "Disk available: $DISK_AVAIL"
    if [[ $(df / | awk 'NR==2 {print $4}' | sed 's/[A-Z]//') -lt 10 ]]; then
        warn "Low disk space. Need at least 10GB."
    fi

    # GPU
    echo ""
    if command -v nvidia-smi &> /dev/null; then
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null | head -1 | awk '{print $1}')
        log "GPU: $GPU_NAME (${GPU_MEM}MB VRAM) ✅"
        HAS_GPU=1
    else
        warn "No NVIDIA GPU detected. Will use CPU mode (slower)."
        HAS_GPU=0
    fi

    # Internet
    echo ""
    if curl -s --max-time 5 https://github.com > /dev/null 2>&1; then
        log "Internet: Connected ✅"
    else
        warn "No internet. Some features may not work."
    fi

    echo ""
    read -p "Press ENTER to continue or Ctrl+C to cancel... "
}

# =============================================================================
# INSTALL DEPENDENCIES
# =============================================================================

install_dependencies() {
    header
    echo -e "${BOLD}📦 Installing System Dependencies...${NC}"
    echo ""

    log "Updating package lists..."
    if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        apt-get install -y -qq \
            python3-pip python3-venv \
            git curl wget ffmpeg \
            libgl1-mesa-glx libglib2.0-0 \
            libsm6 libxext6 libxrender-dev \
            portaudio19-dev \
            net-tools \
            2>/dev/null || true
    elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "rocky" ]]; then
        yum install -y -q python3-pip git curl wget ffmpeg 2>/dev/null || true
    fi

    success "System dependencies installed"
}

# =============================================================================
# CUDA & DRIVERS
# =============================================================================

install_cuda() {
    if [[ $HAS_GPU -eq 1 ]]; then
        header
        echo -e "${BOLD}🟢 NVIDIA GPU Detected - Checking CUDA...${NC}"
        echo ""

        CUDA_VERSION=$(nvcc --version 2>/dev/null | grep "release" | awk '{print $5}' | sed 's/,//')
        if [[ -n "$CUDA_VERSION" ]]; then
            log "CUDA already installed: $CUDA_VERSION ✅"
        else
            warn "CUDA not found in PATH. Checking system CUDA..."
            if [[ -d /usr/local/cuda ]]; then
                CUDA_VERSION=$(cat /usr/local/cuda/version.txt 2>/dev/null | grep -oP '\d+\.\d+' | head -1)
                log "System CUDA: $CUDA_VERSION ✅"
            else
                warn "CUDA not found. Installing PyTorch with CPU-only mode."
                warn "For GPU acceleration, install CUDA toolkit separately."
            fi
        fi

        # Check cuDNN
        if [[ -f /usr/local/cuda/lib64/libcudnn.so ]]; then
            log "cuDNN: Found ✅"
        else
            warn "cuDNN not found. GPU performance may be limited."
        fi
    fi
}

# =============================================================================
# PYTHON ENVIRONMENT
# =============================================================================

setup_python() {
    header
    echo -e "${BOLD}🐍 Setting up Python Environment...${NC}"
    echo ""

    VENV_DIR="$INSTALL_DIR/venv"

    if [[ -d "$VENV_DIR" ]]; then
        warn "Virtual environment exists. Recreating..."
        rm -rf "$VENV_DIR"
    fi

    log "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    success "Virtual environment created: $VENV_DIR"

    log "Upgrading pip..."
    "$VENV_DIR/bin/pip" install --upgrade pip -q

    echo ""
    log "Installing Python packages..."

    # Core packages
    PACKAGES=(
        "torch==2.2.0"
        "torchvision==0.17.0"
        "ultralytics>=8.2.0"
        "opencv-python>=4.9.0"
        "fastapi>=0.110.0"
        "uvicorn[standard]>=0.27.0"
        "streamlit>=1.33.0"
        "python-telegram-bot>=21.0"
        "gtts>=2.5.0"
        "edge-tts>=6.1.0"
        "python-dotenv>=1.0.0"
        "requests>=2.31.0"
        "pillow>=10.3.0"
        "numpy>=1.26.0"
        "psutil>=5.9.0"
        "schedule>=1.2.0"
        "httpx>=0.27.0"
        "pydantic>=2.6.0"
    )

    for pkg in "${PACKAGES[@]}"; do
        PKG_NAME=$(echo "$pkg" | cut -d'=' -f1)
        echo -n "  Installing $PKG_NAME... "
        if [[ $HAS_GPU -eq 1 ]]; then
            "$VENV_DIR/bin/pip" install "$pkg" -q --extra-index-url https://download.pytorch.org/whl/cu121 2>/dev/null && echo "✅" || echo "⚠️"
        else
            "$VENV_DIR/bin/pip" install "$pkg" -q 2>/dev/null && echo "✅" || echo "⚠️"
        fi
    done

    success "Python packages installed"
}

# =============================================================================
# DOWNLOAD & SETUP CODE
# =============================================================================

download_code() {
    header
    echo -e "${BOLD}📥 Downloading AI24x7 Factory Edition...${NC}"
    echo ""

    if [[ -d "$INSTALL_DIR/.git" ]]; then
        warn "Code already exists. Updating..."
        cd "$INSTALL_DIR"
        git pull origin "$BRANCH" 2>/dev/null || true
    else
        log "Cloning repository..."
        rm -rf "$INSTALL_DIR"
        git clone --depth 1 -b "$BRANCH" "$REPO" "$INSTALL_DIR"
        success "Code downloaded to $INSTALL_DIR"
    fi

    # Copy venv into install dir
    if [[ -d /opt/ai24x7-factory/venv ]]; then
        ln -sf /opt/ai24x7-factory/venv "$INSTALL_DIR/venv" 2>/dev/null || true
    fi
}

# =============================================================================
# AI MODELS DOWNLOAD
# =============================================================================

download_models() {
    header
    echo -e "${BOLD}🤖 Downloading AI Models...${NC}"
    echo ""

    MODELS_DIR="$INSTALL_DIR/models"
    mkdir -p "$MODELS_DIR"

    log "Models will be downloaded automatically on first run"
    log "to save bandwidth and install time."

    echo ""
    echo -e "  ${YELLOW}Models included:${NC}"
    echo -e "  • YOLOv8n - Person detection (auto-download, ~6MB)"
    echo -e "  • PPE Detector - Helmet/vest detection (v1 ready)"
    echo -e "  • Fire Detector - Fire/smoke detection (v1 ready)"
    echo -e "  • ANPR Model - Number plate recognition (v1 ready)"
    echo ""

    # Pre-download YOLOv8n
    echo -n "  Pre-downloading YOLOv8n... "
    if "$INSTALL_DIR/venv/bin/python" -c "from ultralytics import YOLOv8; print('ok')" 2>/dev/null | grep -q ok; then
        "$INSTALL_DIR/venv/bin/python" -c "from ultralytics import YOLOv8; YOLOv8('yolov8n.pt')" 2>/dev/null && echo "✅" || echo "⚠️ (will download on first run)"
    else
        echo "⚠️"
    fi

    success "Models ready"
}

# =============================================================================
# CONFIGURATION WIZARD
# =============================================================================

setup_config() {
    header
    echo -e "${BOLD}⚙️  Configuration Wizard${NC}"
    echo ""

    CONFIG_FILE="$INSTALL_DIR/config.json"
    DEFAULT_PORT=5056

    # Factory name
    echo -e "${CYAN}🏭 FACTORY SETUP${NC}"
    echo ""
    read -p "Factory Name [My Factory]: " FACTORY_NAME
    FACTORY_NAME=${FACTORY_NAME:-My Factory}

    # License key
    echo ""
    echo -e "${CYAN}🔐 LICENSE SETUP${NC}"
    echo ""
    echo "Get your license key from: https://ai24x7.cloud/license"
    echo "Format: FACTORY-XXXX-XXXX-XXXX-XXXX"
    echo ""
    read -p "Enter License Key (or press ENTER for demo mode): " LICENSE_KEY

    if [[ -n "$LICENSE_KEY" ]]; then
        echo "LICENSE_KEY=$LICENSE_KEY" > "$INSTALL_DIR/.env"
        success "License key saved"
    else
        warn "No license key. Running in DEMO mode."
        echo "LICENSE_KEY=demo" > "$INSTALL_DIR/.env"
    fi

    # Cameras
    echo ""
    echo -e "${CYAN}📹 CAMERA SETUP${NC}"
    echo ""
    read -p "Number of cameras [1]: " NUM_CAMERAS
    NUM_CAMERAS=${NUM_CAMERAS:-1}

    CAMERAS="["
    for i in $(seq 1 $NUM_CAMERAS); do
        echo ""
        echo "  Camera $i:"
        read -p "  Name [Camera $i]: " CAM_NAME
        CAM_NAME=${CAM_NAME:-Camera $i}
        read -p "  RTSP URL (or press ENTER to skip): " RTSP_URL

        if [[ -n "$RTSP_URL" ]]; then
            CAMERAS+="{\"id\":$i,\"name\":\"$CAM_NAME\",\"rtsp\":\"$RTSP_URL\"}"
        else
            CAMERAS+="{\"id\":$i,\"name\":\"$CAM_NAME\",\"rtsp\":\"demo\"}"
        fi
        if [[ $i -lt $NUM_CAMERAS ]]; then CAMERAS+=","; fi
    done
    CAMERAS+="]"

    # Alerts
    echo ""
    echo -e "${CYAN}📱 ALERT SETUP${NC}"
    echo ""
    read -p "Telegram Bot Token (or ENTER to skip): " TG_TOKEN
    read -p "Telegram Chat ID: " TG_CHAT_ID
    read -p "SMS API Key (Damini/Fast2SMS): " SMS_API_KEY
    read -p "Admin WhatsApp number (for alerts): " ADMIN_PHONE

    # Build config JSON
    cat > "$CONFIG_FILE" << CONFIGEOF
{
    "factory": {
        "name": "$FACTORY_NAME",
        "license_key": "${LICENSE_KEY:-demo}",
        "install_date": "$(date -I)"
    },
    "server": {
        "host": "0.0.0.0",
        "port": $DEFAULT_PORT,
        "license_server": "$LICENSE_SERVER"
    },
    "cameras": $CAMERAS,
    "alerts": {
        "telegram": {
            "enabled": $([ -n "$TG_TOKEN" ] && echo "true" || echo "false"),
            "bot_token": "${TG_TOKEN:-}",
            "chat_id": "${TG_CHAT_ID:-}"
        },
        "sms": {
            "enabled": $([ -n "$SMS_API_KEY" ] && echo "true" || echo "false"),
            "api_key": "${SMS_API_KEY:-}",
            "recipients": ["${ADMIN_PHONE:-}"]
        }
    },
    "safety": {
        "ppe_check": true,
        "fire_check": true,
        "fall_check": true,
        "ppe_rules": {
            "helmet": true,
            "vest": true,
            "gloves": false,
            "shoes": true
        }
    },
    "shifts": {
        "morning": {"start": "06:00", "end": "14:00"},
        "afternoon": {"start": "14:00", "end": "22:00"},
        "night": {"start": "22:00", "end": "06:00"}
    }
}
CONFIGEOF

    success "Configuration saved: $CONFIG_FILE"
}

# =============================================================================
# SYSTEMD SERVICE
# =============================================================================

setup_service() {
    header
    echo -e "${BOLD}🚀 Setting up System Service...${NC}"
    echo ""

    # Create systemd service
    cat > /etc/systemd/system/ai24x7-factory.service << SERVICEEOF
[Unit]
Description=AI24x7 Factory Edition
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
Environment=PYTHONPATH=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/factory/main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Watchdog - restart if no heartbeat for 5 minutes
WatchdogSec=300

[Install]
WantedBy=multi-user.target
SERVICEEOF

    systemctl daemon-reload
    systemctl enable ai24x7-factory.service
    success "Systemd service created: ai24x7-factory.service"
}

# =============================================================================
# FIREWALL
# =============================================================================

setup_firewall() {
    header
    echo -e "${BOLD}🛡️  Firewall Setup${NC}"
    echo ""

    PORT=$(grep -o '"port": [0-9]*' "$INSTALL_DIR/config.json" 2>/dev/null | grep -o '[0-9]*' | head -1)
    PORT=${PORT:-5056}

    # UFW
    if command -v ufw &> /dev/null; then
        log "Configuring UFW firewall..."
        ufw allow $PORT/tcp comment "AI24x7 Factory" 2>/dev/null || true
        ufw allow 5052/tcp comment "AI24x7 Dashboard" 2>/dev/null || true
        success "UFW configured"
    fi

    # iptables
    if command -v iptables &> /dev/null; then
        iptables -C INPUT -p tcp --dport $PORT -j ACCEPT 2>/dev/null || \
        iptables -A INPUT -p tcp --dport $PORT -j ACCEPT 2>/dev/null
        log "iptables configured for port $PORT"
    fi

    success "Firewall configured"
}

# =============================================================================
# START SERVICES
# =============================================================================

start_services() {
    header
    echo -e "${BOLD}🎯 Starting Services...${NC}"
    echo ""

    systemctl start ai24x7-factory.service 2>/dev/null || true
    sleep 3

    if systemctl is-active --quiet ai24x7-factory.service; then
        success "AI24x7 Factory service: RUNNING ✅"
    else
        warn "Service started but may need a moment..."
        sleep 5
    fi

    # Dashboard
    DASHBOARD_PORT=5052
    log "Starting dashboard on port $DASHBOARD_PORT..."
    nohup "$INSTALL_DIR/venv/bin/streamlit" run \
        "$INSTALL_DIR/factory/dashboard/factory_dashboard.py" \
        --server.port $DASHBOARD_PORT \
        --server.address 0.0.0.0 \
        --server.headless true \
        > /var/log/ai24x7-factory-dashboard.log 2>&1 &

    sleep 3
    success "Dashboard starting..."
}

# =============================================================================
# VERIFICATION
# =============================================================================

verify() {
    header
    echo -e "${BOLD}✅ Installation Verification${NC}"
    echo ""

    # Check service
    if systemctl is-active --quiet ai24x7-factory.service; then
        success "Service: RUNNING"
    else
        warn "Service: Check logs with: journalctl -u ai24x7-factory -n 20"
    fi

    # Check ports
    PORT=$(grep -o '"port": [0-9]*' "$INSTALL_DIR/config.json" 2>/dev/null | grep -o '[0-9]*' | head -1)
    PORT=${PORT:-5056}
    if ss -tlnp 2>/dev/null | grep -q ":$PORT "; then
        success "API Server: LISTENING on port $PORT"
    else
        warn "API Server: Not yet listening (may take 30 seconds)"
    fi

    # Check dashboard
    if ss -tlnp 2>/dev/null | grep -q ":5052 "; then
        success "Dashboard: http://$(hostname -I | awk '{print $1}'):5052"
    else
        warn "Dashboard: Starting (wait 30 seconds)"
    fi

    # Check license
    LICENSE_KEY=$(grep "LICENSE_KEY" "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2)
    if [[ "$LICENSE_KEY" == "demo" ]]; then
        warn "License: DEMO MODE (limited features)"
    else
        success "License: CONFIGURED"
    fi
}

# =============================================================================
# USAGE GUIDE
# =============================================================================

show_guide() {
    header
    echo -e "${BOLD}🎉 INSTALLATION COMPLETE!${NC}"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}       🏭 AI24x7 FACTORY EDITION IS READY!        ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    PORT=$(grep -o '"port": [0-9]*' "$INSTALL_DIR/config.json" 2>/dev/null | grep -o '[0-9]*' | head -1)
    PORT=${PORT:-5056}
    IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")

    echo -e "${BOLD}📍 ACCESS URLs:${NC}"
    echo -e "  🌐 Dashboard: ${CYAN}http://$IP:5052${NC}"
    echo -e "  🔌 API:       ${CYAN}http://$IP:$PORT${NC}"
    echo -e "  📊 Health:    ${CYAN}http://$IP:$PORT/health${NC}"
    echo ""

    echo -e "${BOLD}🔧 USEFUL COMMANDS:${NC}"
    echo -e "  ${CYAN}systemctl status ai24x7-factory${NC}   - Check status"
    echo -e "  ${CYAN}systemctl restart ai24x7-factory${NC}   - Restart service"
    echo -e "  ${CYAN}journalctl -u ai24x7-factory -f${NC}  - View logs (Ctrl+C to exit)"
    echo -e "  ${CYAN}$INSTALL_DIR/venv/bin/python $INSTALL_DIR/factory/main.py${NC}  - Run manually"
    echo ""

    echo -e "${BOLD}📹 ADD CAMERAS:${NC}"
    echo -e "  Edit: ${CYAN}$INSTALL_DIR/config.json${NC}"
    echo -e "  Then: ${CYAN}systemctl restart ai24x7-factory${NC}"
    echo ""

    echo -e "${BOLD}🔄 UPDATE SYSTEM:${NC}"
    echo -e "  cd $INSTALL_DIR && git pull"
    echo -e "  systemctl restart ai24x7-factory"
    echo ""

    echo -e "${BOLD}📄 DOCUMENTATION:${NC}"
    echo -e "  ${CYAN}https://github.com/Gogreenraghav/ai24x7-factory-edition${NC}"
    echo ""

    LICENSE_KEY=$(grep "LICENSE_KEY" "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2)
    if [[ "$LICENSE_KEY" == "demo" ]]; then
        echo -e "${YELLOW}⚠️  DEMO MODE: Get a license key for full features${NC}"
        echo -e "    ${CYAN}https://ai24x7.cloud/license${NC}"
        echo ""
    fi

    echo -e "${BOLD}💬 SUPPORT:${NC}"
    echo -e "  Telegram: ${CYAN}@ai24x7_support${NC}"
    echo -e "  Email:    ${CYAN}support@ai24x7.cloud${NC}"
    echo ""
    echo -e "${GREEN}Thank you for choosing AI24x7 Factory Edition!${NC}"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    # Init
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"

    check_root "$@"
    check_system
    install_dependencies
    install_cuda
    setup_python
    download_code
    download_models
    setup_config
    setup_service
    setup_firewall
    start_services
    verify
    show_guide
}

main "$@"
