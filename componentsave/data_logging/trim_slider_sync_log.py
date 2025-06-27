# Save as: F:\Apps\freedom_system\componentsave\data_logging\trim_slider_sync_log.py

import os

LOG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'log', 'ui_panels', 'slider_sync_log.txt')
MAX_LINES = 100

if os.path.exists(LOG_PATH):
    with open(LOG_PATH, 'r') as f:
        lines = f.readlines()

    if len(lines) > MAX_LINES:
        with open(LOG_PATH, 'w') as f:
            f.writelines(lines[-MAX_LINES:])
        print(f"[TRIM] Log trimmed to last {MAX_LINES} entries.")
    else:
        print("[TRIM] No trimming needed.")
else:
    print("[TRIM] No log file found.")
