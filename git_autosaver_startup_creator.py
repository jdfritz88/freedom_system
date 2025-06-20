import os
from pathlib import Path

# Define paths
SCRIPT_PATH = "F:/Apps/freedom_system/git_autosaver.py"
STARTUP_DIR = os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
BAT_FILE = os.path.join(STARTUP_DIR, "git_autosaver.bat")

# Create batch file contents
batch_contents = f"@echo off\nstart /min python \"{SCRIPT_PATH}\""

# Make sure the startup folder exists
Path(STARTUP_DIR).mkdir(parents=True, exist_ok=True)

# Write the .bat file
with open(BAT_FILE, "w") as f:
    f.write(batch_contents)

print(f"✅ git_autosaver.bat created at: {BAT_FILE}")
