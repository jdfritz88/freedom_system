# Save as: F:\Apps\freedom_system\componentsave\diagnostics\slider_sync_log_viewer.py

import os

log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'log', 'ui_panels', 'slider_sync_log.txt')

print("[VIEW] Slider Sync Log:")
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        for line in f.readlines()[-10:]:  # Show last 10 entries
            print(line.strip())
else:
    print("[INFO] No log found yet.")
