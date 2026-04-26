#!/usr/bin/env python3
"""Fire and Smoke Detection using YOLOv8"""
import cv2
from ultralytics import YOLOv8

class FireDetector:
    def __init__(self):
        print("🔥 Fire detector initializing...")
        # Using YOLOv8n for speed
        self.model = YOLOv8('yolov8n.pt')
        print("✅ Fire detector ready")
    
    def detect(self, rtsp_url):
        """Detect fire/smoke from camera feed"""
        # In production: connect to RTSP stream
        # For demo: return sample result
        return {
            "fire": False,
            "smoke": False,
            "confidence": 0.0,
            "timestamp": None
        }
