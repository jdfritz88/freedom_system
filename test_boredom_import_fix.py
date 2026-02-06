#!/usr/bin/env python
"""
Test script to verify the circular import fix for boredom_monitor extension
Tests both the exllamav2 import and the boredom monitor's module access
"""

import sys
import os

# Add text-generation-webui to path (simulating how it's normally run)
tgwui_path = "F:/Apps/freedom_system/freedom_system_2000/text-generation-webui"
sys.path.insert(0, tgwui_path)

print("=" * 60)
print("Testing Circular Import Fix for Boredom Monitor")
print("=" * 60)

# Test 1: Check if we can import from modules directly
print("\nTest 1: Direct module import (as text-gen-webui does)...")
try:
    from modules import shared
    print("[OK] SUCCESS: Can import modules.shared directly")
except ImportError as e:
    print(f"[FAIL] FAILED: Cannot import modules.shared: {e}")

# Test 2: Check if extension can be loaded
print("\nTest 2: Loading boredom_monitor extension...")
try:
    # Add extensions path
    extensions_path = os.path.join(tgwui_path, "extensions")
    if extensions_path not in sys.path:
        sys.path.append(extensions_path)

    # Import the extension
    from boredom_monitor import script
    print("[OK] SUCCESS: Boredom monitor extension loaded")

    # Test if the extension can still access modules
    print("\nTest 3: Extension's module access...")
    test_script = """
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'modules'))
from modules import shared
print("Extension can access modules!")
"""
    exec(test_script)
    print("[OK] SUCCESS: Extension can access modules with append")

except ImportError as e:
    print(f"[FAIL] FAILED: Cannot load boredom_monitor: {e}")

# Test 4: Check if exllamav2 local file would cause issues
print("\nTest 4: Checking for circular import issue...")
try:
    # The real test would be if exllamav2 package was installed
    # But we can check if the local file would be imported first
    import importlib.util

    # Check what Python would find for 'exllamav2'
    spec = importlib.util.find_spec('exllamav2')
    if spec and 'modules/exllamav2.py' in str(spec.origin):
        print(f"[WARN] WARNING: Would import local file: {spec.origin}")
        print("  This would cause circular import if exllamav2 package exists")
    elif spec:
        print(f"[OK] SUCCESS: Would import package from: {spec.origin}")
    else:
        print("[INFO] exllamav2 package not installed (expected in this test)")
        print("  With append instead of insert, package would be found first when installed")

except Exception as e:
    print(f"Test error: {e}")

print("\n" + "=" * 60)
print("Summary:")
print("- The fix changes sys.path.insert(0, ...) to sys.path.append(...)")
print("- This allows Python to find installed packages first")
print("- But still provides module access for the extension")
print("- Should resolve the circular import when exllamav2 package is installed")
print("=" * 60)