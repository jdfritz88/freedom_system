# Replaces BAT call with direct Python execution for voice system

import subprocess
import os
from datetime import datetime

LOG_DIR = "F:/Apps/freedom_system/log/startup"
os.makedirs(LOG_DIR, exist_ok=True)

def launch_and_log(name, command):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(LOG_DIR, f"{name}_{timestamp}.log")
    with open(log_path, "w", encoding="utf-8") as f:
        process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, shell=True)
    print(f"[STARTED] {name} → logging to {log_path}")

def run_all():
    print("[MONITOR] Launching Freedom System components...")

    launch_and_log("EmotionEngine", "python componentsave/launchers/emotion_engine_boot_flag.py")
    launch_and_log("VoiceSystem", "python componentsave/output_bridges/systems_voice/voice_emotion_driver.py")
    launch_and_log("UILoader", "python startup_ui_loader_integration.py --optimize-ui --async-panels --fifo-queue --gpu-detect --delay-throttle")

if __name__ == "__main__":
    run_all()
