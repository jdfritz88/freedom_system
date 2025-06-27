import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import subprocess
import os

BASE = r"F:\Apps\freedom_system\componentsave"

def run_test(label, path):
    print(f"\n[RUNNING] {label}")
    result = subprocess.run(["python", os.path.join(BASE, path)], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"[ERROR] {result.stderr}")

print("[START] Freedom System Subsystem Diagnostic Sweep")

# Emotion Core Test (Runtime emotion test)
run_test("Emotion Core Runtime Test", "emotional_core_logic\\runtime_emotion_test.py")

# Voice Delay & Lock Test
run_test("Voice Emotion Delay Lock Test", "output_bridges\\systems_voice\\test_voice_delay_lock.py")

# Image Generation Test
run_test("Image Driver Emotion Test", "output_bridges\\systems_image\\test_image_emotion_driver.py")

# UI System Test
run_test("UI System Panel Test", "diagnostics\\ui_system_test.py")

# Log Retention Policy
run_test("Log Retention Policy Execution", "data_logging\\log_retention_policy.py")

print("\n[COMPLETE] Subsystem Diagnostics Finished")
