import os
from datetime import datetime

# Set the folder path
base_folder = r"F:\Apps\freedom_system\componentsave\ui_panels"
log_path = r"F:\Apps\freedom_system\componentsave\diagnostics\ui_panels_file_list.txt"

# Prepare list
py_files = []

# Walk all subfolders
for root, dirs, files in os.walk(base_folder):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, base_folder)
            py_files.append(relative_path)

# Write to file
os.makedirs(os.path.dirname(log_path), exist_ok=True)
with open(log_path, "w", encoding="utf-8") as log:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.write(f"[UI Panel File Scan] {timestamp}\n")
    log.write(f"Total .py files found: {len(py_files)}\n\n")
    for file in sorted(py_files):
        log.write(f"{file}\n")

# Print to screen
print(f"[UI Panel File Scan] {timestamp}")
print(f"Total .py files found: {len(py_files)}\n")
for file in sorted(py_files):
    print(file)
