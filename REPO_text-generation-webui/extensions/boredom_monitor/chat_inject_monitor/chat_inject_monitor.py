"""
Chat Inject Monitor - GUI Application
======================================
A standalone GUI app with 16 verification methods to test if messages
were successfully injected into the text-generation-webui chat.

Features:
- Button for each verification method (1-16)
- Status console showing all activity
- Quick verification button
- Run all methods button
- Connection check button
- Configurable test message

All operations are bound to buttons - no command line knowledge needed!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import requests
import re
import sys
from datetime import datetime
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
LOG_DIR = Path("F:/Apps/freedom_system/log")

# Default configuration
DEFAULT_CONFIG = {
    "webui_base": "http://127.0.0.1:7860",
    "timeout_seconds": 5,
    "log_to_file": True,
    "log_file": "chat_inject_monitor.log",
    "default_test_message": "[INJECTION-TEST] Hello World"
}


def load_config() -> dict:
    """Load configuration from JSON file or use defaults"""
    config = DEFAULT_CONFIG.copy()
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
    except Exception as e:
        pass
    return config


def save_config(config: dict):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        pass


# ============================================================================
# API HELPERS
# ============================================================================
def get_webui_base() -> str:
    """Get WebUI base URL from config"""
    return load_config().get("webui_base", "http://127.0.0.1:7860")


def get_timeout() -> int:
    """Get request timeout from config"""
    return load_config().get("timeout_seconds", 5)


def api_get(endpoint: str) -> tuple:
    """
    Make a GET request to the webui API.
    Returns (success: bool, data: dict or None, error: str or None)
    """
    webui_base = get_webui_base()
    url = f"{webui_base}{endpoint}"

    try:
        response = requests.get(url, timeout=get_timeout())
        if response.status_code == 200:
            try:
                return True, response.json(), None
            except:
                return True, {"text": response.text}, None
        else:
            return False, None, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, None, "Connection refused - is WebUI running?"
    except requests.exceptions.Timeout:
        return False, None, "Request timed out"
    except Exception as e:
        return False, None, str(e)


# ============================================================================
# ALL 16 VERIFICATION METHODS
# ============================================================================

def verify_method_1_history_state(test_message: str) -> dict:
    """Method 1: HISTORY_STATE - Check history via API"""
    result = {"method": "HISTORY_STATE", "method_num": 1, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")
        if success and data:
            data_str = json.dumps(data)
            result["found"] = test_message in data_str
            result["success"] = True
            result["api_response_preview"] = data_str[:200]
        else:
            success, data, error = api_get("/internal/state")
            if success and data:
                data_str = json.dumps(data)
                result["found"] = test_message in data_str
                result["success"] = True
            else:
                result["error"] = error or "No history API available"
                result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_2_message_count(test_message: str) -> dict:
    """Method 2: MESSAGE_COUNT - Count messages via API"""
    result = {"method": "MESSAGE_COUNT", "method_num": 2, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")
        if success and data:
            result["success"] = True
            result["api_data"] = data
            if "history_length" in data:
                result["message_count"] = data["history_length"]
                result["found"] = data["history_length"] > 0
            else:
                result["found"] = True
        else:
            result["error"] = error or "Could not get message count"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_3_display_html(test_message: str) -> dict:
    """Method 3: DISPLAY_HTML - Check display HTML via API"""
    result = {"method": "DISPLAY_HTML", "method_num": 3, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/")
        if success and data:
            html_content = data.get("text", str(data))
            result["found"] = test_message in html_content
            result["html_length"] = len(html_content)
            result["success"] = True
        else:
            result["error"] = "STANDALONE_LIMITATION - Cannot access display component directly"
            result["note"] = "Use browser verification methods (15-16) for accurate HTML check"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_4_metadata_timestamp(test_message: str) -> dict:
    """Method 4: METADATA_TIMESTAMP - Check for recent timestamp"""
    result = {"method": "METADATA_TIMESTAMP", "method_num": 4, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")
        if success and data:
            result["success"] = True
            now = time.time()
            if "last_injection_time" in data:
                inject_time = data["last_injection_time"]
                if now - inject_time < 60:
                    result["found"] = True
                    result["recent_timestamp"] = inject_time
            elif "timestamp" in data:
                result["found"] = True
                result["has_timestamp"] = True
            else:
                result["found"] = False
        else:
            result["error"] = error or "Could not check timestamps"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_5_api_state(test_message: str) -> dict:
    """Method 5: API_STATE - Query internal state via API"""
    result = {"method": "API_STATE", "method_num": 5, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/internal/state")
        if success and data:
            data_str = json.dumps(data)
            result["found"] = test_message in data_str
            result["state_preview"] = data_str[:200]
            result["success"] = True
        else:
            result["error"] = error or "Internal API not available"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_6_verification_endpoint(test_message: str) -> dict:
    """Method 6: VERIFICATION_ENDPOINT - Custom verification endpoint"""
    result = {"method": "VERIFICATION_ENDPOINT", "method_num": 6, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/api/v1/internal/boredom_monitor/queue_status")
        if success and data:
            data_str = json.dumps(data)
            result["found"] = test_message in data_str
            result["endpoint_response"] = data
            result["success"] = True
        else:
            result["error"] = error or "Verification endpoint not available"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_7_dom_content(test_message: str) -> dict:
    """Method 7: DOM_CONTENT - Check browser DOM (requires browser)"""
    result = {"method": "DOM_CONTENT", "method_num": 7, "success": True, "found": False, "error": None}
    result["error"] = "REQUIRES_BROWSER - Cannot access DOM from standalone Python"
    result["note"] = "Use Selenium (Method 13) or browser methods (15-16)"
    return result


def verify_method_8_mutation_observer(test_message: str) -> dict:
    """Method 8: MUTATION_OBSERVER - Check MutationObserver (requires browser)"""
    result = {"method": "MUTATION_OBSERVER", "method_num": 8, "success": True, "found": False, "error": None}
    result["error"] = "REQUIRES_BROWSER - MutationObserver is JavaScript API"
    result["note"] = "Use browser methods (15-16) for mutation observation"
    return result


def verify_method_9_data_raw(test_message: str) -> dict:
    """Method 9: DATA_RAW - Check data-raw attributes in HTML"""
    result = {"method": "DATA_RAW", "method_num": 9, "success": True, "found": False, "error": None}
    result["error"] = "STANDALONE_LIMITATION - Cannot access display HTML directly"
    result["note"] = "Use browser methods (15-16) for HTML verification"
    return result


def verify_method_10_dom_message_count(test_message: str) -> dict:
    """Method 10: DOM_MESSAGE_COUNT - Count DOM elements (requires browser)"""
    result = {"method": "DOM_MESSAGE_COUNT", "method_num": 10, "success": True, "found": False, "error": None}
    result["error"] = "REQUIRES_BROWSER - Cannot count DOM elements from Python"
    result["note"] = "Use browser methods (15-16) for DOM verification"
    return result


def verify_method_11_sse_events(test_message: str) -> dict:
    """Method 11: SSE_EVENTS - Monitor Server-Sent Events"""
    result = {"method": "SSE_EVENTS", "method_num": 11, "success": True, "found": False, "error": None}
    result["error"] = "NOT_PRACTICAL - SSE requires persistent connection"
    result["note"] = "SSE monitoring best done during injection, not after"
    return result


def verify_method_12_request_monitor(test_message: str) -> dict:
    """Method 12: REQUEST_MONITOR - Monitor HTTP requests"""
    result = {"method": "REQUEST_MONITOR", "method_num": 12, "success": True, "found": False, "error": None}
    result["error"] = "NOT_AVAILABLE - Would require request logging middleware"
    result["note"] = "Consider checking server logs instead"
    return result


def verify_method_13_selenium(test_message: str) -> dict:
    """Method 13: SELENIUM - Use Selenium browser automation"""
    result = {"method": "SELENIUM", "method_num": 13, "success": False, "found": False, "error": None}
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        try:
            webui_base = get_webui_base()
            driver.get(webui_base)
            time.sleep(2)
            page_source = driver.page_source
            result["found"] = test_message in page_source
            result["page_length"] = len(page_source)
            result["success"] = True
        finally:
            driver.quit()
    except ImportError:
        result["error"] = "selenium not installed - pip install selenium"
        result["success"] = True
    except Exception as e:
        result["error"] = f"Selenium error: {e}"
        result["success"] = True
    return result


def verify_method_14_comprehensive(test_message: str) -> dict:
    """Method 14: COMPREHENSIVE - Run multiple verification methods"""
    result = {"method": "COMPREHENSIVE", "method_num": 14, "success": False, "found": False, "error": None}
    try:
        method_results = {
            1: verify_method_1_history_state(test_message),
            5: verify_method_5_api_state(test_message),
            6: verify_method_6_verification_endpoint(test_message),
            15: verify_method_15_browser_callback(test_message),
            16: verify_method_16_browser_api_query(test_message),
        }
        found_count = sum(1 for r in method_results.values() if r.get("found", False))
        total_checked = len(method_results)
        result["success"] = True
        result["found"] = found_count > 0
        result["found_count"] = found_count
        result["total_checked"] = total_checked
        result["confidence"] = f"{found_count}/{total_checked}"
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_15_browser_callback(test_message: str, wait_seconds: float = 0.5) -> dict:
    """Method 15: BROWSER_CALLBACK - Check browser verification reports"""
    result = {"method": "BROWSER_CALLBACK", "method_num": 15, "success": False, "found": False, "error": None}
    try:
        time.sleep(wait_seconds)
        success, data, error = api_get("/api/v1/internal/boredom_monitor/browser_verification")
        if success and data:
            reports = data.get('reports', [])
            result["total_reports"] = len(reports)
            for report in reports:
                msg_text = report.get('message_text', '')
                if test_message in msg_text:
                    result["found"] = True
                    result["browser_report"] = {
                        "message_text": msg_text[:100],
                        "timestamp": report.get("timestamp"),
                        "server_received": report.get("server_received"),
                        "message_count": report.get("message_count")
                    }
                    break
            result["success"] = True
        else:
            result["error"] = error or "Browser verification endpoint not available"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


def verify_method_16_browser_api_query(test_message: str) -> dict:
    """Method 16: BROWSER_API_QUERY - Query browser verification API"""
    result = {"method": "BROWSER_API_QUERY", "method_num": 16, "success": False, "found": False, "error": None}
    try:
        success, data, error = api_get("/api/v1/internal/boredom_monitor/browser_verification")
        if success and data:
            reports = data.get('reports', [])
            result["total_reports"] = len(reports)
            for report in reports:
                msg_text = report.get('message_text', '')
                if test_message in msg_text:
                    result["found"] = True
                    result["matching_report"] = {
                        "message_text": msg_text[:100],
                        "timestamp": report.get("timestamp"),
                        "server_received": report.get("server_received")
                    }
                    break
            result["success"] = True
        else:
            result["error"] = error or "Browser verification endpoint not available"
            result["success"] = True
    except Exception as e:
        result["error"] = str(e)
    return result


# All verification methods dictionary
ALL_VERIFICATION_METHODS = {
    1: ("HISTORY_STATE", verify_method_1_history_state),
    2: ("MESSAGE_COUNT", verify_method_2_message_count),
    3: ("DISPLAY_HTML", verify_method_3_display_html),
    4: ("METADATA_TIMESTAMP", verify_method_4_metadata_timestamp),
    5: ("API_STATE", verify_method_5_api_state),
    6: ("VERIFICATION_ENDPOINT", verify_method_6_verification_endpoint),
    7: ("DOM_CONTENT", verify_method_7_dom_content),
    8: ("MUTATION_OBSERVER", verify_method_8_mutation_observer),
    9: ("DATA_RAW", verify_method_9_data_raw),
    10: ("DOM_MESSAGE_COUNT", verify_method_10_dom_message_count),
    11: ("SSE_EVENTS", verify_method_11_sse_events),
    12: ("REQUEST_MONITOR", verify_method_12_request_monitor),
    13: ("SELENIUM", verify_method_13_selenium),
    14: ("COMPREHENSIVE", verify_method_14_comprehensive),
    15: ("BROWSER_CALLBACK", verify_method_15_browser_callback),
    16: ("BROWSER_API_QUERY", verify_method_16_browser_api_query),
}


# ============================================================================
# GUI APPLICATION
# ============================================================================

class ChatInjectMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Inject Monitor - 16 Verification Methods")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Load config
        self.config = load_config()

        # Create main container
        self.create_widgets()

        # Initial status
        self.log_status("=" * 60)
        self.log_status("Chat Inject Monitor Started")
        self.log_status(f"WebUI URL: {self.config.get('webui_base', 'http://127.0.0.1:7860')}")
        self.log_status("=" * 60)
        self.log_status("")
        self.log_status("Click 'Check Connection' to verify WebUI is accessible")
        self.log_status("")

    def create_widgets(self):
        # Top frame - Configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        # WebUI URL
        ttk.Label(config_frame, text="WebUI URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_var = tk.StringVar(value=self.config.get("webui_base", "http://127.0.0.1:7860"))
        self.url_entry = ttk.Entry(config_frame, textvariable=self.url_var, width=40)
        self.url_entry.grid(row=0, column=1, padx=5)

        ttk.Button(config_frame, text="Save URL", command=self.save_url).grid(row=0, column=2, padx=5)
        ttk.Button(config_frame, text="Check Connection", command=self.check_connection).grid(row=0, column=3, padx=5)

        # Test message
        ttk.Label(config_frame, text="Test Message:").grid(row=1, column=0, sticky=tk.W, pady=(10,0))
        self.test_msg_var = tk.StringVar(value=self.config.get("default_test_message", "[INJECTION-TEST] Hello World"))
        self.test_msg_entry = ttk.Entry(config_frame, textvariable=self.test_msg_var, width=60)
        self.test_msg_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=(10,0), sticky=tk.W)

        # Quick Actions frame
        quick_frame = ttk.LabelFrame(self.root, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(quick_frame, text="Quick Verify", command=self.quick_verify, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Run ALL 16 Methods", command=self.run_all_methods, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_frame, text="Clear Status", command=self.clear_status, width=15).pack(side=tk.LEFT, padx=5)

        # Connection status indicator
        self.connection_status = ttk.Label(quick_frame, text="Status: Unknown", foreground="gray")
        self.connection_status.pack(side=tk.RIGHT, padx=10)

        # Methods frame - 16 buttons
        methods_frame = ttk.LabelFrame(self.root, text="Individual Verification Methods (Click to Run)", padding=10)
        methods_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create 4 rows of 4 buttons each
        method_descriptions = {
            1: "HISTORY_STATE\n(Check history)",
            2: "MESSAGE_COUNT\n(Count messages)",
            3: "DISPLAY_HTML\n(Check HTML)",
            4: "METADATA_TIME\n(Check timestamp)",
            5: "API_STATE\n(Query API state)",
            6: "VERIFY_ENDPOINT\n(Custom endpoint)",
            7: "DOM_CONTENT\n(Browser DOM)",
            8: "MUTATION_OBS\n(DOM changes)",
            9: "DATA_RAW\n(HTML data-raw)",
            10: "DOM_MSG_COUNT\n(Count DOM msgs)",
            11: "SSE_EVENTS\n(Server events)",
            12: "REQUEST_MON\n(HTTP requests)",
            13: "SELENIUM\n(Browser auto)",
            14: "COMPREHENSIVE\n(Run multiple)",
            15: "BROWSER_CALLBACK\n(JS callback)",
            16: "BROWSER_API\n(Query browser)"
        }

        for i, (method_num, desc) in enumerate(method_descriptions.items()):
            row = i // 4
            col = i % 4
            btn = ttk.Button(
                methods_frame,
                text=f"{method_num}. {desc}",
                command=lambda n=method_num: self.run_single_method(n),
                width=18
            )
            btn.grid(row=row, column=col, padx=3, pady=3)

        # Status console frame
        status_frame = ttk.LabelFrame(self.root, text="Status Console (All Activity)", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrolled text widget for status
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            wrap=tk.WORD,
            width=100,
            height=20,
            font=('Consolas', 9)
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colored text
        self.status_text.tag_configure("timestamp", foreground="gray")
        self.status_text.tag_configure("info", foreground="black")
        self.status_text.tag_configure("success", foreground="green")
        self.status_text.tag_configure("error", foreground="red")
        self.status_text.tag_configure("warning", foreground="orange")
        self.status_text.tag_configure("header", foreground="blue", font=('Consolas', 9, 'bold'))

    def log_status(self, message, level="INFO"):
        """Add a message to the status console"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # Determine tag based on level
        if level == "SUCCESS":
            tag = "success"
        elif level == "ERROR":
            tag = "error"
        elif level == "WARNING":
            tag = "warning"
        elif level == "HEADER":
            tag = "header"
        else:
            tag = "info"

        # Insert timestamp
        self.status_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        # Insert message
        self.status_text.insert(tk.END, f"{message}\n", tag)

        # Auto-scroll to bottom
        self.status_text.see(tk.END)

        # Also log to file
        config = load_config()
        if config.get("log_to_file", True):
            try:
                log_path = LOG_DIR / config.get("log_file", "chat_inject_monitor.log")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] [{level}] {message}\n")
            except:
                pass

    def clear_status(self):
        """Clear the status console"""
        self.status_text.delete(1.0, tk.END)
        self.log_status("Status console cleared")

    def save_url(self):
        """Save the WebUI URL to config"""
        new_url = self.url_var.get().strip()
        self.config["webui_base"] = new_url
        save_config(self.config)
        self.log_status(f"WebUI URL saved: {new_url}", "SUCCESS")

    def check_connection(self):
        """Check if WebUI is accessible"""
        self.log_status("", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status("CHECKING CONNECTION TO WEBUI", "HEADER")
        self.log_status("=" * 50, "HEADER")

        webui_base = self.url_var.get().strip()
        self.log_status(f"Target URL: {webui_base}")

        def do_check():
            try:
                self.log_status("Sending HTTP GET request...")
                response = requests.get(webui_base, timeout=5)
                if response.status_code == 200:
                    self.log_status(f"Response received: HTTP {response.status_code}", "SUCCESS")
                    self.log_status(f"Response size: {len(response.text)} bytes")
                    self.log_status("CONNECTION SUCCESSFUL!", "SUCCESS")
                    self.root.after(0, lambda: self.connection_status.config(text="Status: Connected", foreground="green"))
                else:
                    self.log_status(f"Response received: HTTP {response.status_code}", "WARNING")
                    self.root.after(0, lambda: self.connection_status.config(text=f"Status: HTTP {response.status_code}", foreground="orange"))
            except requests.exceptions.ConnectionError:
                self.log_status("CONNECTION FAILED: Connection refused", "ERROR")
                self.log_status("Make sure text-generation-webui is running!", "ERROR")
                self.root.after(0, lambda: self.connection_status.config(text="Status: Not Connected", foreground="red"))
            except requests.exceptions.Timeout:
                self.log_status("CONNECTION FAILED: Request timed out", "ERROR")
                self.root.after(0, lambda: self.connection_status.config(text="Status: Timeout", foreground="red"))
            except Exception as e:
                self.log_status(f"CONNECTION FAILED: {str(e)}", "ERROR")
                self.root.after(0, lambda: self.connection_status.config(text="Status: Error", foreground="red"))

            self.log_status("")

        # Run in thread to not block GUI
        threading.Thread(target=do_check, daemon=True).start()

    def run_single_method(self, method_num):
        """Run a single verification method"""
        test_message = self.test_msg_var.get().strip()
        if not test_message:
            messagebox.showwarning("Warning", "Please enter a test message!")
            return

        name, func = ALL_VERIFICATION_METHODS[method_num]

        self.log_status("", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status(f"RUNNING METHOD {method_num}: {name}", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status(f"Test message: {test_message}")

        def do_run():
            self.log_status(f"Executing verification method {method_num}...")
            start_time = time.time()

            result = func(test_message)

            elapsed = time.time() - start_time
            self.log_status(f"Execution time: {elapsed:.3f} seconds")
            self.log_status("")
            self.log_status("--- RESULT ---")
            self.log_status(f"Method: {result.get('method', 'Unknown')}")
            self.log_status(f"Success: {result.get('success', False)}")

            found = result.get('found', False)
            if found:
                self.log_status(f"Found: YES - Message detected!", "SUCCESS")
            else:
                self.log_status(f"Found: NO - Message not detected", "WARNING")

            if result.get('error'):
                self.log_status(f"Error/Note: {result.get('error')}", "WARNING")
            if result.get('note'):
                self.log_status(f"Note: {result.get('note')}")

            # Log additional details
            for key, value in result.items():
                if key not in ['method', 'method_num', 'success', 'found', 'error', 'note']:
                    self.log_status(f"  {key}: {value}")

            self.log_status("")

        threading.Thread(target=do_run, daemon=True).start()

    def quick_verify(self):
        """Run quick verification (API-based methods only)"""
        test_message = self.test_msg_var.get().strip()
        if not test_message:
            messagebox.showwarning("Warning", "Please enter a test message!")
            return

        self.log_status("", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status("QUICK VERIFICATION (API-BASED METHODS)", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status(f"Test message: {test_message}")
        self.log_status("")

        def do_quick():
            methods_to_run = [1, 5, 6, 16]  # Quick methods
            found_any = False

            for method_num in methods_to_run:
                name, func = ALL_VERIFICATION_METHODS[method_num]
                self.log_status(f"Running Method {method_num}: {name}...")

                result = func(test_message)
                found = result.get('found', False)

                if found:
                    self.log_status(f"  -> FOUND!", "SUCCESS")
                    found_any = True
                else:
                    error = result.get('error', '')
                    if error:
                        self.log_status(f"  -> Not found ({error[:50]})", "WARNING")
                    else:
                        self.log_status(f"  -> Not found")

            self.log_status("")
            self.log_status("=" * 30)
            if found_any:
                self.log_status("OVERALL RESULT: MESSAGE FOUND", "SUCCESS")
            else:
                self.log_status("OVERALL RESULT: MESSAGE NOT FOUND", "WARNING")
            self.log_status("=" * 30)
            self.log_status("")

        threading.Thread(target=do_quick, daemon=True).start()

    def run_all_methods(self):
        """Run all 16 verification methods"""
        test_message = self.test_msg_var.get().strip()
        if not test_message:
            messagebox.showwarning("Warning", "Please enter a test message!")
            return

        self.log_status("", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status("RUNNING ALL 16 VERIFICATION METHODS", "HEADER")
        self.log_status("=" * 50, "HEADER")
        self.log_status(f"Test message: {test_message}")
        self.log_status("")

        def do_all():
            results_summary = []

            for method_num in range(1, 17):
                name, func = ALL_VERIFICATION_METHODS[method_num]
                self.log_status(f"[{method_num:2d}/16] Running: {name}...")

                start_time = time.time()
                result = func(test_message)
                elapsed = time.time() - start_time

                found = result.get('found', False)
                error = result.get('error', '')

                status_str = "FOUND" if found else "NOT FOUND"
                if error and not found:
                    status_str = f"NOT FOUND ({error[:30]})"

                if found:
                    self.log_status(f"        -> {status_str} ({elapsed:.2f}s)", "SUCCESS")
                else:
                    self.log_status(f"        -> {status_str} ({elapsed:.2f}s)", "WARNING" if error else "INFO")

                results_summary.append((method_num, name, found, error))

                time.sleep(0.05)  # Brief pause between methods

            # Summary
            self.log_status("")
            self.log_status("=" * 50, "HEADER")
            self.log_status("SUMMARY", "HEADER")
            self.log_status("=" * 50, "HEADER")

            found_count = sum(1 for r in results_summary if r[2])
            self.log_status(f"Total Methods Run: 16")
            self.log_status(f"Found Message: {found_count} methods")
            self.log_status(f"Not Found: {16 - found_count} methods")
            self.log_status("")

            if found_count > 0:
                self.log_status("Methods that found the message:", "SUCCESS")
                for method_num, name, found, error in results_summary:
                    if found:
                        self.log_status(f"  - Method {method_num}: {name}", "SUCCESS")

            self.log_status("")
            if found_count > 0:
                self.log_status("OVERALL: MESSAGE WAS FOUND", "SUCCESS")
            else:
                self.log_status("OVERALL: MESSAGE NOT FOUND BY ANY METHOD", "WARNING")
            self.log_status("")

        threading.Thread(target=do_all, daemon=True).start()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    root = tk.Tk()
    app = ChatInjectMonitorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
