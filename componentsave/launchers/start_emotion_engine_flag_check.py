import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# ✅ Rewritten: start_emotion_engine_flag_check.py
# Location: F:/Apps/freedom_system/componentsave/launchers/
# Function: Checks for the emotion engine startup flag and exits with success/failure status

import os
import sys

FLAG_PATH = "F:/Apps/freedom_system/componentsave/flags/emotion_engine_flag.json"

if __name__ == '__main__':
    if os.path.isfile(FLAG_PATH):
        print(f"[FLAG] Emotion engine boot flag detected: {FLAG_PATH}")
        sys.exit(0)
    else:
        print("[FLAG] Emotion engine boot flag missing.")
        sys.exit(1)
