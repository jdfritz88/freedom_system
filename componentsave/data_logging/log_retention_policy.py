import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import os
import time

# Configuration
LOG_DIR = r"F:\Apps\freedom_system\log"
DAYS_TO_KEEP = 3
NOW = time.time()

print("[LOG CLEANUP] Starting 3-day retention policy")

for system in os.listdir(LOG_DIR):
    system_path = os.path.join(LOG_DIR, system)
    if os.path.isdir(system_path):
        for file in os.listdir(system_path):
            file_path = os.path.join(system_path, file)
            if os.path.isfile(file_path):
                file_age_days = (NOW - os.path.getmtime(file_path)) / 86400
                if file_age_days > DAYS_TO_KEEP:
                    try:
                        os.remove(file_path)
                        print(f"[DELETED] {file} from {system}")
                    except Exception as e:
                        print(f"[ERROR] Failed to delete {file}: {e}")

print("[COMPLETE] Log cleanup finished.")
