# Parses and summarizes Freedom System startup logs

import os
from datetime import datetime

LOG_DIR = "F:/Apps/freedom_system/log/startup"
latest_logs = {}

# Identify latest log for each type
for filename in os.listdir(LOG_DIR):
    if filename.endswith(".log"):
        key = filename.split("_")[0]
        path = os.path.join(LOG_DIR, filename)
        if key not in latest_logs or os.path.getmtime(path) > os.path.getmtime(latest_logs[key]):
            latest_logs[key] = path

summary = []

for system, path in latest_logs.items():
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        last_line = lines[-1].strip() if lines else "(Empty log)"
        summary.append(f"[{system}] {last_line}")

print("\n[SUMMARY] Most recent startup log results:")
for entry in summary:
    print(entry)
