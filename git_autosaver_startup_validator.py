import os

SCRIPT_PATH = "F:/Apps/freedom_system/git_autosaver.py"
STARTUP_DIR = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
BAT_FILE = os.path.join(STARTUP_DIR, "git_autosaver.bat")

print("Startup Folder:", STARTUP_DIR)
print("Expected .bat File:", BAT_FILE)

if os.path.exists(BAT_FILE):
    with open(BAT_FILE, "r") as f:
        content = f.read()
    if SCRIPT_PATH in content:
        print("✅ Confirmed: git_autosaver.bat points to the correct script.")
    else:
        print("⚠️ Found the file, but it doesn't point to the correct script.")
else:
    print("❌ Missing: git_autosaver.bat does not exist in the Startup folder.")
