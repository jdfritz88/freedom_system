"""AllTalk app-folder watcher (REPO_alltalk).

Started automatically when AllTalk's server starts (by _boot/freedom_alltalk.py), however
AllTalk was launched. Every 60 minutes it checks AllTalk's own folder
(app_cabinet/alltalk_tts) and alerts the user - it never changes, moves or deletes anything,
so there is a chance to see why something happened:

  * NEW FILE      - a file that was not in the folder before (user-, Claude- or app-made;
                    logs and screenshots included). Everything the user makes belongs in
                    REPO_alltalk, not in AllTalk's folder.
  * MODIFIED      - one of the folder's existing files (the developer's files) changed within
                    the last 60 minutes.
  * DELETED       - one of the folder's existing files disappeared.
  * RVC TRAINING  - an RVC voice-training process is running; its files are listed.

Not alerted: Python cache (__pycache__, *.pyc), AllTalk's Python environment
(alltalk_environment), .git, *.tmp, system/config/at_github_sha.json.

Developer updates are not alerted:
  * the REPO_alltalk update check marks its update window in logs/watcher_update_window.json;
  * and a changed file that exactly matches the developer's code after a recent `git pull`
    (git reflog) is recognised as a developer update.

Alerts: a message box that stays on screen until closed, plus logs/alltalk_watcher.log.
The list of known files is kept in logs/alltalk_watcher_known_files.json so files added while
AllTalk was off are still caught.
"""
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta

APP = os.path.abspath(sys.argv[1])
REPO = os.path.abspath(sys.argv[2])
SERVER_PID = int(sys.argv[3]) if len(sys.argv) > 3 else None

CHECK_EVERY = 60 * 60          # seconds between folder checks
MODIFIED_WINDOW = 60 * 60      # "modified within the last 60 minutes"
LIFE_POLL = 30                 # seconds between "is AllTalk still running" checks
RESTART_GRACE = 5 * 60         # AllTalk restarting: keep watching this long for a new server

LOGS = os.path.join(REPO, "logs")
LOG_FILE = os.path.join(LOGS, "alltalk_watcher.log")
KNOWN_FILE = os.path.join(LOGS, "alltalk_watcher_known_files.json")
LOCK_FILE = os.path.join(LOGS, "alltalk_watcher.pid")
UPDATE_WINDOW_FILE = os.path.join(LOGS, "watcher_update_window.json")

SKIP_DIRS = {"__pycache__", "alltalk_environment", ".git"}
SKIP_SUFFIXES = (".pyc", ".tmp")
SKIP_FILES = {os.path.normcase(os.path.join("system", "config", "at_github_sha.json"))}


def log(msg):
    os.makedirs(LOGS, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")


def alert(title, text):
    """Message box that stays until the user closes it; the watcher keeps running."""
    log(f"ALERT {title}: {text}")
    flags = 0x30 | 0x10000 | 0x40000   # warning icon | set foreground | topmost
    threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, text, title, flags),
                     daemon=False).start()


def scan():
    """{relative path: mtime} of every watched file in AllTalk's folder."""
    files = {}
    for root, dirs, names in os.walk(APP):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if n.endswith(SKIP_SUFFIXES):
                continue
            full = os.path.join(root, n)
            rel = os.path.relpath(full, APP)
            if os.path.normcase(rel) in SKIP_FILES:
                continue
            try:
                files[rel] = os.stat(full).st_mtime
            except OSError:
                pass
    return files


def git(*args):
    r = subprocess.run(["git", "-C", APP, *args], capture_output=True, text=True,
                       creationflags=0x08000000)  # no console window
    return r.stdout if r.returncode == 0 else ""


def update_window():
    try:
        with open(UPDATE_WINDOW_FILE, encoding="utf-8-sig") as f:  # PowerShell 5.1 writes a BOM
            w = json.load(f)
        start = datetime.fromisoformat(w["start"])
        end = datetime.fromisoformat(w["end"]) if w.get("end") else datetime.now()
        return start - timedelta(minutes=1), end + timedelta(minutes=2)
    except (OSError, ValueError, KeyError):
        return None


def recent_git_pull(since):
    """True if git's reflog shows a pull/merge/reset of AllTalk's code since `since`."""
    for line in git("reflog", "--date=iso-strict", "-n", "20").splitlines():
        # e.g.  f16117e HEAD@{2026-09-25T19:28:42-07:00}: pull --ff-only origin alltalkbeta: Fast-forward
        try:
            stamp = line.split("HEAD@{", 1)[1].split("}", 1)[0]
            when = datetime.fromisoformat(stamp).replace(tzinfo=None)
        except (IndexError, ValueError):
            continue
        if when >= since and any(k in line for k in (": pull", ": merge", ": reset", ": checkout")):
            return True
    return False


def is_developer_update(rel, mtime, window, pulled):
    t = datetime.fromtimestamp(mtime)
    if window and window[0] <= t <= window[1]:
        return True
    if pulled:
        # Developer update only if the file now exactly matches the developer's code.
        status = git("status", "--porcelain", "--", rel.replace(os.sep, "/"))
        tracked = git("ls-files", "--", rel.replace(os.sep, "/")).strip()
        return bool(tracked) and status.strip() == ""
    return False


SHOW = 5   # example file names per group in the message box (the log has every file)


def grouped(paths, indent="  "):
    """'N files in <folder>' per folder, with a few example names."""
    groups = {}
    for p in paths:
        groups.setdefault(os.path.dirname(p) or ".", []).append(os.path.basename(p))
    lines = []
    for folder in sorted(groups):
        names = sorted(groups[folder])
        where = "the main folder" if folder == "." else folder + "\\"
        if len(names) == 1:
            lines.append(f"{indent}{os.path.join(folder, names[0]) if folder != '.' else names[0]}")
            continue
        more = f" ... and {len(names) - SHOW} more" if len(names) > SHOW else ""
        lines.append(f"{indent}{len(names)} files in {where}: " + ", ".join(names[:SHOW]) + more)
    return "\n".join(lines)


def grouped_moves(moved):
    """'N files from <folder> moved to <repo folder>' with a few example names."""
    groups = {}
    for src, dest in moved.items():
        groups.setdefault((os.path.dirname(src) or ".", dest), []).append(os.path.basename(src))
    lines = []
    for (folder, dest) in sorted(groups):
        names = sorted(groups[(folder, dest)])
        where = "the main folder" if folder == "." else folder + "\\"
        more = f" ... and {len(names) - SHOW} more" if len(names) > SHOW else ""
        noun = "file" if len(names) == 1 else "files"
        lines.append(f"  {len(names)} {noun} from {where} moved to {dest}\\\n    " + ", ".join(names[:SHOW]) + more)
    return "\n".join(lines)


def find_moves(missing, known):
    """{missing file: REPO_alltalk folder it now sits in} for files found in REPO_alltalk with
    the same name and the same timestamp (a move keeps the timestamp)."""
    index = {}
    for root, dirs, names in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for n in names:
            index.setdefault(n.lower(), []).append(os.path.join(root, n))
    moved = {}
    for r in missing:
        for cand in index.get(os.path.basename(r).lower(), []):
            try:
                if abs(os.stat(cand).st_mtime - known[r]) < 2:
                    moved[r] = os.path.dirname(cand)
                    break
            except OSError:
                pass
    return moved


def rvc_training_processes():
    try:
        import psutil
    except ImportError:
        return []
    found = []
    for p in psutil.process_iter(["pid", "cmdline"]):
        cmd = " ".join(p.info.get("cmdline") or [])
        low = cmd.lower().replace("\\", "/")
        if "rvc" in low and "/train" in low:
            found.append(f"PID {p.info['pid']}: {cmd}")
    return found


def check(known):
    now = time.time()
    current = scan()
    window = update_window()
    pulled = recent_git_pull(datetime.fromtimestamp(now - MODIFIED_WINDOW))

    new = sorted(r for r in current if r not in known)
    deleted = sorted(r for r in known if r not in current)
    modified = sorted(r for r, m in current.items()
                      if r in known and m > now - MODIFIED_WINDOW and m != known[r])

    dev_new = [r for r in new if is_developer_update(r, current[r], window, pulled)]
    dev_mod = [r for r in modified if is_developer_update(r, current[r], window, pulled)]
    new = [r for r in new if r not in dev_new]
    modified = [r for r in modified if r not in dev_mod]
    if pulled:
        # Only files the developer's update itself removed from AllTalk's code are not
        # alerted; any other missing file (the user's included) is always reported.
        removed_by_update = {p.strip() for p in
                             git("diff", "--name-only", "--diff-filter=D", "ORIG_HEAD", "HEAD").splitlines()}
        deleted = [r for r in deleted if r.replace(os.sep, "/") not in removed_by_update]
    if dev_new or dev_mod:
        log(f"developer update recognised: {len(dev_new)} new, {len(dev_mod)} changed files - not alerted")

    # Files gone from AllTalk's folder: moved into REPO_alltalk (same name and timestamp
    # found there), or deleted (found nowhere in REPO_alltalk).
    moved = find_moves(deleted, known) if deleted else {}
    deleted = [r for r in deleted if r not in moved]

    rvc = rvc_training_processes()
    problems, full = [], []
    if new:
        problems.append("NEW FILES in AllTalk's app folder (these belong in REPO_alltalk):\n" + grouped(new))
        full.append("NEW:\n  " + "\n  ".join(new))
    if modified:
        problems.append("MODIFIED in the last 60 minutes (AllTalk's own files):\n" + grouped(modified))
        full.append("MODIFIED:\n  " + "\n  ".join(modified))
    if moved:
        problems.append("MOVED out of AllTalk's app folder into REPO_alltalk:\n" + grouped_moves(moved))
        full.append("MOVED:\n  " + "\n  ".join(f"{r} -> {moved[r]}" for r in sorted(moved)))
    if deleted:
        problems.append("DELETED from AllTalk's app folder (not found anywhere in REPO_alltalk):\n" + grouped(deleted))
        full.append("DELETED:\n  " + "\n  ".join(deleted))
    if rvc:
        rvc_files = sorted(r for r in new if "logs" in r.split(os.sep))
        problems.append("RVC TRAINING is running:\n  " + "\n  ".join(rvc) +
                        ("\n  Files it produced in AllTalk's folder:\n" + grouped(rvc_files, indent="    ") if rvc_files else ""))
    if problems:
        log("full list of changes found:\n" + "\n".join(full))
        alert("AllTalk app folder watcher",
              "Changes were found inside app_cabinet\\alltalk_tts since the last check.\n"
              "The watcher only reports: it has not changed, moved or deleted anything itself.\n\n" +
              "\n\n".join(problems) + f"\n\nFull list of every file: {LOG_FILE}")
    else:
        log(f"check OK: {len(current)} files, nothing new, nothing modified in the last 60 minutes")

    # Remember what is there now, so each file is reported once.
    with open(KNOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f)
    return current


def alltalk_running():
    try:
        import psutil
    except ImportError:
        return True
    app = os.path.normcase(APP)
    for p in psutil.process_iter(["cmdline"]):
        cmd = " ".join(p.info.get("cmdline") or [])
        if "tts_server.py" in cmd and app in os.path.normcase(cmd):
            return True
        if SERVER_PID and p.pid == SERVER_PID:
            return True
    return False


def take_lock():
    """Only one watcher at a time."""
    try:
        import psutil
        with open(LOCK_FILE, encoding="utf-8") as f:
            other = int(f.read().strip())
        if other != os.getpid() and psutil.pid_exists(other):
            p = psutil.Process(other)
            if "alltalk_folder_watcher.py" in " ".join(p.cmdline()):
                return False
    except (OSError, ValueError, ImportError, Exception):  # noqa: BLE001 - stale/unreadable lock
        pass
    with open(LOCK_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    return True


def main():
    os.makedirs(LOGS, exist_ok=True)
    if not take_lock():
        return
    log(f"watcher started (AllTalk server PID {SERVER_PID}), checking every 60 minutes")
    try:
        with open(KNOWN_FILE, encoding="utf-8") as f:
            known = json.load(f)
    except (OSError, ValueError):
        known = scan()
        with open(KNOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(known, f)
        log(f"first run: recorded {len(known)} existing files as the starting point")
    known = check(known)
    next_check = time.time() + CHECK_EVERY
    gone_since = None
    while True:
        time.sleep(LIFE_POLL)
        if alltalk_running():
            gone_since = None
        else:
            gone_since = gone_since or time.time()
            if time.time() - gone_since > RESTART_GRACE:
                log("AllTalk has stopped - watcher stopping")
                break
        if time.time() >= next_check:
            known = check(known)
            next_check = time.time() + CHECK_EVERY
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


if __name__ == "__main__":
    main()
