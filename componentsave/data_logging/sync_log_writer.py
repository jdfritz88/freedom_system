# Save as: F:\Apps\freedom_system\componentsave\data_logging\sync_log_writer.py

import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'log', 'ui_panels')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, 'slider_sync_log.txt')

def log_slider_sync(delay, decay, threshold, blend, lock):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] Delay={delay:.2f}, Decay={decay:.2f}, Threshold={threshold:.2f}, Blend={blend:.2f}, Lock={lock:.2f}\n"
    with open(LOG_PATH, 'a') as f:
        f.write(line)
