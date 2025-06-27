import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Save location for diagnostics manifest:
# F:/Apps/freedom_system/componentsave/diagnostics/diagnostics_manifest.py

# Purpose:
# - Tracks all test and benchmark files used by the Freedom System
# - Ensures all essential diagnostics are known and recoverable
# - Serves as the root registry for system tests

# Do not remove this file unless clearing diagnostics explicitly.
# Update it any time new tools or test reports are added.

RECORDED_FILES = [
    "ui_system_test.py",
    "freedom_ui_optimization_report.txt",
    "freedom_ui_optimization_report.md",
    "freedom_ui_optimization_report.pdf",
    "freedom_ui_optimization_report.rd",
    "Freedom-System-Full-Report-2025-06-21.md",
    "Freedom-System-Full-Report-2025-06-21.pdf",
    "Freedom-System-Full-Report format.txt",
    "diagnostics_manifest.py"
]
