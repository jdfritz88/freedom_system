# ==========================================
# BOREDOM MONITOR EXTENSION - INSTALL SCRIPT
# Creates local venv + installs requirements
# ==========================================

import os
import subprocess
import sys

ext_dir = os.path.dirname(__file__)
venv_dir = os.path.join(ext_dir, "venv")
req_file = os.path.join(ext_dir, "requirements.txt")


def install():
    if not os.path.exists(venv_dir):
        print("[Installer] Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

    pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    print("[Installer] Installing requirements...")
    subprocess.check_call([pip, "install", "-r", req_file])


if __name__ == "__main__":
    install()
