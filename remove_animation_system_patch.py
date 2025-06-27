import os
import shutil
import ctypes
import sys

# Define the path to the animation system folder
animation_folder = r"F:\Apps\freedom_system\componentsave\output_bridges\systems_animation"

# Log file path
log_file = r"F:\Apps\freedom_system\log\startup\Remove_AnimationSystem_Log.txt"

# Ensure the log directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Attempt to remove the animation folder and log result
with open(log_file, "w") as log:
    if os.path.exists(animation_folder):
        try:
            shutil.rmtree(animation_folder)
            log.write("[REMOVED] systems_animation folder successfully deleted.\n")
        except Exception as e:
            log.write(f"[ERROR] Failed to delete folder: {e}\n")
    else:
        log.write("[SKIPPED] systems_animation folder does not exist. Nothing to delete.\n")

    log.write("Patch execution complete.\n")

# Display message box
ctypes.windll.user32.MessageBoxW(0, "Animation system removed.\nCheck log for details.", "Patch Complete", 0x40)

# Pause the terminal window
os.system("pause")
