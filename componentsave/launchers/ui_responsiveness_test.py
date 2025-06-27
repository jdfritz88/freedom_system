import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ui_responsiveness_test.py
# Simulates UI responsiveness and flags blocking behavior in critical panel modules

import time
import threading
import importlib.util
import sys

TARGET_MODULES = [
    "F:/Apps/freedom_system/componentsave/ui_panels/gui_emotion_panels.py",
    "F:/Apps/freedom_system/componentsave/ui_panels/background_toggle_control.py"
]

TEST_DURATION = 3  # seconds

# Try to import the module in a thread and see if it hangs

def timed_import(path, results):
    module_name = path.split("/")[-1]
    try:
        spec = importlib.util.spec_from_file_location("temp_ui_module", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        results.append((module_name, "OK"))
    except Exception as e:
        results.append((module_name, f"FAIL: {str(e)}"))

def run_ui_responsiveness_test():
    print("[🧪] Running UI Responsiveness Test...")
    results = []

    for path in TARGET_MODULES:
        result_holder = []
        thread = threading.Thread(target=timed_import, args=(path, result_holder))
        thread.start()
        thread.join(TEST_DURATION)

        if thread.is_alive():
            print(f" - {path.split('/')[-1]:35} -> TIMEOUT (Unresponsive)")
            thread.join(timeout=1)
        else:
            status = result_holder[0][1] if result_holder else "Unknown"
            print(f" - {path.split('/')[-1]:35} -> {status}")

if __name__ == "__main__":
    run_ui_responsiveness_test()
