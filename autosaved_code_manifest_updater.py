import os
import datetime

SOURCE_PATH = "F:/Apps/freedom_system/autosaved_code"
MANIFEST_FILE = os.path.join(SOURCE_PATH, "autosaved_manifest.txt")

def update_manifest():
    files = [f for f in os.listdir(SOURCE_PATH) if f.endswith(".py") and not f.startswith(".")]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Autosaved Code Manifest — Last updated {timestamp}\n\n")
        for file in sorted(files):
            f.write(f"- {file}\n")

    print(f"✅ Manifest updated: {MANIFEST_FILE}")

if __name__ == "__main__":
    update_manifest()
