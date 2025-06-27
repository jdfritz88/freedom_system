# Save as: F:\Apps\freedom_system\componentsave\data_logging\slider_log_scheduler.py

import os
import sys
import threading
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_logging.trim_slider_sync_log import LOG_PATH, MAX_LINES


def scheduled_trim_loop(interval_seconds=86400):
    while True:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, 'r') as f:
                lines = f.readlines()

            if len(lines) > MAX_LINES:
                with open(LOG_PATH, 'w') as f:
                    f.writelines(lines[-MAX_LINES:])
                print(f"[TRIM] Scheduled trim complete → last {MAX_LINES} lines kept.")
        time.sleep(interval_seconds)


def start_log_trim_scheduler():
    thread = threading.Thread(target=scheduled_trim_loop, daemon=True)
    thread.start()
    print("[TRIM] Auto log trimming scheduler launched.")
