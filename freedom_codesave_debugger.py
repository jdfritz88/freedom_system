import os
import subprocess
import time
from pathlib import Path
from datetime import datetime

REPO_PATH = Path("F:/Apps/freedom_system")
FILES = [
    "freedom_autopush_main.py",
    "freedom_autopush_launcher.py",
    "freedom_autopush_startup.py",
    "freedom_autopush_startup_override.py",
    "freedom_autopush_startup_old.py",
    "freedom_github_ready_check.py",
    "freedom_autopush_testcase.py",
    "freedom_github_commit_now.py"
]

LOG_DIR = Path("F:/")
LOG_FILE = LOG_DIR / "freedom_codesave_debug_log.txt"

log_lines = []

def log(msg):
    log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    log(f"CMD: {' '.join(cmd)}")
    log(f"OUT: {result.stdout.strip()}")
    log(f"ERR: {result.stderr.strip()}")
    log(f"RET: {result.returncode}")
    return result.returncode

if not REPO_PATH.exists():
    log(f"ERROR: Repo path does not exist: {REPO_PATH}")
else:
    os.chdir(REPO_PATH)
    log("Starting Git debug validation (10 rounds)...")

    for i in range(10):
        log(f"\n--- ROUND {i+1} ---")
        run_cmd(["git", "status"])
        for file in FILES:
            if Path(file).exists():
                run_cmd(["git", "add", file])
                run_cmd(["git", "commit", "-m", f"Debug round {i+1} {file}"])
        run_cmd(["git", "push"])
        time.sleep(1)

    log("\nPython Interpreter Validation")
    run_cmd(["where", "python"])
    run_cmd(["python", "--version"])
    run_cmd(["py", "--version"])

# Ensure log directory exists before writing
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        for line in log_lines:
            f.write(line + "\n")
    print(f"Debug results written to: {LOG_FILE}")
except Exception as e:
    print(f"Failed to write debug log: {e}")
