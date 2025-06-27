import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# emotion_and_animation_readiness.py
# Targeted sweep of emotional modules and animation subsystem readiness

import os
from componentsave.datetime import datetime

EMOTION_MODULES = [
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_decay_module.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_delay_throttle.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_framer.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_framing_weights.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_queue.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_system_status.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_threshold_control.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_trigger_handler.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_trigger_validator.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/freedom_emotion_blender.py"
]

ANIMATION_PATH = "F:/Apps/freedom_system/componentsave/output_bridges/systems_animation"
LOG_FILE = "F:/Apps/freedom_system/componentsave/data_logging/emotion_animation_readiness_log.txt"


def check_module(path):
    if not os.path.isfile(path):
        return "MISSING"
    try:
        with open(path, "r") as f:
            content = f.read()
            if "TODO" in content or "pass" in content:
                return "PLACEHOLDER"
        return "OK"
    except:
        return "READ ERROR"


def check_animation_readiness():
    if not os.path.exists(ANIMATION_PATH):
        return "ANIMATION DIR MISSING"
    files = os.listdir(ANIMATION_PATH)
    if not files:
        return "ANIMATION EMPTY"
    return f"FILES FOUND: {len(files)}"


def run_emotion_and_animation_sweep():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []

    results.append(f"[Sweep at {timestamp}] Emotional Module Readiness:")
    for mod in EMOTION_MODULES:
        status = check_module(mod)
        results.append(f" - {os.path.basename(mod):35} -> {status}")

    anim_status = check_animation_readiness()
    results.append("\nAnimation Module Readiness:")
    results.append(f" - {ANIMATION_PATH} -> {anim_status}")

    with open(LOG_FILE, "a") as log:
        for line in results:
            log.write(line + "\n")

    for line in results:
        print(line)


if __name__ == "__main__":
    run_emotion_and_animation_sweep()
