# PATCH: embed_dashboard_into_startup.py
# Location: F:/Apps/freedom_system/embed_dashboard_into_startup.py

import os

BAT_PATH = r"F:\Apps\freedom_system\start_freedom_system.bat"
DASHBOARD_LAUNCH = "python componentsave/ui_panels/gui_dashboard_window.py"


def inject_dashboard_launcher():
    if not os.path.exists(BAT_PATH):
        print(f"[ERROR] Missing: {BAT_PATH}")
        return

    with open(BAT_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove existing duplicates
    lines = [line for line in lines if DASHBOARD_LAUNCH not in line.strip()]

    # Find where to insert – after boot flag checks
    insert_index = 0
    for i, line in enumerate(lines):
        if "start_emotion_engine_flag_check.py" in line:
            insert_index = i + 1
            break

    lines.insert(insert_index, f"{DASHBOARD_LAUNCH}\n")

    with open(BAT_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    print("[PATCH APPLIED] Dashboard launcher injected into start_freedom_system.bat")


if __name__ == "__main__":
    inject_dashboard_launcher()
