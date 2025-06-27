# Save as: F:\Apps\freedom_system\componentsave\diagnostics\test_trim_slider_log.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_logging import trim_slider_sync_log

if __name__ == '__main__':
    print("[TEST] Running slider log trim diagnostic...")
    trim_slider_sync_log
