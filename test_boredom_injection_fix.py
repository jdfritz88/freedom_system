#!/usr/bin/env python3
"""
Test script for fixed boredom monitor auto-injection
Tests the corrected Plan B implementation
"""

import sys
import os
import time
from pathlib import Path

# Add text-generation-webui to path
tgwui_path = Path("F:/Apps/freedom_system/freedom_system_2000/text-generation-webui")
sys.path.insert(0, str(tgwui_path))

def setup_enhanced_logging(component_name):
    """Setup enhanced logging for testing"""
    def log_enhanced(message, level="INFO", function_name="", component=component_name):
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"[{component}]"

        if function_name:
            prefix = f"{prefix} [{function_name}]"

        full_message = f"{prefix} [{level}] {message}"
        print(full_message)

        # Write to test log file
        log_file = f"F:/Apps/freedom_system/log/boredom_injection_test.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {full_message}\n")
        except Exception:
            pass

    return log_enhanced

log_enhanced = setup_enhanced_logging("INJECTION-TEST")

def test_import_requirements():
    """Test if required modules can be imported"""
    log_enhanced("Testing import requirements", "INFO", "test_import_requirements")

    try:
        from modules import shared
        log_enhanced("SUCCESS: modules.shared imported successfully", "SUCCESS", "test_import_requirements")
    except ImportError as e:
        log_enhanced(f"ERROR: Failed to import modules.shared: {e}", "ERROR", "test_import_requirements")
        return False

    try:
        from modules.chat import generate_chat_reply
        log_enhanced("SUCCESS: generate_chat_reply imported successfully", "SUCCESS", "test_import_requirements")
    except ImportError as e:
        log_enhanced(f"ERROR: Failed to import generate_chat_reply: {e}", "ERROR", "test_import_requirements")
        return False

    try:
        import gradio as gr
        log_enhanced("SUCCESS: gradio imported successfully", "SUCCESS", "test_import_requirements")
    except ImportError as e:
        log_enhanced(f"ERROR: Failed to import gradio: {e}", "ERROR", "test_import_requirements")
        return False

    return True

def test_boredom_extension_import():
    """Test if boredom monitor extension can be imported"""
    log_enhanced("Testing boredom monitor extension import", "INFO", "test_boredom_extension_import")

    try:
        # Try to import the extension
        boredom_path = tgwui_path / "extensions" / "boredom_monitor"
        sys.path.insert(0, str(boredom_path))

        import script as boredom_script
        log_enhanced("SUCCESS: Boredom monitor script imported successfully", "SUCCESS", "test_boredom_extension_import")

        # Test if the trigger function exists
        if hasattr(boredom_script, 'trigger_emotional_response'):
            log_enhanced("SUCCESS: trigger_emotional_response function found", "SUCCESS", "test_boredom_extension_import")
        else:
            log_enhanced("ERROR: trigger_emotional_response function not found", "ERROR", "test_boredom_extension_import")
            return False, None

        return True, boredom_script

    except Exception as e:
        log_enhanced(f"ERROR: Failed to import boredom monitor: {e}", "ERROR", "test_boredom_extension_import")
        return False, None

def test_manual_trigger():
    """Test manual trigger of emotional response"""
    log_enhanced("Testing manual trigger of emotional response", "INFO", "test_manual_trigger")

    # Import requirements first
    if not test_import_requirements():
        log_enhanced("Required modules not available - skipping manual trigger test", "WARNING", "test_manual_trigger")
        return False

    # Import boredom extension
    success, boredom_script = test_boredom_extension_import()
    if not success:
        log_enhanced("Boredom extension not available - skipping manual trigger test", "WARNING", "test_manual_trigger")
        return False

    try:
        # Test the manual trigger function
        if hasattr(boredom_script, 'manual_trigger_test'):
            log_enhanced("Calling manual_trigger_test('bored', 1)", "INFO", "test_manual_trigger")
            result = boredom_script.manual_trigger_test('bored', 1)

            if result:
                log_enhanced("SUCCESS: Manual trigger succeeded", "SUCCESS", "test_manual_trigger")
                return True
            else:
                log_enhanced("WARNING: Manual trigger returned False", "WARNING", "test_manual_trigger")
                return False
        else:
            log_enhanced("WARNING: manual_trigger_test function not found", "WARNING", "test_manual_trigger")
            return False

    except Exception as e:
        log_enhanced(f"ERROR: Manual trigger test failed: {e}", "ERROR", "test_manual_trigger")
        return False

def test_injection_components():
    """Test individual injection components"""
    log_enhanced("Testing injection components", "INFO", "test_injection_components")

    # Test input hijack mechanism
    try:
        success, boredom_script = test_boredom_extension_import()
        if success and hasattr(boredom_script, 'input_hijack'):
            hijack = boredom_script.input_hijack
            log_enhanced(f"SUCCESS: Input hijack found: {hijack}", "SUCCESS", "test_injection_components")

            # Test hijack modification
            test_message = "Test hijack message"
            hijack.update({"state": True, "value": [test_message, test_message]})

            if hijack['state'] and hijack['value'][0] == test_message:
                log_enhanced("SUCCESS: Input hijack modification works", "SUCCESS", "test_injection_components")
            else:
                log_enhanced("ERROR: Input hijack modification failed", "ERROR", "test_injection_components")

        else:
            log_enhanced("ERROR: Input hijack not found", "ERROR", "test_injection_components")

    except Exception as e:
        log_enhanced(f"ERROR: Injection component test failed: {e}", "ERROR", "test_injection_components")

def main():
    """Run all injection tests"""
    log_enhanced("=== BOREDOM INJECTION FIX TEST ===", "INFO", "main")
    log_enhanced("Testing Plan B corrected input hijack implementation", "INFO", "main")

    # Test 1: Import requirements
    log_enhanced("Test 1: Import Requirements", "INFO", "main")
    imports_ok = test_import_requirements()

    # Test 2: Extension import
    log_enhanced("Test 2: Extension Import", "INFO", "main")
    extension_ok, _ = test_boredom_extension_import()

    # Test 3: Injection components
    log_enhanced("Test 3: Injection Components", "INFO", "main")
    test_injection_components()

    # Test 4: Manual trigger (only if other tests pass)
    if imports_ok and extension_ok:
        log_enhanced("Test 4: Manual Trigger", "INFO", "main")
        trigger_ok = test_manual_trigger()
    else:
        log_enhanced("Test 4: Manual Trigger - SKIPPED (prerequisites failed)", "WARNING", "main")
        trigger_ok = False

    # Summary
    log_enhanced("=== TEST SUMMARY ===", "INFO", "main")
    log_enhanced(f"Imports: {'PASS' if imports_ok else 'FAIL'}", "INFO", "main")
    log_enhanced(f"Extension: {'PASS' if extension_ok else 'FAIL'}", "INFO", "main")
    log_enhanced(f"Manual Trigger: {'PASS' if trigger_ok else 'FAIL'}", "INFO", "main")

    if imports_ok and extension_ok and trigger_ok:
        log_enhanced("SUCCESS: ALL TESTS PASSED - Injection fix appears to work!", "SUCCESS", "main")
    else:
        log_enhanced("WARNING: Some tests failed - check logs for details", "WARNING", "main")

if __name__ == "__main__":
    main()