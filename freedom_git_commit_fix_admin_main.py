import os
import sys
import subprocess
import ctypes
import time
from datetime import datetime
from pathlib import Path

PRIMARY = Path("F:/Apps/freedom_system")
FALLBACK = Path("C:/Users/jespe/freedom_system")
REPO_PATH = PRIMARY if PRIMARY.exists() else FALLBACK
FILES = [
    "freedom_autopush_main.py",
    "freedom_autopush_launcher.py",
    "freedom_autopush_startup.py",
    "freedom_autopush_startup_override.py",
    "freedom_autopush_startup_old.py",
    "freedom_github_ready_check.py",
    "freedom_autopush_testcase.py",
    "freedom_github_commit_now.py",
    "freedom_autopush_batch1.py",
    "freedom_codesave_debugger.py",
    "freedom_git_commit_fix_admin_main.py",
    "freedom_git_commit_fix_admin_runner.py"
]

# Ensure repo directory exists
if not REPO_PATH.exists():
    print(f"⚠️ Repo path not found. Creating: {REPO_PATH}")
    REPO_PATH.mkdir(parents=True, exist_ok=True)

print(f"🔁 Using repo path: {REPO_PATH}")
os.chdir(REPO_PATH)

# Admin elevation fallback
try:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    if not is_admin:
        print("🔐 Attempting elevation...")
        params = f'\"{__file__}\"'
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()
except Exception as e:
    print(f"⚠️ Admin check/elevation failed: {e}\n⏬ Continuing in restricted mode")

# Try Git, fallback if needed
use_simulation = False
try:
    subprocess.run(["git", "--version"], capture_output=True, check=True)
    subprocess.run(["git", "status"], capture_output=True, timeout=5)
except Exception:
    use_simulation = True

if use_simulation:
    print("⚙️ Sandbox or restricted mode — running in simulation")
    for file in FILES:
        path = REPO_PATH / file
        if path.exists():
            print(f"[SIM] git add --force {file}")
            print(f"[SIM] git commit -m 'Final save {file} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'")
    print("[SIM] git push")
else:
    for file in FILES:
        path = REPO_PATH / file
        if path.exists():
            subprocess.run(["git", "add", "--force", file], shell=True)
            subprocess.run([
                "git", "commit", "-m",
                f"Final save {file} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ], shell=True)
    push_result = subprocess.run(["git", "push"], shell=True, capture_output=True, text=True)
    if push_result.returncode == 0:
        print("✅ Git push successful.")
    else:
        print("❌ Git push failed:")
        print(push_result.stdout)
        print(push_result.stderr)

print("\n✅ Done. This window will close automatically in 15 seconds...")
time.sleep(15)
