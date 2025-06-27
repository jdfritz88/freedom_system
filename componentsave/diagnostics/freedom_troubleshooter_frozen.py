import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# FROZEN VERSION - DO NOT MODIFY UNLESS SYSTEM STATE CHANGES
# freedom_troubleshooter_frozen.py
# Snapshot of successful system diagnostic for Freedom System

"""
WHAT THIS FILE DOES:
- It checks if all key Freedom System components exist and can be imported
- It confirms the Emotion Engine, Voice System, Image Engine, Face Trainer, and Log Folder are present and functioning
- It does NOT make changes, only reports status
- It represents a frozen clean state—if you ever run into issues later, run this file to confirm if the core system is still okay

WHEN TO USE:
- After changes or crashes, run this to see if the main systems are still intact
- If everything passes, you know the problem is outside the core structure
- If something fails, you’ll know what to patch or restore

DO NOT EDIT unless the system structure has changed
"""

import os
import importlib.util
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
COMPONENT_PATHS = {
    "Emotion Engine": "componentsave/emotional_core_logic/emotion_system_core.py",
    "Voice Bridge": "componentsave/output_bridges/systems_voice/voice_emotion_bridge.py",
    "Image Engine": "componentsave/output_bridges/systems_image/image_emotion_driver.py",
    "Face Trainer": "componentsave/face_trainer/face_training_engine.py",
    "Log Folder": "log"
}


def check_file_exists(label, relative_path):
    abs_path = os.path.join(ROOT, relative_path)
    if os.path.isdir(abs_path):
        print(f"[✓] {label} folder exists: {relative_path}")
        return True
    elif os.path.isfile(abs_path):
        print(f"[✓] {label} found: {relative_path}")
        return True
    else:
        print(f"[X] {label} MISSING: {relative_path}")
        return False


def try_import_module(label, relative_path):
    abs_path = os.path.join(ROOT, relative_path)
    if not os.path.isfile(abs_path):
        print(f"[X] {label} NOT FOUND for import: {relative_path}")
        return False
    try:
        spec = importlib.util.spec_from_file_location("temp_module", abs_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"[✓] {label} import check passed")
        return True
    except Exception as e:
        print(f"[!] {label} import FAILED:")
        print(traceback.format_exc())
        return False


def run_diagnostics():
    print("\n=== Freedom System Troubleshooter (FROZEN SNAPSHOT) ===\n")
    for label, path in COMPONENT_PATHS.items():
        exists = check_file_exists(label, path)
        if exists and path.endswith(".py"):
            try_import_module(label, path)

    print("\nDiagnostics complete.")
    print("This frozen version reflects a passing state. Do not alter unless system layout changes.")


if __name__ == "__main__":
    run_diagnostics()
