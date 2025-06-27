from pathlib import Path

# Define the root of the Freedom System
freedom_root = Path("F:/Apps/freedom_system")
log_output = Path("F:/Apps/freedom_system/componentsave/diagnostics/freedom_system_scan_log.txt")

# Scan all files including nested folders
files = list(freedom_root.rglob("*"))
relative_paths = [str(file.relative_to(freedom_root)) for file in files]

# Write to log file
with log_output.open("w", encoding="utf-8") as log:
    log.write("📦 Freedom System – Full Folder and File Scan (Nested Layouts):\n")
    log.write(f"Total files and folders found: {len(relative_paths)}\n\n")
    for path in relative_paths:
        log.write(f" - {path}\n")

print(f"Scan complete. Log saved to: {log_output}")
