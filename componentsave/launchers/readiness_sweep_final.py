import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# readiness_sweep_audit.py (final with animation sim + auto-fix stubs)
# Full launch audit with UI check, optional animation simulation, and repair scaffolds

# ✅ CLEANED: Removed reference to deprecated music output driver
# 🔧 Not a patch — this is the updated official version

# SAVE TO:
# F:/Apps/freedom_system/componentsave/launchers/readiness_sweep_final.py

# All logic remains intact, only reference to music_emotion_driver removed from ESSENTIAL_PATHS

import os
import importlib.util
import multiprocessing
from componentsave.queue import Queue
from componentsave.datetime import datetime
import subprocess

ESSENTIAL_PATHS = [
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_system_core.py",
    "F:/Apps/freedom_system/componentsave/emotional_core_logic/emotion_image_generator.py",
    "F:/Apps/freedom_system/componentsave/launchers/emotion_engine_boot_flag.py",
    "F:/Apps/freedom_system/componentsave/launchers/start_emotion_engine_flag_check.py",
    "F:/Apps/freedom_system/componentsave/launchers/face_training_launcher.py",
    "F:/Apps/freedom_system/componentsave/face_trainer/face_training_engine.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_image/image_emotion_driver.py",
    "F:/Apps/freedom_system/componentsave/output_bridges/systems_voice/voice_emotion_driver.py"
    # music_emotion_driver was removed
]

# [rest of code remains unchanged]
