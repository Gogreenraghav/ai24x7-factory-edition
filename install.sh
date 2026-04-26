#!/bin/bash
# AI24x7 Factory Edition - Quick Install
# Usage: bash install.sh

set -e

echo "🏭 AI24x7 Factory Edition Installer"
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install Python 3.10+ first."
    exit 1
fi

# Check CUDA
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU found"
    nvidia-smi --query-gpu=name,memory.total --format=csv 2>/dev/null | head -2
else
    echo "⚠️ No NVIDIA GPU - will use CPU mode (slower)"
fi

# Create virtual environment
echo "📦 Creating Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics>=8.0.0
pip install opencv-python>=4.8.0
pip install fastapi uvicorn streamlit
pip install python-telegram-bot>=20.0
pip install gtts edge-tts
pip install python-dotenv requests

# Create directories
echo "📁 Creating directories..."
mkdir -p logs data models camera_feeds

# License check
echo ""
echo "🔐 LICENSE REQUIRED"
echo "Get your license key from: https://ai24x7.cloud/license"
read -p "Enter license key (FACTORY-XXXX-XXXX-XXXX-XXXX): " LICENSE_KEY
echo "LICENSE_KEY=$LICENSE_KEY" > .env

# Config
cat > config.json << 'CONFIGEOF'
{
    "factory_name": "My Factory",
    "cameras": [],
    "alert_contacts": {
        "sms": [],
        "whatsapp": [],
        "telegram": []
    },
    "shifts": {
        "morning": {"start": "06:00", "end": "14:00"},
        "afternoon": {"start": "14:00", "end": "22:00"},
        "night": {"start": "22:00", "end": "06:00"}
    },
    "ppe_rules": {
        "helmet": true,
        "vest": true,
        "gloves": false,
        "shoes": true
    }
}
CONFIGEOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your camera RTSP URLs"
echo "2. Add alert contacts in config.json"
echo "3. Run: python3 main.py"
echo "4. Dashboard: http://localhost:5052"
echo ""
echo "📖 Full docs: https://docs.google.com/document/d/1Bls5HqGfUoY97JByLvEagDaYKgHeiM180ALqiVocCJ0/edit"
