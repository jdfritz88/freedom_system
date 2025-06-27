# File: F:/Apps/freedom_system/startup_ui_loader_integration.py

import os

START_BAT = "start_freedom_system.bat"
UI_LAUNCH_CMD = "python componentsave/ui_panels/gui_dashboard_window.py"
FLAG_PATH = "launchers/emotion_engine_boot_flag.py"


def ensure_flag_file():
    flag_code = """# File: launchers/emotion_engine_boot_flag.py
# Sets boot flag for emotion engine startup.

with open('emotion_engine.flag', 'w') as f:
    f.write('READY')

print('[FLAG] Emotion engine boot flag created.')
"""
    full_flag_path = os.path.join(".", FLAG_PATH)
    os.makedirs(os.path.dirname(full_flag_path), exist_ok=True)
    with open(full_flag_path, 'w', encoding='utf-8') as f:
        f.write(flag_code)
    print("[INJECTED] emotion_engine_boot_flag.py regenerated.")


def inject_ui_launcher():
    if not os.path.exists(START_BAT):
        print(f"[ERROR] Missing: {START_BAT}")
        return

    with open(START_BAT, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if UI_LAUNCH_CMD not in ''.join(lines):
        lines.insert(0, UI_LAUNCH_CMD + "\n")

    with open(START_BAT, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("[PATCH APPLIED] UI dashboard launch embedded into BAT.")


if __name__ == "__main__":
    ensure_flag_file()
    inject_ui_launcher()
