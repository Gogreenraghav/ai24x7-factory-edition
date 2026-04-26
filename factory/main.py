#!/usr/bin/env python3
"""
AI24x7 Factory Edition - Main Entry Point
"""
import os, sys, json, time, subprocess
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from factory.license_client import check_license, get_hardware_id
from factory.config import load_config
from safety.fire_detector import FireDetector
from safety.ppe_detector import PPEDetector
from safety.fall_detector import FallDetector
from operations.anpr_camera import ANPRCamera
from operations.equipment_monitor import EquipmentMonitor
from operations.shift_manager import ShiftManager
from alerts.sms_alerts import SMSAlerts
from alerts.telegram_alerts import TelegramAlerts
from alerts.tts_announcer import TTSAnnouncer
from reporting.shift_report import ShiftReportGenerator

class FactorySystem:
    def __init__(self):
        print("🏭 AI24x7 Factory Edition v1.0")
        print("=" * 40)
        
        # License check
        if not check_license():
            print("❌ LICENSE INVALID - System cannot start")
            print("   Contact: ai24x7.cloud/license")
            sys.exit(1)
        
        # Load config
        self.config = load_config()
        self.hw_id = get_hardware_id()
        print(f"✅ Hardware ID: {self.hw_id[:16]}...")
        
        # Initialize modules
        self.fire = FireDetector()
        self.ppe = PPEDetector()
        self.fall = FallDetector()
        self.anpr = ANPRCamera(self.config.get('cameras', []))
        self.equip = EquipmentMonitor()
        self.shift = ShiftManager(self.config.get('shifts', {}))
        
        self.sms = SMSAlerts()
        self.telegram = TelegramAlerts()
        self.tts = TTSAnnouncer()
        self.report = ShiftReportGenerator()
        
        print("✅ All modules initialized")
        print()
    
    def run(self):
        print("🚀 Factory monitoring started")
        print("Press Ctrl+C to stop")
        print()
        
        last_shift_check = time.time()
        
        try:
            while True:
                cameras = self.config.get('cameras', [])
                
                for cam in cameras:
                    cam_id = cam.get('id')
                    rtsp = cam.get('rtsp')
                    
                    # Fire detection
                    fire_result = self.fire.detect(rtsp)
                    if fire_result.get('fire'):
                        self.tts.announce("Fire detected in camera " + str(cam_id))
                        self.sms.send_alert(f"FIRE in Camera {cam_id}!", cam_id)
                        self.telegram.send(f"🔥 FIRE DETECTED - Camera {cam_id}")
                    
                    # PPE check
                    ppe_result = self.ppe.check(rtsp, cam.get('ppe_rules', {}))
                    if ppe_result.get('violations'):
                        for v in ppe_result['violations']:
                            self.telegram.send(f"⚠️ PPE Violation - Camera {cam_id}: {v}")
                    
                    # Fall detection
                    fall_result = self.fall.detect(rtsp)
                    if fall_result.get('fallen'):
                        self.tts.announce("Fall detected in camera " + str(cam_id))
                        self.sms.send_alert(f"FALL in Camera {cam_id}", cam_id)
                        self.telegram.send(f"🏃 FALL DETECTED - Camera {cam_id}")
                    
                    # ANPR
                    anpr_result = self.anpr.process(rtsp)
                    if anpr_result.get('plates'):
                        for plate in anpr_result['plates']:
                            print(f"🚗 Plate: {plate}")
                
                # Shift check every 60 seconds
                if time.time() - last_shift_check > 60:
                    current_shift = self.shift.get_current_shift()
                    if self.shift.is_shift_changed(current_shift):
                        print(f"🔄 Shift changed to: {current_shift}")
                        self.report.generate_shift_report(current_shift)
                    last_shift_check = time.time()
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n🛑 Factory monitoring stopped")

if __name__ == "__main__":
    system = FactorySystem()
    system.run()
