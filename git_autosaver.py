import subprocess
import datetime
import os

log_path = "F:/Apps/freedom_system/autosave_log.txt"

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

try:
    os.chdir("F:/Apps/freedom_system")
    log("Starting autosave process.")

    subprocess.run(["git", "add", "-A"], check=True)
    log("Staged all changes.")

    commit_message = f"[Autosave] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    log(f"Committed with message: {commit_message}")

    subprocess.run(["git", "push"], check=True)
    log("Pushed to GitHub.")

except subprocess.CalledProcessError as e:
    log(f"❌ Git command failed: {e}")
except Exception as e:
    log(f"❌ Unexpected error: {e}")
