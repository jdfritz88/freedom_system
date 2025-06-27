import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# readiness_sweep_audit.py
# Scans for essential Freedom System components and launchers and verifies readiness
# Optimized using recommendations from the UI optimization report

import os
import importlib.util
import multiprocessing
from componentsave.queue import Queue

# Define essential components to check
ESSENTIAL_PATHS = [
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_system_core.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_image_generator.py",
    "F:/Apps/freedom_system/componentsave/launchers/emotion_engine_boot_flag.py",
    "F:/Apps/freedom_system/componentsave/launchers/start_emotion_engine_flag_check.py",
    "F:/Apps/freedom_system/componentsave/launchers/face_training_launcher.py",
    "F:/Apps/freedom_system/componentsave/face_trainer/face_training_engine.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_image/image_emotion_driver.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_voice/voice_emotion_driver.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_music/music_emotion_driver.py",
]


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


def run_readiness_sweep():
    print("[🔍] Running Readiness Sweep on Essential Components...")
    results = []
    result_queue = multiprocessing.Queue()
    processes = []

    for path in ESSENTIAL_PATHS:
        p = multiprocessing.Process(target=audit_component, args=(path, result_queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    while not result_queue.empty():
        results.append(result_queue.get())

    print("\n[✅] Audit Results:")
    for path, exists, importable in results:
        status = "OK" if exists and importable else ("Missing" if not exists else "Import Fail")
        print(f" - {os.path.basename(path):35} -> {status}")


if __name__ == "__main__":
    run_readiness_sweep()
