#!/bin/bash
set -e
echo "AI24x7 Factory Edition - Starting..."
cd /opt/ai24x7-factory/factory/dashboard
if [ ! -f factory_data.db ]; then
    python3 -c "from factory_db import init_db, seed_demo_data; init_db(); seed_demo_data()" 2>/dev/null || true
fi
echo "Database ready"
cd /opt/ai24x7-factory
echo "Starting all services..."
nohup python3 /opt/ai24x7-factory/factory/api/cctv_api.py >> /data/logs/cctv.log 2>&1 &
nohup python3 /opt/ai24x7-factory/factory/api/license_api.py >> /data/logs/license.log 2>&1 &
nohup python3 /opt/ai24x7-factory/factory/api/payment_api.py >> /data/logs/payment.log 2>&1 &
nohup python3 /opt/ai24x7-factory/factory/api/factory_camera_api.py >> /data/logs/camera.log 2>&1 &
cd /opt/ai24x7-factory/factory/dashboard
nohup python3 -m streamlit run factory_dashboard.py --server.port 5052 --server.headless true --server.address 0.0.0.0 >> /data/logs/dashboard.log 2>&1 &
echo "All services started on ports 5050,5052,5053,5054,5055"
tail -f /dev/null
