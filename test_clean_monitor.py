#!/usr/bin/env python3
"""
Test the clean DirectCallMonitor implementation
Validates that we fixed the inheritance issues
"""

import ast
import json
from pathlib import Path

def test_clean_implementation():
    """Test that the implementation is now clean without inheritance issues"""
    script_path = Path("freedom_system_2000/text-generation-webui/extensions/boredom_monitor/script.py")

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    results = {
        "inheritance_removed": False,
        "api_imports_removed": False,
        "clean_monitor_class": False,
        "no_parent_dependencies": False
    }

    # Check that we removed inheritance
    if "class DirectCallBoredomDetector(BoredomDetector):" not in content:
        results["inheritance_removed"] = True

    # Check that we removed BoredomDetector import
    if "from .idle_boredom_detector import BoredomDetector" not in content:
        results["api_imports_removed"] = True

    # Check that we have clean DirectCallMonitor
    if "class DirectCallMonitor:" in content:
        results["clean_monitor_class"] = True

    # Check no super() calls or parent method dependencies
    if "super().__init__" not in content and "self.config.get" not in content:
        results["no_parent_dependencies"] = True

    return results

def main():
    print("=" * 60)
    print("CLEAN DIRECTCALLMONITOR IMPLEMENTATION TEST")
    print("=" * 60)

    results = test_clean_implementation()

    print("\nImplementation validation:")
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {check}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS: Clean implementation completed")
        print("- No inheritance from API-based classes")
        print("- No config dependencies")
        print("- Purpose-built for direct calls")
    else:
        print("ISSUES: Implementation still has problems")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    main()