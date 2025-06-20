import ctypes
import sys
import os
from pathlib import Path

script_path = Path("F:/Apps/freedom_system/freedom_git_commit_fix_admin_main.py")

if not script_path.exists():
    print(f"❌ Could not find: {script_path}")
    sys.exit(1)

ctypes.windll.shell32.ShellExecuteW(
    None,
    "runas",
    sys.executable,
    f'"{script_path}"',
    None,
    1
)
