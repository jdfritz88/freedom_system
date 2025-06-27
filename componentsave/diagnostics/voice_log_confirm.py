# Manually reprint the last line of the most recent voice system log

import os

log_dir = "F:/Apps/freedom_system/log/startup"
voice_logs = [f for f in os.listdir(log_dir) if f.startswith("VoiceSystem") and f.endswith(".log")]

if not voice_logs:
    print("[ERROR] No VoiceSystem logs found.")
else:
    latest = max(voice_logs, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
    with open(os.path.join(log_dir, latest), "r", encoding="utf-8") as f:
        lines = f.readlines()
        print(f"[Voice Log] {lines[-1].strip() if lines else '(Empty)'}")
