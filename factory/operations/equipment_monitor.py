#!/usr/bin/env python3
"""Equipment Status Monitoring"""
class EquipmentMonitor:
    def __init__(self):
        print("⚙️ Equipment monitor initialized")
    
    def check_status(self, equipment_id):
        return {"running": True, "temperature": 45, "status": "normal"}
