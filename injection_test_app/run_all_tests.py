"""
Comprehensive Injection Test Runner
===================================

This script runs ALL injection tests with FULL verification.
It tests every documented injection method and verifies that
messages actually appear in the UI.

CRITICAL DIFFERENCE FROM PREVIOUS TESTS:
- Previous tests only SENT messages and ASSUMED success
- This test VERIFIES that messages actually appear in the UI
- Uses multiple verification methods for confirmation

Usage:
    python run_all_tests.py [--quick] [--full] [--selenium] [--method METHOD]

Author: Freedom System
"""

import sys
import os
import time
import json
import logging
import argparse
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# CRITICAL: Parse our arguments BEFORE any imports that might use argparse
# The text-generation-webui modules/shared.py parses sys.argv on import
# which conflicts with our test arguments. We parse first, then clear sys.argv.
_original_argv = sys.argv.copy()
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument('--quick', action='store_true')
_parser.add_argument('--full', action='store_true')
_parser.add_argument('--selenium', action='store_true')
_parser.add_argument('--method', type=str)
_parsed_args, _remaining = _parser.parse_known_args()

# Reset sys.argv to prevent conflicts with webui's argument parser
sys.argv = [sys.argv[0]]

# Configure paths
SCRIPT_DIR = Path(__file__).parent
LOG_DIR = Path("F:/Apps/freedom_system/log")
LOG_DIR.mkdir(exist_ok=True)
WEBUI_START_BAT = Path("F:/Apps/freedom_system/app_cabinet/text-generation-webui/start_windows.bat")

# Configure logging
log_file = LOG_DIR / f"injection_test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)

logger = logging.getLogger("TestRunner")


class WebUIAlarmDialog:
    """
    Non-blocking alarm dialog that alerts user when WebUI is not running.
    - Does NOT block other windows
    - Does NOT stay always on top
    - Has a Proceed button to continue once WebUI is started
    """

    def __init__(self):
        self.proceed_clicked = False
        self.root = None
        self.status_label = None
        self.proceed_btn = None
        self._check_thread = None
        self._running = True

    def show(self):
        """Show the alarm dialog (non-blocking)."""
        self.root = tk.Tk()
        self.root.title("Injection Test - WebUI Not Running")
        self.root.geometry("550x320")
        self.root.resizable(False, False)

        # Don't make it always on top - just a normal window
        self.root.attributes('-topmost', False)

        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.root.winfo_screenheight() // 2) - (320 // 2)
        self.root.geometry(f"550x320+{x}+{y}")

        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Warning icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        warning_label = ttk.Label(
            title_frame,
            text="WARNING",
            font=('Segoe UI', 16, 'bold'),
            foreground='#d9534f'
        )
        warning_label.pack()

        # Message
        msg_label = ttk.Label(
            main_frame,
            text="text-generation-webui is NOT running!\n\nThe injection tests require the WebUI to be running.",
            font=('Segoe UI', 11),
            justify=tk.CENTER,
            wraplength=500
        )
        msg_label.pack(pady=(0, 15))

        # Instructions frame
        instr_frame = ttk.LabelFrame(main_frame, text="Instructions", padding="10")
        instr_frame.pack(fill=tk.X, pady=(0, 15))

        instr_text = (
            "1. Start the WebUI using this batch file:\n"
            f"   {WEBUI_START_BAT}\n\n"
            "2. Wait for the WebUI to fully load (you'll see 'Running on local URL')\n\n"
            "3. Click 'Proceed' below to continue the tests"
        )
        instr_label = ttk.Label(
            instr_frame,
            text=instr_text,
            font=('Consolas', 9),
            justify=tk.LEFT
        )
        instr_label.pack(anchor=tk.W)

        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(
            status_frame,
            text="Status: Checking for WebUI...",
            font=('Segoe UI', 10),
            foreground='#888888'
        )
        self.status_label.pack()

        # Button frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        self.proceed_btn = ttk.Button(
            btn_frame,
            text="Proceed",
            command=self._on_proceed,
            state=tk.DISABLED
        )
        self.proceed_btn.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_btn.pack(side=tk.RIGHT)

        # Start background thread to check WebUI status
        self._check_thread = threading.Thread(target=self._check_webui_loop, daemon=True)
        self._check_thread.start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Run the dialog (this blocks until closed)
        self.root.mainloop()

        return self.proceed_clicked

    def _check_webui_loop(self):
        """Background thread that periodically checks if WebUI is running."""
        import requests

        while self._running:
            try:
                response = requests.get("http://127.0.0.1:7860", timeout=3)
                if response.status_code == 200:
                    self._update_status(True)
                else:
                    self._update_status(False)
            except:
                self._update_status(False)

            time.sleep(2)  # Check every 2 seconds

    def _update_status(self, webui_running: bool):
        """Update the status label and proceed button (thread-safe)."""
        if self.root is None:
            return

        def update():
            if webui_running:
                self.status_label.config(
                    text="Status: WebUI DETECTED on port 7860",
                    foreground='#5cb85c'
                )
                self.proceed_btn.config(state=tk.NORMAL)
            else:
                self.status_label.config(
                    text="Status: WebUI NOT detected - waiting...",
                    foreground='#d9534f'
                )
                self.proceed_btn.config(state=tk.DISABLED)

        try:
            self.root.after(0, update)
        except:
            pass  # Window may have been closed

    def _on_proceed(self):
        """Handle Proceed button click."""
        self.proceed_clicked = True
        self._running = False
        self.root.destroy()

    def _on_cancel(self):
        """Handle Cancel button or window close."""
        self.proceed_clicked = False
        self._running = False
        self.root.destroy()


def check_webui_running() -> bool:
    """Quick check if WebUI is running."""
    try:
        import requests
        response = requests.get("http://127.0.0.1:7860", timeout=3)
        return response.status_code == 200
    except:
        return False


def wait_for_webui() -> bool:
    """
    Check if WebUI is running. If not, show alarm dialog and wait.
    Returns True if user clicked Proceed, False if cancelled.
    """
    if check_webui_running():
        logger.info("WebUI is already running on port 7860")
        return True

    logger.warning("WebUI is NOT running - showing alarm dialog")
    print("\n" + "=" * 60)
    print("  ALARM: text-generation-webui is NOT running!")
    print("=" * 60)
    print(f"\nPlease start the WebUI using:\n  {WEBUI_START_BAT}")
    print("\nA dialog window will appear. Click 'Proceed' once the WebUI is running.\n")

    dialog = WebUIAlarmDialog()
    result = dialog.show()

    if result:
        logger.info("User clicked Proceed - continuing with tests")
        # Give a moment for any final initialization
        time.sleep(1)
        return True
    else:
        logger.info("User cancelled - exiting")
        return False


def print_banner():
    """Print test runner banner."""
    banner = """
================================================================================
                    COMPREHENSIVE INJECTION TEST RUNNER
================================================================================
  This test runner verifies that injected messages ACTUALLY appear in the UI
  Previous tests FAILED because they only sent messages without verification
================================================================================
"""
    print(banner)
    logger.info("=" * 78)
    logger.info("COMPREHENSIVE INJECTION TEST RUNNER")
    logger.info("=" * 78)


def check_prerequisites() -> Dict[str, bool]:
    """Check all prerequisites for testing."""
    logger.info("Checking prerequisites...")

    prereqs = {
        'webui_modules': False,
        'requests': False,
        'selenium': False,
        'webui_running': False,
        'openai_api_running': False
    }

    # Check if we can import webui modules
    try:
        sys.path.insert(0, str(Path("F:/Apps/freedom_system/app_cabinet/text-generation-webui")))
        from modules import shared
        prereqs['webui_modules'] = True
        logger.info("  [OK] text-generation-webui modules available")
    except ImportError as e:
        logger.warning(f"  [NO] text-generation-webui modules: {e}")

    # Check requests
    try:
        import requests
        prereqs['requests'] = True
        logger.info("  [OK] requests library available")
    except ImportError:
        logger.warning("  [NO] requests library not installed")

    # Check selenium
    try:
        from selenium import webdriver
        prereqs['selenium'] = True
        logger.info("  [OK] selenium available")
    except ImportError:
        logger.warning("  [NO] selenium not installed (optional)")

    # Check if WebUI is running
    if prereqs['requests']:
        import requests
        try:
            response = requests.get("http://127.0.0.1:7860", timeout=5)
            prereqs['webui_running'] = response.status_code == 200
            if prereqs['webui_running']:
                logger.info("  [OK] text-generation-webui running on port 7860")
            else:
                logger.warning("  [NO] text-generation-webui not responding properly")
        except:
            logger.warning("  [NO] text-generation-webui not running on port 7860")

    # Check if OpenAI API is running
    if prereqs['requests']:
        import requests
        try:
            response = requests.get("http://127.0.0.1:5000/v1/models", timeout=5)
            prereqs['openai_api_running'] = response.status_code == 200
            if prereqs['openai_api_running']:
                logger.info("  [OK] OpenAI API running on port 5000")
            else:
                logger.warning("  [NO] OpenAI API not responding properly")
        except:
            logger.warning("  [NO] OpenAI API not running on port 5000")

    return prereqs


def run_quick_tests(prereqs: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Run quick tests - most reliable methods only."""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING QUICK TESTS (Most Reliable Methods)")
    logger.info("=" * 60)

    results = []

    if prereqs['webui_modules']:
        from injection_tester import InjectionTester, InjectionMethod

        tester = InjectionTester()

        # Test 1: CHARACTER_GREETING (PROVEN WORKING - runs FIRST)
        # This is the EXACT pattern used by text-generation-webui to inject greetings
        logger.info("\n--- Test 1: CHARACTER_GREETING (PROVEN WORKING) ---")
        result = tester.test_injection_method(
            InjectionMethod.CHARACTER_GREETING,
            f"QUICK-TEST-1: Character greeting pattern at {datetime.now().strftime('%H:%M:%S')}"
        )
        results.append({
            'name': 'CHARACTER_GREETING (Proven Pattern)',
            'success': result.overall_success,
            'injection_success': result.injection.success,
            'confirmations': result.confirmation_count,
            'total_verifications': len(result.verifications)
        })

        time.sleep(1)

        # Test 2: Direct history manipulation
        logger.info("\n--- Test 2: Direct History Manipulation ---")
        result = tester.test_injection_method(
            InjectionMethod.DIRECT_HISTORY,
            f"QUICK-TEST-2: Direct history at {datetime.now().strftime('%H:%M:%S')}"
        )
        results.append({
            'name': 'Direct History',
            'success': result.overall_success,
            'injection_success': result.injection.success,
            'confirmations': result.confirmation_count,
            'total_verifications': len(result.verifications)
        })

        time.sleep(1)

        # Test 3: send_dummy_reply
        logger.info("\n--- Test 3: send_dummy_reply ---")
        result = tester.test_injection_method(
            InjectionMethod.SEND_DUMMY_REPLY,
            f"QUICK-TEST-3: send_dummy_reply at {datetime.now().strftime('%H:%M:%S')}"
        )
        results.append({
            'name': 'send_dummy_reply',
            'success': result.overall_success,
            'injection_success': result.injection.success,
            'confirmations': result.confirmation_count,
            'total_verifications': len(result.verifications)
        })

    if prereqs['openai_api_running']:
        from injection_tester import InjectionTester, InjectionMethod

        tester = InjectionTester()

        # Test 4: OpenAI API
        logger.info("\n--- Test 4: OpenAI API ---")
        result = tester.test_injection_method(
            InjectionMethod.OPENAI_CHAT_API,
            f"QUICK-TEST-4: What time is it?"
        )
        results.append({
            'name': 'OpenAI API',
            'success': result.overall_success,
            'injection_success': result.injection.success,
            'confirmations': result.confirmation_count,
            'total_verifications': len(result.verifications)
        })

    return results


def run_full_tests(prereqs: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Run full tests - all available methods with all 14 verifications."""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING FULL TESTS (All Methods x All 14 Verifications)")
    logger.info("=" * 60)

    results = []

    if prereqs['webui_modules']:
        from injection_tester import InjectionTester, InjectionMethod

        tester = InjectionTester()

        # Test methods in order - CHARACTER_GREETING first (proven working)
        methods_to_test = [
            # Test #1: The PROVEN working method - exactly how text-generation-webui works
            InjectionMethod.CHARACTER_GREETING,
            InjectionMethod.HISTORY_MODIFIER,
            InjectionMethod.SEND_DUMMY_REPLY,
            InjectionMethod.DIRECT_HISTORY,
        ]

        if prereqs['openai_api_running']:
            methods_to_test.append(InjectionMethod.OPENAI_CHAT_API)

        for i, method in enumerate(methods_to_test, 1):
            logger.info(f"\n--- Test {i}/{len(methods_to_test)}: {method.value} ---")
            result = tester.test_injection_method(
                method,
                f"FULL-TEST-{i}: {method.value} at {datetime.now().strftime('%H:%M:%S')}"
            )
            results.append({
                'name': method.value,
                'success': result.overall_success,
                'injection_success': result.injection.success,
                'confirmations': result.confirmation_count,
                'verifications': [
                    {'method': v.method.value, 'verified': v.verified}
                    for v in result.verifications
                ]
            })
            time.sleep(1)

        # Save detailed report
        report = tester.generate_report()
        print(report)
        tester.save_report()

    return results


def run_selenium_tests(prereqs: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Run tests with Selenium verification."""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING SELENIUM TESTS (External Browser Verification)")
    logger.info("=" * 60)

    results = []

    if not prereqs['selenium']:
        logger.warning("Selenium not available - skipping")
        return results

    try:
        from selenium_verifier import SeleniumVerifier, ComprehensiveVerifier

        # Initialize verifier
        verifier = SeleniumVerifier(headless=True)
        logger.info("Selenium browser initialized")

        # Get initial state
        initial_count = verifier.get_message_count()
        logger.info(f"Initial message count: {initial_count}")

        # Take screenshot of initial state
        verifier.take_screenshot(str(LOG_DIR / "selenium_initial_state.png"))

        # If webui modules available, test injection with Selenium verification
        if prereqs['webui_modules']:
            from injection_tester import InjectionTester, InjectionMethod

            tester = InjectionTester()
            test_message = f"SELENIUM-TEST: Injected at {datetime.now().strftime('%H:%M:%S.%f')}"

            # Inject via direct history
            logger.info(f"Injecting test message: '{test_message}'")
            injection_result = tester.inject_via_direct_history(test_message)

            # Wait for potential UI update
            time.sleep(2)

            # Verify with Selenium
            logger.info("Verifying with Selenium...")
            selenium_result = verifier.verify_message_exists(test_message, timeout=10)

            results.append({
                'name': 'Selenium Verification',
                'injection_success': injection_result.success,
                'selenium_verified': selenium_result.verified,
                'duration_ms': selenium_result.duration_ms,
                'details': selenium_result.details
            })

            # Take screenshot of result
            verifier.take_screenshot(str(LOG_DIR / "selenium_after_injection.png"))

        verifier.close()

    except Exception as e:
        logger.error(f"Selenium test error: {e}")
        results.append({
            'name': 'Selenium Verification',
            'error': str(e)
        })

    return results


def print_summary(all_results: Dict[str, List[Dict[str, Any]]]):
    """Print test summary."""
    print("\n" + "=" * 78)
    print("TEST SUMMARY")
    print("=" * 78)

    total_tests = 0
    total_success = 0
    total_verified = 0

    for category, results in all_results.items():
        if results:
            print(f"\n{category.upper()}:")
            for result in results:
                total_tests += 1
                status = "PASS" if result.get('success') or result.get('selenium_verified') else "FAIL"
                if status == "PASS":
                    total_success += 1
                    if result.get('confirmations', 0) > 0 or result.get('selenium_verified'):
                        total_verified += 1

                print(f"  [{status}] {result.get('name', 'Unknown')}")
                if result.get('confirmations'):
                    print(f"       Confirmations: {result['confirmations']}")
                if result.get('error'):
                    print(f"       Error: {result['error']}")

    print("\n" + "-" * 78)
    print(f"TOTAL: {total_success}/{total_tests} tests passed")
    print(f"VERIFIED: {total_verified}/{total_tests} tests verified in UI")

    if total_verified == total_tests and total_tests > 0:
        print("\n*** ALL TESTS PASSED AND VERIFIED ***")
    elif total_verified > 0:
        print(f"\n*** {total_verified} tests successfully VERIFIED in UI ***")
    else:
        print("\n*** WARNING: No tests were verified in UI ***")

    print("=" * 78)


def main():
    """Main entry point."""
    # Use pre-parsed arguments (parsed at module load before webui imports)
    # This avoids conflicts with text-generation-webui's argument parser
    args = _parsed_args

    print_banner()

    # FIRST: Check if WebUI is running, show alarm dialog if not
    if not wait_for_webui():
        print("\nTest cancelled by user.")
        logger.info("Test cancelled - WebUI not started")
        return

    print("\nWebUI detected! Continuing with tests...\n")

    # Check prerequisites
    prereqs = check_prerequisites()

    # Determine what to run
    all_results = {}

    if args.method:
        # Test specific method
        from injection_tester import InjectionTester, InjectionMethod
        try:
            method = InjectionMethod(args.method)
            tester = InjectionTester()
            result = tester.test_injection_method(method)
            all_results['specific'] = [{
                'name': method.value,
                'success': result.overall_success,
                'confirmations': result.confirmation_count
            }]
        except ValueError:
            logger.error(f"Unknown method: {args.method}")
            from injection_tester import InjectionMethod
            logger.info(f"Available: {[m.value for m in InjectionMethod]}")
            return

    elif args.full:
        all_results['full'] = run_full_tests(prereqs)
        if args.selenium:
            all_results['selenium'] = run_selenium_tests(prereqs)

    elif args.selenium:
        all_results['quick'] = run_quick_tests(prereqs)
        all_results['selenium'] = run_selenium_tests(prereqs)

    else:
        # Default: quick tests
        all_results['quick'] = run_quick_tests(prereqs)

    # Print summary
    print_summary(all_results)

    # Save results to JSON
    results_file = LOG_DIR / f"injection_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'prerequisites': prereqs,
            'results': all_results
        }, f, indent=2, default=str)
    logger.info(f"\nResults saved to: {results_file}")
    logger.info(f"Log saved to: {log_file}")


if __name__ == "__main__":
    main()
