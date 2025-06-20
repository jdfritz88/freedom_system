# git_autosaver.py
import os
import time
from datetime import datetime
from git import Repo

# === Settings ===
REPO_PATH = "F:/Apps/freedom_system"
CHECK_FOLDER = os.path.join(REPO_PATH, "autosaved_code")
SLEEP_SECONDS = 300  # Check every 5 minutes

def autosave_loop():
    repo = Repo(REPO_PATH)
    origin = repo.remote(name="origin")

    while True:
        print("[Autosave] Checking for changes...")
        repo.git.add(CHECK_FOLDER)
        if repo.is_dirty(untracked_files=True):
            message = f"Autosave at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            repo.index.commit(message)
            origin.push()
            print("[Autosave] Changes committed and pushed.")
        else:
            print("[Autosave] No changes detected.")

        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    autosave_loop()
