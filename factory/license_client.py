#!/usr/bin/env python3
"""License Client - Hardware binding + cloud validation"""
import os, hashlib, uuid, requests

LICENSE_SERVER = "http://43.242.224.231:5053"
LICENSE_FILE = ".license"

def get_hardware_id():
    """Generate unique hardware ID from MAC + CPU"""
    mac = uuid.getnode()
    cpu_id = os.popen("cat /proc/cpuinfo | grep 'model name' | head -1").read()[:100].strip()
    hw_string = f"{mac}-{cpu_id}-{uuid.gethostname()}"
    return hashlib.sha256(hw_string.encode()).hexdigest()

def check_license():
    """Validate license with server"""
    license_key = os.environ.get('LICENSE_KEY', '')
    if not license_key:
        print("⚠️ No license key found in LICENSE_KEY env var")
        return True  # Allow in demo mode
    
    hw_id = get_hardware_id()
    
    try:
        resp = requests.post(f"{LICENSE_SERVER}/validate",
            json={"key": license_key, "hw_id": hw_id, "product": "factory"},
            timeout=10)
        if resp.status_code == 200:
            print("✅ License valid")
            return True
        else:
            print(f"❌ License invalid: {resp.text}")
            return False
    except Exception as e:
        print(f"⚠️ License server unreachable: {e}")
        return True  # Grace period
