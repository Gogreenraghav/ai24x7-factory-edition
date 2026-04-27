#!/usr/bin/env python3
"""AI24x7 Factory Edition — Health Check"""
import sys
import socket
import urllib.request
import sqlite3
from pathlib import Path

def check_port(port, name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        status = "✅" if result == 0 else "❌"
        print(f"{status} {name} (port {port})")
        return result == 0
    except Exception as e:
        print(f"❌ {name} (port {port}): {e}")
        return False

def check_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM cameras")
        count = c.fetchone()[0]
        conn.close()
        print(f"✅ Database: {count} cameras")
        return True
    except Exception as e:
        print(f"❌ Database: {e}")
        return False

def main():
    print("=" * 40)
    print(" AI24x7 Factory — Health Check")
    print("=" * 40)

    results = []

    # Check ports
    results.append(check_port(5052, "Dashboard"))
    results.append(check_port(5050, "CCTV API"))
    results.append(check_port(5053, "License Server"))
    results.append(check_port(5054, "Camera API"))
    results.append(check_port(5055, "Payment Server"))
    results.append(check_port(8080, "AI Server"))

    # Check database
    db_path = "/opt/ai24x7-factory/factory/dashboard/factory_data.db"
    if Path(db_path).exists():
        results.append(check_db(db_path))
    else:
        print(f"⚠️  Database not found at {db_path}")
        # Try alternate path
        if Path("/data/db/factory_data.db").exists():
            results.append(check_db("/data/db/factory_data.db"))

    print("=" * 40)
    passed = sum(results)
    total = len(results)
    print(f" Result: {passed}/{total} checks passed")

    if passed == total:
        print(" Status: ✅ ALL SYSTEMS OPERATIONAL")
        sys.exit(0)
    elif passed >= total - 1:
        print(" Status: ⚠️  DEGRADED (some services down)")
        sys.exit(0)
    else:
        print(" Status: ❌ CRITICAL FAILURE")
        sys.exit(1)

if __name__ == "__main__":
    main()
