#!/usr/bin/env python3

import sys
from pathlib import Path

print("=== PYTHON ENVIRONMENT TEST ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {Path.cwd()}")
print()

print("Python path (first 10 entries):")
for i, path in enumerate(sys.path[:10], 1):
    print(f"  {i:2d}. {path}")
print()

# Test specific packages
packages_to_test = ["fastapi", "uvicorn", "gradio", "torch"]
print("Package availability test:")
for package in packages_to_test:
    try:
        __import__(package)
        print(f"  ✓ {package} - AVAILABLE")
    except ImportError as e:
        print(f"  ✗ {package} - NOT AVAILABLE ({e})")

print()

# Check text-generation-webui specific paths
tgwui_root = Path.cwd()
print(f"Checking text-generation-webui paths from: {tgwui_root}")

env_candidates = [
    tgwui_root / "installer_files" / "env" / "Lib" / "site-packages",
    tgwui_root / "installer_files" / "conda" / "envs" / "textgen" / "Lib" / "site-packages",
    tgwui_root / "installer_files" / "conda" / "Lib" / "site-packages",
    tgwui_root / "_env" / "Lib" / "site-packages"
]

for i, candidate in enumerate(env_candidates, 1):
    exists = candidate.exists()
    print(f"  {i}. {candidate} -> {'EXISTS' if exists else 'NOT FOUND'}")

print("\n=== END TEST ===")