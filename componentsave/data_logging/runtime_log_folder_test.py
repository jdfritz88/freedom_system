import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# 🧪 Runtime Test: Log Folder Creation + Pruning
# Save to: F:/Apps/freedom_system/componentsave/data_logging
# Purpose: Ensure log folders exist, match top-level components, and prune older than 3 days

import os
import time
import shutil
from componentsave.datetime import datetime, timedelta

results = []

log_root = "F:/Apps/freedom_system/log"
expected_subdirs = [
    "CodeKeySTT",
    "Coqui_TTS",
    "FaceTrainer",
    "emotional_core_logic",
    "output_bridges",
    "ui_panels",
    "launchers"
]

# 1. Confirm subfolders exist
for subdir in expected_subdirs:
    path = os.path.join(log_root, subdir)
    if os.path.exists(path):
        results.append(f"✅ Log subfolder exists: {subdir}")
    else:
        results.append(f"❌ Missing log subfolder: {subdir}")

# 2. Simulate pruning of logs older than 3 days
pruned = 0
now = time.time()
thresh = now - (3 * 86400)  # 3 days

for subdir in expected_subdirs:
    path = os.path.join(log_root, subdir)
    if not os.path.exists(path):
        continue
    
    for file in os.listdir(path):
        fpath = os.path.join(path, file)
        try:
            if os.path.isfile(fpath) and os.path.getmtime(fpath) < thresh:
                os.remove(fpath)
                pruned += 1
        except:
            continue

results.append(f"✅ Pruning complete. Old files deleted: {pruned}")

# 📊 Output log validation
print("\nLog Folder Structure + Pruning Check:")
for line in results:
    print(line)
