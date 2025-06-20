import subprocess
import datetime
import os
import threading
from win10toast import ToastNotifier

log_path = "F:/Apps/freedom_system/autosave_log.txt"
toaster = ToastNotifier()

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def notify(title, text):
    try:
        threading.Thread(target=toaster.show_toast, args=(title, text), kwargs={"duration": 3}).start()
    except Exception as e:
        log(f"❌ Notify failed: {e}")

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

    notify("Autosave Complete", "Your files have been saved and pushed to GitHub.")

except subprocess.CalledProcessError as e:
    log(f"❌ Git command failed: {e}")
    notify("Autosave Error", str(e))
except Exception as e:
    log(f"❌ Unexpected error: {e}")
    notify("Autosave Error", str(e))
