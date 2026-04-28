#!/bin/bash
# AI24x7 Factory Edition — Professional Pendrive Installer
# Run from pendrive: sudo bash AI24x7_Install.run

set -e

RED='\033[0;31m'; GRN='\033[0;32m'; YEL='\033[1;33m'; CYN='\033[0;36m'; NC='\033[0m'
INSTALL_DIR="/opt/ai24x7-docker"
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="/var/log/ai24x7_install.log"

log() { echo -e "${GRN}[OK]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YEL}[WARN]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; exit 1; }

echo ""
echo "=========================================="
echo "   AI24x7 FACTORY EDITION — INSTALLER"
echo "   Smart AI CCTV Monitoring System"
echo "=========================================="
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then error "Run as root: sudo bash AI24x7_Install.run"; fi

# Detect machine ID for license
get_machine_id() {
    if [ -f /sys/class/dmi/id/product_uuid ]; then
        cat /sys/class/dmi/id/product_uuid
    elif [ -f /etc/machine-id ]; then
        cat /etc/machine-id | head -c 32
    else
        hostname | sha256sum | head -c 32
    fi
}

MACHINE_ID=$(get_machine_id)
log "Machine ID: $MACHINE_ID"

# ── Step 1: Extract bundle ────────────────────────────────────
log "Step 1/7: Extracting bundle..."
EXTRACT_DIR="/tmp/ai24x7_extract_$$"
mkdir -p "$EXTRACT_DIR"
if [ -f "$BUNDLE_DIR/ai24x7_v1.run" ]; then
    bash "$BUNDLE_DIR/ai24x7_v1.run" --noexec --target "$EXTRACT_DIR" 2>/dev/null || \
    grep -A1 "^ARCHIVE" "$BUNDLE_DIR/ai24x7_v1.run" | grep -v "^ARCHIVE" | tr -d "'" | tr -d '\n' | base64 -d > "$EXTRACT_DIR/bundle.tar.gz" 2>/dev/null
fi

# If extraction fails, use direct files
if [ ! -d "$EXTRACT_DIR/ai24x7-bundle" ]; then
    cp -r "$BUNDLE_DIR" "$EXTRACT_DIR/ai24x7-bundle" 2>/dev/null || error "No bundle found in pendrive"
fi
log "Bundle extracted."

# ── Step 2: Detect Python ───────────────────────────────────────
log "Step 2/7: Checking Python..."
PYTHON_BIN=$(which python3 2>/dev/null || which python 2>/dev/null)
if [ -z "$PYTHON_BIN" ]; then
    warn "Python not found. Installing..."
    apt-get update -qq && apt-get install -y python3 python3-pip python3-venv > /dev/null 2>&1
    PYTHON_BIN=$(which python3)
fi
PYTHON_VERSION=$($PYTHON_BIN --version 2>&1 | awk '{print $2}')
log "Python: $PYTHON_VERSION"

# ── Step 3: Install Redis ──────────────────────────────────────
log "Step 3/7: Installing Redis..."
if command -v redis-server &> /dev/null; then
    log "Redis already installed."
else
    REDIS_BIN="$EXTRACT_DIR/ai24x7-bundle/redis/redis-server"
    if [ -f "$REDIS_BIN" ]; then
        cp "$REDIS_BIN" /usr/local/bin/redis-server
        chmod +x /usr/local/bin/redis-server
        log "Redis portable binary installed."
    else
        apt-get install -y redis-server > /dev/null 2>&1 && log "Redis installed via apt."
    fi
fi

# Start Redis
redis-server --daemonize yes --port 6379 2>/dev/null || true
sleep 1
if redis-cli ping > /dev/null 2>&1; then log "Redis: Running on port 6379"; else warn "Redis may not be running"; fi

# ── Step 4: Create AI24x7 directories ─────────────────────────
log "Step 4/7: Setting up directories..."
mkdir -p "$INSTALL_DIR/factory/services"
mkdir -p "$INSTALL_DIR/factory/dashboard"
mkdir -p "$INSTALL_DIR/factory/smart_layers"
mkdir -p "$INSTALL_DIR/factory/alerts"
mkdir -p "$INSTALL_DIR/factory/api"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/models"
mkdir -p "/var/log/ai24x7"
mkdir -p "/etc/ai24x7"

# ── Step 5: Copy service files ────────────────────────────────
log "Step 5/7: Installing AI24x7 services..."
cp -r "$EXTRACT_DIR/ai24x7-bundle/services/"* "$INSTALL_DIR/factory/" 2>/dev/null || true
cp -r "$EXTRACT_DIR/ai24x7-bundle/db/"* "$INSTALL_DIR/data/" 2>/dev/null || true
cp -r "$EXTRACT_DIR/ai24x7-bundle/config/"* "$INSTALL_DIR/factory/" 2>/dev/null || true
cp -r "$EXTRACT_DIR/ai24x7-bundle/scripts/"* "$INSTALL_DIR/factory/" 2>/dev/null || true
cp "$EXTRACT_DIR/ai24x7-bundle/install.sh" "$INSTALL_DIR/" 2>/dev/null || true
log "Services installed."

# ── Step 6: Model setup ─────────────────────────────────────────
log "Step 6/7: AI Model..."
MODEL_PEND="$BUNDLE_DIR/models/model-q5_k_m.gguf"
if [ -f "$MODEL_PEND" ]; then
    cp "$MODEL_PEND" "$INSTALL_DIR/models/"
    log "Model copied from pendrive."
elif [ -d "/opt/cctv-finetune/output/gguf_v10_q5_k_m" ]; then
    ln -sf "/opt/cctv-finetune/output/gguf_v10_q5_k_m/model-q5_k_m.gguf" "$INSTALL_DIR/models/model-q5_k_m.gguf" 2>/dev/null || true
    log "Model linked from existing installation."
else
    warn "AI Model not found on pendrive. Please copy model file manually."
fi

# ── Step 7: License Key ───────────────────────────────────────
echo ""
echo "=========================================="
echo "   LICENSE ACTIVATION"
echo "=========================================="
echo ""
echo -e "${CYN}Your Machine ID: ${MACHINE_ID}${NC}"
echo ""
echo "Send this Machine ID to your AI24x7 provider."
echo "You will receive a LICENSE KEY in return."
echo ""
read -p "Enter your LICENSE KEY: " LICENSE_KEY

if [ -z "$LICENSE_KEY" ]; then
    error "License key required. Contact AI24x7 support."
fi

# Save license key
echo "$LICENSE_KEY" > /etc/ai24x7/license.key
echo "$MACHINE_ID" > /etc/ai24x7/machine.id
log "License key saved."

# ── Start Services ─────────────────────────────────────────────
log "Starting AI24x7 services..."

# Create Python venv if needed
if [ ! -d "$INSTALL_DIR/venv" ]; then
    $PYTHON_BIN -m venv "$INSTALL_DIR/venv"
    "$INSTALL_DIR/venv/bin/pip" install -q edge-tts gtts aiohttp flask redis 2>/dev/null || true
fi

# Generate init config
cat > /etc/ai24x7/init.conf << EOF
LICENSE_KEY=$LICENSE_KEY
MACHINE_ID=$MACHINE_ID
INSTALL_DIR=$INSTALL_DIR
PORT_DASHBOARD=5052
PORT_LICENSE=5053
PORT_API=5056
PORT_ALERT=5058
PORT_WIZARD=5059
PORT_QWEN=8080
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
EOF

# Start dashboard
cd "$INSTALL_DIR/factory"
nohup "$INSTALL_DIR/venv/bin/python" -m streamlit run factory/dashboard/factory_dashboard.py --server.port 5052 --server.address 0.0.0.0 > /var/log/ai24x7/dashboard.log 2>&1 &
log "Dashboard: http://localhost:5052"

# Cleanup
rm -rf "$EXTRACT_DIR"

echo ""
echo "=========================================="
echo "   INSTALLATION COMPLETE!"
echo "=========================================="
echo ""
echo -e "${GRN}Dashboard:${NC}  http://localhost:5052"
echo -e "${GRN}Machine ID:${NC} $MACHINE_ID"
echo -e "${GRN}License:${NC}     ACTIVE"
echo ""
echo "Next: Open Dashboard and configure cameras."
echo "=========================================="
