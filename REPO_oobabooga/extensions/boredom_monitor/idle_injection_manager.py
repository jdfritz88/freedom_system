# ==========================================
# FREEDOM SYSTEM - IDLE INJECTION MANAGER
# Follows Freedom_Installer_Coding_Standards.txt
# Follows oobabooga_extension_standards.md
# ==========================================

# Standard #9: Script Loader Override - Load from shared _env
import sys
import os
from pathlib import Path

# Auto-repair environment paths if missing
try:
    # Try to find the Oobabooga Python environment - Fixed for actual Oobabooga structure
    current_dir = Path(__file__).parent
    # Go from extensions/boredom_monitor to oobabooga root
    oobabooga_root = current_dir.parent.parent  
    env_candidates = [
        oobabooga_root / "installer_files" / "env" / "Lib" / "site-packages",  # Primary: oobabooga/installer_files/env
        oobabooga_root / "installer_files" / "conda" / "Lib" / "site-packages",  # Secondary: conda environment
        Path("F:/Apps/freedom_system/componentsave/apps_installed/oobabooga/installer_files/env/Lib/site-packages"),  # Absolute primary
        Path("F:/Apps/freedom_system/componentsave/apps_installed/oobabooga/installer_files/conda/Lib/site-packages"),  # Absolute secondary
        oobabooga_root / "_env" / "Lib" / "site-packages",  # Legacy: oobabooga/_env/Lib/site-packages
        current_dir / "_env" / "Lib" / "site-packages"  # Extension-relative fallback
    ]
    
    env_path = None
    for candidate in env_candidates:
        if candidate.exists():
            env_path = str(candidate)
            break
    
    if env_path and env_path not in sys.path:
        sys.path.insert(0, env_path)
        print("SUCCESS: Environment path loaded: " + env_path)
    elif not env_path:
        print("WARNING: Shared _env folder not found, using system Python")
        
except Exception as e:
    print("ERROR: Environment path setup failed: " + str(e))

# Standard imports after environment setup
import json
import time
from datetime import datetime

class IdleInjectionManager:
    """
    Manages dual injection methods for the Freedom System boredom monitor
    Implements both input hijacking and JavaScript injection as per boredom_monitor_analysis.md
    
    Follows Standards:
    - #1: Folder Isolation - Lives in boredom_monitor extension folder
    - #2: Environment Usage - Uses shared _env folder
    - #9: Script Loader Override - Overrides Python paths for _env
    - #11: Log Placement - Logs to root log folder
    - #12: Log Format - Includes timestamps, component names, status indicators
    """
    
    def __init__(self, config_path=None):
        self.component_name = "INJECTION-MANAGER"
        
        # Standard #11: Log Placement - Use root log folder
        self.log_file = Path("F:/Apps/freedom_system/log/boredom_monitor.log")
        
        # Configuration - Fixed to use extension directory
        extension_dir = Path(__file__).parent
        self.config_path = config_path or (extension_dir / "idle_response_config.json")
        self.config = self._load_config()
        
        # Injection state management
        self.freedom_injection = {
            'state': False,
            'value': ["", ""],
            'use_api': False
        }
        
        # Method preferences (API vs non-API)
        self.prefer_api_injection = self.config.get("prefer_api_injection", False)
        self.api_injection_enabled = self.config.get("api_injection_enabled", True)
        self.non_api_injection_enabled = self.config.get("non_api_injection_enabled", True)
        
        # Statistics
        self.injection_count = 0
        self.api_injection_count = 0
        self.non_api_injection_count = 0
        self.last_injection_time = 0
        
        # Bridge connector integration
        self.bridge_connector = None
        self.initialization_success = False
        
        try:
            # Try to import and initialize bridge connector
            self._initialize_bridge_connector()
            self.initialization_success = True
            self.log("IdleInjectionManager initialized successfully", "[OK]")
            
        except Exception as e:
            self.log("IdleInjectionManager initialization failed: " + str(e), "[FAIL]")
    
    def log(self, message, status="[INFO]"):
        """
        Standard #12: Log Format - Include timestamp, component name, action result
        Logs to both console and root log folder
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = "[" + timestamp + "] [" + self.component_name + "] " + status + " " + str(message)
        
        # Console output
        print(log_entry)
        
        # File logging to root log folder
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print("[" + timestamp + "] [" + self.component_name + "] [ERROR] Failed to write log: " + str(e))
    
    def _load_config(self):
        """Load injection configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.log("Injection configuration loaded from " + str(config_file), "[OK]")
                return config
            else:
                # Default configuration
                default_config = {
                    "prefer_api_injection": False,
                    "api_injection_enabled": True,
                    "non_api_injection_enabled": True,
                    "injection_cooldown_seconds": 2
                }
                self.log("Using default injection configuration", "[INFO]")
                return default_config
                
        except Exception as e:
            self.log("Failed to load injection config: " + str(e), "[ERROR]")
            return {}
    
    def _initialize_bridge_connector(self):
        """Initialize the bridge connector system"""
        try:
            # Try to import the existing bridge connector
            from .idle_gradio_bridge_connector import get_idle_bridge_connector
            
            self.bridge_connector = get_idle_bridge_connector()
            self.log("Bridge connector initialized successfully", "[OK]")
            
        except ImportError:
            try:
                # Try without relative import
                from idle_gradio_bridge_connector import get_idle_bridge_connector
                
                self.bridge_connector = get_idle_bridge_connector()
                self.log("Bridge connector initialized successfully (fallback import)", "[OK]")
                
            except ImportError:
                self.log("Bridge connector not available - will use JavaScript fallback only", "[WARNING]")
                self.bridge_connector = None
        
        except Exception as e:
            self.log("Bridge connector initialization failed: " + str(e), "[ERROR]")
            self.bridge_connector = None
    
    def inject_freedom_message(self, message, use_api=None):
        """
        Main injection function - routes to appropriate method based on configuration
        
        Args:
            message: The message to inject
            use_api: Override for API preference (True/False/None for auto-select)
        
        Returns:
            dict: Result with success status and method used
        """
        try:
            # Determine injection method
            if use_api is None:
                use_api = self.prefer_api_injection
            
            # Cooldown check
            current_time = time.time()
            cooldown_seconds = self.config.get("injection_cooldown_seconds", 2)
            
            if current_time - self.last_injection_time < cooldown_seconds:
                remaining = cooldown_seconds - (current_time - self.last_injection_time)
                self.log("Injection on cooldown for " + str(round(remaining, 1)) + " more seconds", "[WARNING]")
                return {
                    'success': False,
                    'method': 'none',
                    'reason': 'cooldown',
                    'remaining_seconds': remaining
                }
            
            # Attempt injection based on preference
            if use_api and self.api_injection_enabled:
                result = self._attempt_api_injection(message)
                if result['success']:
                    self._record_successful_injection('api')
                    return result
                elif self.non_api_injection_enabled:
                    self.log("API injection failed, falling back to non-API method", "[WARNING]")
                    result = self._attempt_non_api_injection(message)
                    if result['success']:
                        self._record_successful_injection('non-api')
                    return result
                else:
                    return result
            
            elif self.non_api_injection_enabled:
                result = self._attempt_non_api_injection(message)
                if result['success']:
                    self._record_successful_injection('non-api')
                    return result
                elif self.api_injection_enabled:
                    self.log("Non-API injection failed, falling back to API method", "[WARNING]")
                    result = self._attempt_api_injection(message)
                    if result['success']:
                        self._record_successful_injection('api')
                    return result
                else:
                    return result
            
            else:
                self.log("All injection methods disabled", "[ERROR]")
                return {
                    'success': False,
                    'method': 'none',
                    'reason': 'all_methods_disabled'
                }
                
        except Exception as e:
            self.log("Injection manager failed: " + str(e), "[FAIL]")
            return {
                'success': False,
                'method': 'error',
                'reason': str(e)
            }
    
    def _attempt_api_injection(self, message):
        """
        Attempt API injection via bridge connector
        """
        try:
            if not self.bridge_connector:
                return {
                    'success': False,
                    'method': 'api',
                    'reason': 'bridge_not_available'
                }
            
            self.log("Attempting API injection via bridge connector", "[INFO]")
            
            # Use the bridge connector for API injection
            success = self.bridge_connector.inject_idle_message(message)
            
            if success:
                self.log("API injection successful", "[OK]")
                return {
                    'success': True,
                    'method': 'api',
                    'message': message
                }
            else:
                self.log("API injection failed via bridge", "[ERROR]")
                return {
                    'success': False,
                    'method': 'api',
                    'reason': 'bridge_injection_failed'
                }
                
        except Exception as e:
            self.log("API injection exception: " + str(e), "[ERROR]")
            return {
                'success': False,
                'method': 'api',
                'reason': str(e)
            }
    
    def _attempt_non_api_injection(self, message):
        """
        Attempt non-API injection via input hijacking
        This sets up the injection state for the chat_input_modifier to use
        """
        try:
            self.log("Attempting non-API injection via input hijacking", "[INFO]")
            
            # Set up injection state
            self.freedom_injection['state'] = True
            self.freedom_injection['value'] = [message, message]
            self.freedom_injection['use_api'] = False
            
            self.log("Non-API injection queued for next user input", "[OK]")
            return {
                'success': True,
                'method': 'non-api',
                'message': message,
                'note': 'queued_for_next_user_input'
            }
            
        except Exception as e:
            self.log("Non-API injection exception: " + str(e), "[ERROR]")
            return {
                'success': False,
                'method': 'non-api',
                'reason': str(e)
            }
    
    def _record_successful_injection(self, method):
        """Record successful injection statistics"""
        self.injection_count += 1
        self.last_injection_time = time.time()
        
        if method == 'api':
            self.api_injection_count += 1
        elif method == 'non-api':
            self.non_api_injection_count += 1
        
        self.log("Injection recorded: Total=" + str(self.injection_count) + 
                ", API=" + str(self.api_injection_count) + 
                ", Non-API=" + str(self.non_api_injection_count), "[OK]")
    
    def chat_input_modifier_hook(self, text, visible_text, state):
        """
        Hook function for Oobabooga's chat_input_modifier
        This implements the input hijacking method from the analysis
        
        Should be called from script.py's chat_input_modifier function
        """
        try:
            if self.freedom_injection['state'] and not self.freedom_injection['use_api']:
                # Non-API injection: Hijack user input
                self.freedom_injection['state'] = False
                injected_message = self.freedom_injection['value']
                
                self.log("Non-API injection executed via input hijacking", "[OK]")
                return injected_message
            else:
                # Normal user activity - log for boredom detection
                self.log("User activity detected", "[INFO]")
                return text, visible_text
                
        except Exception as e:
            self.log("Input modifier hook failed: " + str(e), "[ERROR]")
            return text, visible_text
    
    def generate_javascript_injection_code(self, message, use_api=False):
        """
        Generate JavaScript code for client-side injection
        This implements the JavaScript DOM manipulation method from the analysis
        """
        try:
            # Escape the message for JavaScript
            escaped_message = message.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
            
            js_code = """
            setTimeout(() => {
                try {
                    const message = \"""" + escaped_message + """\";
                    const useApi = """ + str(use_api).lower() + """;
                    
                    if (useApi) {
                        // API injection method
                        fetch('/api/v1/chat/completions', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                messages: [{ role: 'user', content: message }],
                                max_tokens: 150,
                                temperature: 0.8
                            })
                        }).then(response => {
                            console.log('[BOREDOM-MONITOR] API injection response:', response.status);
                        }).catch(error => {
                            console.log('[BOREDOM-MONITOR] API injection error:', error);
                        });
                    } else {
                        // Direct DOM injection method
                        const chatInput = document.querySelector('textarea[placeholder*="message"], textarea[data-testid="textbox"]');
                        if (chatInput) {
                            chatInput.value = message;
                            chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                            
                            // Auto-trigger submit button
                            const submitBtn = document.querySelector('button[aria-label*="Submit"], button:contains("Generate")');
                            if (submitBtn) {
                                setTimeout(() => submitBtn.click(), 100);
                            }
                            console.log('[BOREDOM-MONITOR] DOM injection executed successfully');
                        } else {
                            console.log('[BOREDOM-MONITOR] DOM injection failed - elements not found');
                        }
                    }
                } catch (error) {
                    console.log('[BOREDOM-MONITOR] JavaScript injection error:', error);
                }
            }, 500);
            """
            
            self.log("JavaScript injection code generated", "[OK]")
            return js_code
            
        except Exception as e:
            self.log("JavaScript code generation failed: " + str(e), "[ERROR]")
            return "console.log('[BOREDOM-MONITOR] JavaScript injection failed');"
    
    def get_injection_status(self):
        """Get current injection system status"""
        try:
            bridge_status = {}
            if self.bridge_connector:
                bridge_status = self.bridge_connector.get_bridge_status()
            
            status = {
                "initialization_success": self.initialization_success,
                "bridge_available": self.bridge_connector is not None,
                "api_injection_enabled": self.api_injection_enabled,
                "non_api_injection_enabled": self.non_api_injection_enabled,
                "prefer_api_injection": self.prefer_api_injection,
                "injection_count": self.injection_count,
                "api_injection_count": self.api_injection_count,
                "non_api_injection_count": self.non_api_injection_count,
                "last_injection_time": self.last_injection_time,
                "injection_queued": self.freedom_injection['state'],
                "bridge_status": bridge_status
            }
            
            self.log("Injection status retrieved successfully", "[OK]")
            return status
            
        except Exception as e:
            self.log("Failed to get injection status: " + str(e), "[ERROR]")
            return {
                "initialization_success": False,
                "error": str(e)
            }
    
    def test_api_injection(self, test_message="This is a test API injection from the boredom monitor."):
        """Test API injection method"""
        try:
            self.log("Testing API injection method", "[INFO]")
            result = self._attempt_api_injection(test_message)
            
            if result['success']:
                self.log("API injection test successful", "[OK]")
            else:
                self.log("API injection test failed: " + result.get('reason', 'unknown'), "[FAIL]")
            
            return result
            
        except Exception as e:
            self.log("API injection test exception: " + str(e), "[ERROR]")
            return {'success': False, 'method': 'api', 'reason': str(e)}
    
    def test_non_api_injection(self, test_message="This is a test non-API injection from the boredom monitor."):
        """Test non-API injection method"""
        try:
            self.log("Testing non-API injection method", "[INFO]")
            result = self._attempt_non_api_injection(test_message)
            
            if result['success']:
                self.log("Non-API injection test successful (queued)", "[OK]")
            else:
                self.log("Non-API injection test failed: " + result.get('reason', 'unknown'), "[FAIL]")
            
            return result
            
        except Exception as e:
            self.log("Non-API injection test exception: " + str(e), "[ERROR]")
            return {'success': False, 'method': 'non-api', 'reason': str(e)}
    
    def toggle_api_preference(self):
        """Toggle between API and non-API injection preference"""
        try:
            self.prefer_api_injection = not self.prefer_api_injection
            self.log("API injection preference toggled to: " + str(self.prefer_api_injection), "[OK]")
            return self.prefer_api_injection
            
        except Exception as e:
            self.log("Failed to toggle API preference: " + str(e), "[ERROR]")
            return self.prefer_api_injection


# Factory function for easy usage
def create_injection_manager():
    """Create and return a configured injection manager"""
    try:
        manager = IdleInjectionManager()
        if manager.initialization_success:
            print("[INJECTION-MANAGER] [OK] Factory function completed successfully")
            return manager
        else:
            print("[INJECTION-MANAGER] [FAIL] Factory function failed during initialization")
            return None
            
    except Exception as e:
        print("[INJECTION-MANAGER] [FAIL] Factory function exception: " + str(e))
        return None


# Testing functions for diagnostics
def test_injection_methods():
    """Test both injection methods"""
    print("=== INJECTION MANAGER TEST ===")
    
    manager = create_injection_manager()
    if not manager:
        print("[FAIL] Could not create injection manager")
        return False
    
    try:
        # Test API injection
        print("Testing API injection...")
        api_result = manager.test_api_injection()
        print("API Result:", api_result)
        
        # Test non-API injection
        print("Testing non-API injection...")
        non_api_result = manager.test_non_api_injection()
        print("Non-API Result:", non_api_result)
        
        # Show status
        status = manager.get_injection_status()
        print("Status:", status)
        
        print("[OK] Injection methods test completed")
        return True
        
    except Exception as e:
        print("[FAIL] Injection methods test failed: " + str(e))
        return False


# Main execution for testing
if __name__ == "__main__":
    print("=== IDLE INJECTION MANAGER DIAGNOSTICS ===")
    
    # Run initialization test
    manager = create_injection_manager()
    if manager:
        print("[OK] Initialization successful")
        
        # Run tests
        test_injection_methods()
        
        print("[DONE] All diagnostics completed")
    else:
        print("[FAIL] Initialization failed")
        print("[FAIL] Diagnostics could not run")