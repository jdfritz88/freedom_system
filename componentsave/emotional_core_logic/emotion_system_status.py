# GUI import header (required for cross-module access in Freedom System)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Placeholder: simulate log entries for override updates
def log_override_update(setting, value):
    print(f"[OVERRIDE] {setting} set to {value:.2f}")
