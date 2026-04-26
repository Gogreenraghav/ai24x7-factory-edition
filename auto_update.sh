#!/bin/bash
#==============================================================================
# AI24x7 Factory Edition - Auto-Update Script
# Location: /opt/ai24x7-factory/auto_update.sh
# 
# Usage: 
#   ./auto_update.sh              # Interactive
#   ./auto_update.sh --check      # Check only
#   ./auto_update.sh --force      # Force update
#   ./auto_update.sh --rollback   # Rollback last update
#==============================================================================

set -e
APP_DIR="/opt/ai24x7-factory"
REPO_URL="https://github.com/Gogreenraghav/ai24x7-factory-edition.git"
BACKUP_DIR="/opt/ai24x7-factory/backups"
LOG_FILE="/var/log/ai24x7_update.log"
ADMIN_TOKEN="${GITHUB_TOKEN:-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}"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"; }
ok()  { echo -e "${GREEN}[OK]${NC} $1"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

#==============================================================================
# PRE-FLIGHT CHECKS
#==============================================================================
preflight() {
    log "Running pre-flight checks..."
    
    if [ ! -d "$APP_DIR/.git" ]; then
        if [ ! -d "$APP_DIR" ]; then
            mkdir -p "$APP_DIR"
        fi
        log "Cloning repository first time..."
        git clone --depth=1 "$REPO_URL" "$APP_DIR" 2>/dev/null || \
        git clone "https://${ADMIN_TOKEN}@github.com/Gogreenraghav/ai24x7-factory-edition.git" "$APP_DIR"
        ok "Repository cloned"
    fi
    
    mkdir -p "$BACKUP_DIR"
    [ -f /opt/cctv-finetune/venv/bin/activate ] && source /opt/cctv-finetune/venv/bin/activate
    ok "Pre-flight complete"
}

#==============================================================================
# CHECK FOR UPDATES
#==============================================================================
check_updates() {
    log "Checking for updates..."
    cd "$APP_DIR"
    
    # Fetch latest
    git fetch origin main --quiet 2>/dev/null || true
    
    LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "")
    REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "")
    
    if [ "$LOCAL" = "$REMOTE" ] || [ -z "$REMOTE" ]; then
        ok "You are on the latest version"
        echo ""
        git log --oneline -1
        return 0
    else
        BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
        warn "Updates available! ($BEHIND commit(s) behind)"
        echo ""
        log "Your version:"
        git log --oneline -1
        echo ""
        log "Latest version:"
        git log --oneline origin/main -1
        echo ""
        echo "Run './auto_update.sh --force' to update"
        return 1
    fi
}

#==============================================================================
# CREATE BACKUP
#==============================================================================
backup_current() {
    log "Creating backup..."
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/backup_${TIMESTAMP}.tar.gz"
    
    # Exclude git, cache, temp files
    tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
        --exclude='.venv' --exclude='venv' \
        -czf "$BACKUP_FILE" -C "$APP_DIR" . 2>/dev/null || true
    
    # Save git revision for rollback
    if [ -d "$APP_DIR/.git" ]; then
        REVISION=$(git rev-parse HEAD)
        echo "$TIMESTAMP|$REVISION|$(git log --oneline -1)" > "$BACKUP_DIR/revision_${TIMESTAMP}.txt"
    fi
    
    # Keep only last 5 backups
    cd "$BACKUP_DIR" && ls -dt backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    
    ok "Backup saved: $BACKUP_FILE"
    echo "$BACKUP_FILE" > /tmp/ai24x7_last_backup
}

#==============================================================================
# PERFORM UPDATE
#==============================================================================
do_update() {
    log "Starting update..."
    cd "$APP_DIR"
    
    # Stash any local changes
    if git diff --quiet 2>/dev/null; then
        :  # No local changes
    else
        warn "Local changes detected, stashing..."
        git stash 2>/dev/null || true
    fi
    
    # Pull latest
    log "Pulling latest from GitHub..."
    if GIT_TOKEN="https://${ADMIN_TOKEN}@github.com/Gogreenraghav/ai24x7-factory-edition.git" \
       git pull origin main --quiet 2>&1; then
        ok "Code updated"
    else
        err "Git pull failed - check network/credentials"
        return 1
    fi
    
    # Install new dependencies
    if [ -f "$APP_DIR/requirements.txt" ]; then
        log "Installing dependencies..."
        pip install -r "$APP_DIR/requirements.txt" --quiet 2>&1 | tail -3 || true
        ok "Dependencies updated"
    fi
    
    # Update systemd service if needed
    if [ -f "$APP_DIR/install.sh" ]; then
        log "Refreshing systemd service..."
        cp "$APP_DIR/install.sh" /opt/ai24x7-factory/restart_services.sh 2>/dev/null || true
    fi
    
    # Restart services
    restart_services
    
    ok "Update complete!"
    echo ""
    log "Updated to:"
    git log --oneline -1
}

#==============================================================================
# RESTART SERVICES
#==============================================================================
restart_services() {
    log "Restarting AI24x7 services..."
    
    # Restart license client
    if systemctl is-active --quiet ai24x7-factory-license 2>/dev/null; then
        systemctl restart ai24x7-factory-license
        ok "License service restarted"
    fi
    
    # Restart main monitoring
    if systemctl is-active --quiet ai24x7-factory 2>/dev/null; then
        systemctl restart ai24x7-factory
        ok "Factory monitoring restarted"
    fi
    
    # Restart dashboard
    if pgrep -f "factory_dashboard.py" > /dev/null 2>&1; then
        pkill -f "factory_dashboard.py"
        sleep 2
        cd "$APP_DIR/factory/dashboard"
        nohup streamlit run factory_dashboard.py --server.port 5052 --server.headless true > /tmp/factory_dashboard.log 2>&1 &
        ok "Dashboard restarted on :5052"
    fi
    
    # Restart API if running
    if pgrep -f "factory_api.py" > /dev/null 2>&1; then
        pkill -f "factory_api.py"
        sleep 1
        nohup python3 "$APP_DIR/factory/api/factory_api.py" > /tmp/factory_api.log 2>&1 &
        ok "API restarted"
    fi
}

#==============================================================================
# ROLLBACK
#==============================================================================
rollback() {
    log "Rollback initiated..."
    
    LAST_BACKUP=$(ls -dt /tmp/ai24x7_last_backup 2>/dev/null | head -1)
    if [ -z "$LAST_BACKUP" ] || [ ! -f "$(cat $LAST_BACKUP 2>/dev/null)" ]; then
        # Find latest backup manually
        BACKUP_FILE=$(ls -dt "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1)
    else
        BACKUP_FILE=$(cat "$LAST_BACKUP")
    fi
    
    if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
        err "No backup found for rollback!"
        return 1
    fi
    
    warn "Rolling back to: $BACKUP_FILE"
    
    # Extract backup
    tar -xzf "$BACKUP_FILE" -C "$APP_DIR" 2>/dev/null
    
    # Restart services
    restart_services
    
    ok "Rollback complete!"
}

#==============================================================================
# SELF-UPDATE (update this script itself)
#==============================================================================
self_update() {
    log "Updating auto_update.sh itself..."
    SCRIPT_URL="https://raw.githubusercontent.com/Gogreenraghav/ai24x7-factory-edition/main/auto_update.sh"
    curl -fsSL "$SCRIPT_URL" -o /opt/ai24x7-factory/auto_update.sh 2>/dev/null && \
        chmod +x /opt/ai24x7-factory/auto_update.sh && ok "Script updated" || \
        warn "Could not update script (network issue)"
}

#==============================================================================
# VERSION INFO
#==============================================================================
version_info() {
    cd "$APP_DIR"
    echo ""
    echo "╔══════════════════════════════════════╗"
    echo "║   AI24x7 Factory - Update System    ║"
    echo "╠══════════════════════════════════════╣"
    echo "║ App Directory:  $APP_DIR"
    echo "║ Git Remote:     origin/main"
    echo "║ Current Rev:    $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
    echo "║ Latest Rev:     $(git rev-parse --short origin/main 2>/dev/null || echo 'N/A')"
    echo "║ Last Backup:    $(ls -dt "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'None')"
    echo "║ Updated:        $(git log --oneline -1 2>/dev/null || echo 'N/A')"
    echo "╚══════════════════════════════════════╝"
    echo ""
    
    # Service status
    echo "Service Status:"
    systemctl is-active ai24x7-factory 2>/dev/null && echo "  Factory Service:   ACTIVE" || echo "  Factory Service:   INACTIVE"
    pgrep -f factory_dashboard.py > /dev/null && echo "  Dashboard (:5052):  RUNNING" || echo "  Dashboard (:5052):  STOPPED"
    pgrep -f license_client > /dev/null && echo "  License Client:    RUNNING" || echo "  License Client:    STOPPED"
    echo ""
}

#==============================================================================
# MAIN
#==============================================================================
case "${1:-}" in
    --check)
        preflight
        check_updates
        ;;
    --force|--update)
        preflight
        backup_current
        do_update
        version_info
        ;;
    --rollback)
        rollback
        version_info
        ;;
    --version|-v)
        version_info
        ;;
    --self-update)
        self_update
        ;;
    *)
        echo ""
        echo "╔═══════════════════════════════════════════╗"
        echo "║   AI24x7 Factory - Auto Update System    ║"
        echo "╠═══════════════════════════════════════════╣"
        echo "║  Usage: auto_update.sh [OPTION]           ║"
        echo "║                                             ║"
        echo "║  --check      Check for updates only      ║"
        echo "║  --force      Update to latest version    ║"
        echo "║  --rollback   Rollback to previous version ║"
        echo "║  --version    Show version info           ║"
        echo "║  --self-update Update this script itself   ║"
        echo "╚═════════════════════════════════════════════╝"
        echo ""
        echo "For automatic updates, enable in crontab:"
        echo "  0 3 * * * /opt/ai24x7-factory/auto_update.sh --check >> /var/log/ai24x7_update.log 2>&1"
        echo ""
        version_info
        ;;
esac
