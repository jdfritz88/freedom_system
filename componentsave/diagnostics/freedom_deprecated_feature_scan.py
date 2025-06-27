import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# freedom_deprecated_feature_scan.py
# Scans entire Freedom System for other deprecated features (output music, autosave git, cloud, remote)

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIRS = [os.path.join(ROOT, "componentsave"), os.path.join(ROOT, "launchers")]
PATTERNS = [
    r"music_emotion_driver",
    r"emotional_music_router",
    r"push_music_emotion",
    r"git.*push",
    r"autosave",
    r"remote_server",
    r"cloud_endpoint",
    r"firebase",
    r"mqtt",
    r"socket\.connect",
    r"requests\.post\(.*https"
]

print("\n=== Freedom System Deprecated Feature Scan ===\n")

results = []
for search_dir in SEARCH_DIRS:
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                    for pattern in PATTERNS:
                        for match in re.finditer(pattern, text):
                            results.append((full_path, match.group(0)))

if results:
    print("Deprecated references found:")
    for path, match in results:
        print(f" - {path}: {match}")
else:
    print("No deprecated logic detected.")

print("\nScan complete. Remove flagged logic if still present.")
