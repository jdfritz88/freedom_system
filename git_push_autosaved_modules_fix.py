import os
import shutil
import subprocess
from datetime import datetime

SOURCE_PATHS = [
    "emotion_trigger_conflict_resolver.py",
    "emotion_trigger_logger.py",
    "emotion_blending_engine.py",
    "trigger_source_filter.py",
    "emotion_intensity_override.py"
]

DEST_DIR = "F:/Apps/freedom_system/autosaved_code"

def copy_files():
    for file in SOURCE_PATHS:
        if os.path.exists(file):
            dest = os.path.join(DEST_DIR, file)
            shutil.copy(file, dest)
            print(f"✅ Copied {file} to {dest}")

def git_push():
    os.chdir("F:/Apps/freedom_system")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subprocess.run(["git", "add", "autosaved_code"], check=True)
    subprocess.run(["git", "add", "git_push_autosaved_modules.py"], check=True)  # Include this script too
    # Only commit if there are changes
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"Autosave at {timestamp}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Pushed autosaved_code to GitHub")
    else:
        print("⚠️  No changes to commit.")

if __name__ == "__main__":
    copy_files()
    git_push()
