#!/usr/bin/env python3
"""
AI24x7 License Client v3.0
Handles: registration, periodic payment check, anti-tamper, grace period
"""
import os, sys, time, hashlib, uuid, requests, json
from pathlib import Path

LICENSE_SERVER = os.environ.get("LICENSE_SERVER", "http://43.242.224.231:5053")
LICENSE_FILE = Path.home() / ".ai24x7_license"
LICENSE_KEY_ENV = os.environ.get("LICENSE_KEY", "")
CHECK_INTERVAL = 3600  # Check every 1 hour when online
GRACE_FILE = Path.home() / ".ai24x7_grace"

class LicenseError(Exception):
    pass

class HardLockError(LicenseError):
    """5 wrong attempts — permanently locked"""
    pass

class SuspendedError(LicenseError):
    """Payment due — suspended"""
    pass

def get_hardware_id() -> str:
    """Generate unique hardware ID from MAC + CPU + hostname"""
    mac = ':'.join(f'{uuid.getnode():02x}'[i:i+2] for i in range(0,12,2))
    cpu = os.popen("cat /proc/cpuinfo | grep 'model name' | head -1").read()[:80].strip()
    hostname = uuid.gethostname()
    hw_string = f"{mac}-{cpu}-{hostname}".encode().decode('utf-8', errors='ignore')
    return hashlib.sha256(hw_string.encode()).hexdigest()[:32]

def read_license_file() -> dict:
    if not LICENSE_FILE.exists():
        return {}
    try:
        return json.loads(LICENSE_FILE.read_text())
    except:
        return {}

def write_license_file(data: dict):
    LICENSE_FILE.write_text(json.dumps(data, indent=2))

def is_online() -> bool:
    try:
        r = requests.get(f"{LICENSE_SERVER}/health", timeout=3)
        return r.status_code == 200
    except:
        return False

def register(license_key: str) -> dict:
    """Register this machine with the license server"""
    hw_id = get_hardware_id()
    resp = requests.post(f"{LICENSE_SERVER}/register",
        json={"license_key": license_key, "machine_id": hw_id, "client_name": os.environ.get("FACTORY_NAME","Factory")},
        timeout=10)
    data = resp.json()
    write_license_file({"key": license_key, "machine_id": hw_id, "status": "active"})
    return data

def validate_key(license_key: str) -> dict:
    """Validate key — also used for login attempts (anti-tamper)"""
    hw_id = get_hardware_id()
    resp = requests.post(f"{LICENSE_SERVER}/validate-key",
        json={"license_key": license_key, "machine_id": hw_id},
        timeout=10)
    return resp.json()

def check_payment() -> dict:
    """Periodic online check — returns status"""
    hw_id = get_hardware_id()
    key = LICENSE_KEY_ENV or read_license_file().get("key", "")
    if not key:
        return {"valid": False, "action": "NO_KEY"}
    try:
        resp = requests.post(f"{LICENSE_SERVER}/validate-payment",
            json={"license_key": key, "machine_id": hw_id},
            timeout=10)
        return resp.json()
    except requests.RequestException as e:
        # Offline — check local grace period
        return {"valid": False, "action": "OFFLINE", "message": str(e)}

def is_suspended_locally() -> bool:
    """Check if we've been locally suspended"""
    data = read_license_file()
    return data.get("status") == "suspended"

def handle_action(action: str, data: dict):
    """Handle server response actions"""
    if action == "SUSPEND" or action == "HARD_LOCK":
        write_license_file({**read_license_file(), "status": "suspended"})
        # Kill all AI24x7 services
        os.system("systemctl stop smart-layer-api 2>/dev/null")
        os.system("systemctl stop smart-layer-processor 2>/dev/null")
        os.system("pkill -f 'factory_dashboard' 2>/dev/null")
        os.system("pkill -f 'smart_layer' 2>/dev/null")
        
        if action == "HARD_LOCK":
            raise HardLockError(f"Machine locked: {data.get('message', 'Contact AI24x7')}")
        else:
            raise SuspendedError(f"License suspended: {data.get('message', 'Payment due')}")
    
    elif action == "GRACE_PERIOD":
        grace_hrs = data.get('grace_hours_remaining', 0)
        # Save grace end time
        import time
        grace_end = time.time() + (grace_hrs * 3600)
        write_license_file({**read_license_file(), "grace_end": grace_end, "grace_active": True})
        return grace_hrs
    
    elif action == "OK" or action == "UNLOCK":
        write_license_file({**read_license_file(), "status": "active", "grace_end": None})
        return True
    
    return None

def is_in_grace() -> bool:
    """Check if in grace period (offline after payment due)"""
    data = read_license_file()
    if not data.get("grace_active"):
        return False
    grace_end = data.get("grace_end", 0)
    import time
    if time.time() > grace_end:
        return False
    return True

def full_check() -> bool:
    """
    Main license check — call this on startup and periodically.
    Returns True if license is valid and active.
    Raises HardLockError or SuspendedError if locked/suspended.
    """
    # 1. Check local hard lock first
    data = read_license_file()
    if data.get("status") == "suspended":
        # Try online check — server might have more info
        if is_online():
            key = LICENSE_KEY_ENV or data.get("key", "")
            if key:
                resp = validate_key(key)
                action = resp.get("action", "")
                if action == "HARD_LOCK":
                    raise HardLockError(resp.get("message", "Contact AI24x7"))
                elif action != "OK":
                    raise SuspendedError(resp.get("message", "Payment due"))
        raise SuspendedError("License suspended locally")
    
    # 2. Online check
    if is_online():
        result = check_payment()
        action = result.get("action", "OK")
        
        if action in ("SUSPEND", "HARD_LOCK"):
            handle_action(action, result)
        
        elif action == "GRACE_PERIOD":
            handle_action("GRACE_PERIOD", result)
            return True  # Still valid during grace
        
        elif action == "OK":
            handle_action("OK", result)
            return True
        
        elif action == "NOT_REGISTERED":
            # First time — try to register
            key = LICENSE_KEY_ENV or data.get("key", "")
            if key:
                try:
                    reg = register(key)
                    if reg.get("success"):
                        write_license_file({**data, "key": key, "status": "active"})
                        return True
                except Exception as e:
                    print(f"Registration failed: {e}")
            return False
        
        return result.get("valid", False)
    else:
        # Offline — check grace period
        if is_in_grace():
            return True
        # Pure offline with no grace — allow for grace hours
        print("⚠️ Offline and grace expired. License may be suspended when online.")
        return True  # Allow during grace

def init_license():
    """Initialize license on startup"""
    hw_id = get_hardware_id()
    key = LICENSE_KEY_ENV
    
    if not key:
        print("⚠️ No LICENSE_KEY found — DEMO MODE (no enforcement)")
        print("   Set LICENSE_KEY env var or place key in ~/.ai24x7_license")
        return True  # Demo mode
    
    try:
        valid = full_check()
        if valid:
            print(f"✅ AI24x7 License: VALID")
            return True
    except HardLockError as e:
        print(f"🚫 HARD LOCK: {e}")
        print("   Contact AI24x7 Support to unlock")
        sys.exit(1)
    except SuspendedError as e:
        print(f"⚠️ SUSPENDED: {e}")
        print("   Pay outstanding amount to restore service")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ License check failed: {e} — allowing (grace period)")
        return True  # Allow on error to avoid blocking

if __name__ == "__main__":
    ok = init_license()
    sys.exit(0 if ok else 1)