# This checks if run_voice.py is standalone or redundant

import os

voice_dir = "F:/Apps/freedom_system/componentsave/output_bridges/systems_voice"
py_file = os.path.join(voice_dir, "run_voice.py")

if os.path.exists(py_file):
    with open(py_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "voice_emotion_driver.py" in content or "main" in content:
            print("[INFO] run_voice.py appears to be a launcher or wrapper script.")
        else:
            print("[INFO] run_voice.py exists but does not appear to wrap driver.")
else:
    print("[INFO] run_voice.py does not exist.")
