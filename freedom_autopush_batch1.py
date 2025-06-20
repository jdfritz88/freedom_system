import os
import subprocess
from datetime import datetime
import time

# Files to push
FILES = [
    "set_git_identity.py",
    "autosave_to_github.py",
    "git_autosaver.py",
    "git_autosaver.bat",
    "git_autosaver_toast.py",
    "FaceTrainingPrompt.py",
    "FaceTrainingPrompt_SafeFallback.py"
]

REPO_PATH = r"F:\Apps\freedom_system"
CHECK_INTERVAL_SECONDS = 3600  # Check every hour

while True:
    os.chdir(REPO_PATH)

    for file in FILES:
        if os.path.exists(file):
            subprocess.run(["git", "add", file])

    commit_msg = f"Auto-push batch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg])
    subprocess.run(["git", "push"])

    time.sleep(CHECK_INTERVAL_SECONDS)
