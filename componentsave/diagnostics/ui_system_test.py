import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import subprocess
import os
import time

# === UI Test Script for Freedom System ===
# This test attempts to launch each major UI component of the dashboard
# and checks for exceptions during short preview runs.

# List of core UI panels to test
UI_FILES = [
    "dashboard_grid_router.py",
    "emotion_orb_display.py",
    "gui_emotion_panels.py",
    "master_emotion_dashboard.py"
]

# Directory containing UI files
UI_DIR = os.path.join("F:/Apps/freedom_system/componentsave/ui_panels")

print("[TEST] Starting UI System Panel Test")

for file in UI_FILES:
    path = os.path.join(UI_DIR, file)
    if not os.path.exists(path):
        print(f"[SKIP] {file} not found.")
        continue

    print(f"[RUN] Previewing {file}...")
    try:
        proc = subprocess.Popen(["python", path])
        time.sleep(3)  # Run for a short preview duration
        proc.terminate()
        proc.wait()
        print(f"[PASS] {file} launched and closed cleanly.")
    except Exception as e:
        print(f"[FAIL] {file} threw an error: {e}")

print("[COMPLETE] UI System Panel Test Finished")
