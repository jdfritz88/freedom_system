import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# readiness_sweep_with_ui.py
# ✅ Cleaned of music_emotion_driver
# ⚠️ FIXED: Missing function call for run_readiness_sweep()

# SAVE TO:
# F:/Apps/freedom_system/componentsave/launchers/readiness_sweep_with_ui.py
# THEN RUN:
# python F:/Apps/freedom_system/componentsave/launchers/readiness_sweep_with_ui.py

import os
import importlib.util
import multiprocessing
from componentsave.queue import Queue
from componentsave.datetime import datetime
import subprocess

ESSENTIAL_PATHS = [
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_system_core.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_image_generator.py",
    "F:/Apps/freedom_system/componentsave/launchers/emotion_engine_boot_flag.py",
    "F:/Apps/freedom_system/componentsave/launchers/start_emotion_engine_flag_check.py",
    "F:/Apps/freedom_system/componentsave/launchers/face_training_launcher.py",
    "F:/Apps/freedom_system/componentsave/face_trainer/face_training_engine.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_image/image_emotion_driver.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_voice/voice_emotion_driver.py"
]

OPTIONAL_PATHS = [
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_animation/animation_emotion_driver.py",
    "F:/Apps/freedom_system/componentsave/ui_panels/gui_emotion_panels.py",
    "F:/Apps/freedom_system/componentsave/ui_panels/background_toggle_control.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_system_status.py"
]

LOG_PATH = "F:/Apps/freedom_system/componentsave/data_logging/readiness_sweep_log.txt"
UI_TEST_PATH = "F:/Apps/freedom_system/componentsave/launchers/ui_responsiveness_test.py"


def check_file_exists(path):
    return os.path.isfile(path)

def check_importable(path):
    try:
        spec = importlib.util.spec_from_file_location("temp_module", path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return True
        return False
    except Exception:
        return False

def audit_component(path, result_queue):
    exists = check_file_exists(path)
    importable = check_importable(path) if exists else False
    result_queue.put((path, exists, importable))

def run_batch_audit(path_list, label):
    results = []
    result_queue = multiprocessing.Queue()
    processes = []

    for path in path_list:
        p = multiprocessing.Process(target=audit_component, args=(path, result_queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    while not result_queue.empty():
        results.append(result_queue.get())

    return label, results

def write_log(label, results):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as log:
        log.write(f"\n[Audit Run at {timestamp}] {label}\n")
        for path, exists, importable in results:
            status = "OK" if exists and importable else ("Missing" if not exists else "Import Fail")
            log.write(f" - {os.path.basename(path):35} -> {status}\n")

def run_ui_responsiveness_test():
    print("\n[🧪] UI Responsiveness Check...")
    if os.path.isfile(UI_TEST_PATH):
        subprocess.run(["python", UI_TEST_PATH], check=False)
    else:
        print(" - UI responsiveness test not found. Skipping.")

def run_readiness_sweep():
    print("[🔍] Running Readiness Sweep on Essential and Optional Components...")

    for label, paths in [("[Essential Components]", ESSENTIAL_PATHS), ("[Optional Components]", OPTIONAL_PATHS)]:
        section, results = run_batch_audit(paths, label)
        print(f"\n{section}")
        for path, exists, importable in results:
            status = "OK" if exists and importable else ("Missing" if not exists else "Import Fail")
            print(f" - {os.path.basename(path):35} -> {status}")
        write_log(section, results)

    run_ui_responsiveness_test()

# ✅ FIXED: Call the sweep function
if __name__ == "__main__":
    run_readiness_sweep()
