import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# freedom_music_output_hook_scan.py
# Scans the Freedom System for any references to music output logic

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIRS = [
    os.path.join(ROOT, "componentsave"),
    os.path.join(ROOT, "launchers")
]
PATTERNS = [
    r"import .*music_emotion_driver",
    r"from .*music_emotion_driver",
    r"import .*emotional_music_router",
    r"from .*emotional_music_router",
    r"play_music",
    r"trigger_music_output",
    r"emotion.*music.*output"
]

print("\n=== Freedom Music Output Hook Scan ===\n")

matches = []
for search_dir in SEARCH_DIRS:
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for pattern in PATTERNS:
                        for match in re.finditer(pattern, content):
                            matches.append((full_path, match.group(0)))

if matches:
    print("Potential music output hooks found:")
    for path, line in matches:
        print(f" - {path}: {line}")
else:
    print("No music output references found.")

print("\nScan complete. Review and manually remove any listed references if they exist.")
