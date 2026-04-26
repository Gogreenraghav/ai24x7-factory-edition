#!/usr/bin/env python3
"""Shift Management System"""
from datetime import datetime

class ShiftManager:
    def __init__(self, shifts):
        self.shifts = shifts
        self.current_shift = None
    
    def get_current_shift(self):
        now = datetime.now().strftime("%H:%M")
        for name, times in self.shifts.items():
            if times['start'] <= now < times['end']:
                return name
        return "unknown"
    
    def is_shift_changed(self, new_shift):
        if new_shift != self.current_shift:
            self.current_shift = new_shift
            return True
        return False
