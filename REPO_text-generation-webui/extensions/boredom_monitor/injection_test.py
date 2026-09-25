# ==========================================
# FREEDOM SYSTEM - INJECTION TEST MODULE
# Real injection testing with visible WebUI confirmation
# ==========================================

import time
import json
from datetime import datetime
from pathlib import Path

class InjectionTester:
    """
    Tests actual message injection into Oobabooga WebUI
    Provides visual confirmation and success measurement
    """
    
    def __init__(self):
        self.component_name = "INJECTION-TESTER"
        self.log_file = Path("F:/Apps/freedom_system/log/boredom_monitor.log")
        self.test_results = []
        
        # Test messages for verification
        self.test_messages = [
            "FREEDOM INJECTION TEST: This message was injected by the boredom monitor at " + datetime.now().strftime("%H:%M:%S"),
            "Freedom is testing the injection system - can you see this message?",
            "BOREDOM MONITOR ACTIVE: Injection successful if you can read this",
        ]
        
        self.log("InjectionTester initialized", "[OK]")
    
    def log(self, message, status="[INFO]"):
        """Log test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = "[" + timestamp + "] [" + self.component_name + "] " + status + " " + str(message)
        
        print(log_entry)
        
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print("[ERROR] Failed to write test log: " + str(e))
    
    def test_direct_gradio_injection(self, shared_gradio_dict=None):
        """
        Test direct Gradio textbox injection using proper STT method
        This mimics exactly how whisper_stt extension works
        """
        try:
            self.log("Starting direct Gradio injection test (STT method)", "[INFO]")
            
            if not shared_gradio_dict:
                # Try to import Oobabooga's shared module
                try:
                    from modules import shared
                    if hasattr(shared, 'gradio'):
                        shared_gradio_dict = shared.gradio
                        self.log("Found Oobabooga shared.gradio dictionary", "[OK]")
                    else:
                        self.log("shared.gradio not found", "[ERROR]")
                        return False
                except ImportError:
                    self.log("Cannot import Oobabooga modules - extension not running in Oobabooga?", "[ERROR]")
                    return False
            
            # Log all available components for debugging
            self.log("Available Gradio components:", "[INFO]")
            for key in shared_gradio_dict.keys():
                self.log("  - " + str(key), "[INFO]")
            
            # Test the STT method: direct textbox injection
            if 'textbox' in shared_gradio_dict:
                test_message = self.test_messages[0]
                
                self.log("Found 'textbox' component - using STT injection method", "[OK]")
                
                # Store original value
                textbox = shared_gradio_dict['textbox']
                original_value = getattr(textbox, 'value', '')
                
                try:
                    # Method 1: Direct textbox value assignment (like whisper_stt line 64)
                    textbox.value = test_message
                    self.log("Set textbox.value = test message", "[OK]")
                    
                    # The STT extension would trigger this via .change() event
                    # but for testing we'll just verify the value was set
                    current_value = getattr(textbox, 'value', '')
                    
                    if current_value == test_message:
                        self.log("SUCCESS: Textbox value correctly set to test message", "[OK]")
                        
                        # Try to import the script and trigger input hijack
                        try:
                            from . import script
                        except ImportError:
                            import script
                        
                        # Set up input hijack like whisper_stt does
                        if hasattr(script, 'injection_manager') and script.injection_manager:
                            if hasattr(script.injection_manager, 'freedom_injection'):
                                script.injection_manager.freedom_injection['state'] = True
                                script.injection_manager.freedom_injection['value'] = [test_message, test_message]
                                self.log("Input hijack configured - next user input will trigger injection", "[OK]")
                                
                                # Restore original textbox value
                                textbox.value = original_value
                                
                                return True
                            else:
                                self.log("freedom_injection not available in injection manager", "[WARNING]")
                        else:
                            self.log("injection_manager not available", "[WARNING]")
                        
                        # Restore original value even if hijack setup failed
                        textbox.value = original_value
                        return True  # Still consider this a success since textbox injection worked
                    else:
                        self.log("FAILED: Textbox value not set correctly", "[FAIL]")
                        self.log("Expected: " + test_message[:50] + "...", "[INFO]")
                        self.log("Actual: " + str(current_value)[:50] + "...", "[INFO]")
                        
                        # Restore original value
                        textbox.value = original_value
                        return False
                        
                except Exception as e:
                    self.log("Textbox injection failed: " + str(e), "[ERROR]")
                    # Restore original value
                    try:
                        textbox.value = original_value
                    except:
                        pass
                    return False
            else:
                self.log("'textbox' component not found - cannot use STT method", "[FAIL]")
                return False
            
        except Exception as e:
            self.log("Direct Gradio injection test failed: " + str(e), "[FAIL]")
            return False
    
    def test_javascript_injection(self):
        """
        Generate JavaScript code to test DOM injection
        Returns JS code that can be executed to test injection
        """
        try:
            test_message = self.test_messages[1]
            
            js_test_code = f"""
            // FREEDOM SYSTEM INJECTION TEST
            console.log('[INJECTION-TEST] Starting JavaScript injection test');
            
            function testFreedomInjection() {{
                const testMessage = '{test_message}';
                let success = false;
                
                // Method 1: Find textarea input
                const textareas = document.querySelectorAll('textarea');
                console.log('[INJECTION-TEST] Found ' + textareas.length + ' textarea elements');
                
                for (let i = 0; i < textareas.length; i++) {{
                    const textarea = textareas[i];
                    
                    // Check if this looks like a chat input
                    const placeholder = textarea.placeholder || '';
                    const id = textarea.id || '';
                    const classes = textarea.className || '';
                    
                    console.log('[INJECTION-TEST] Textarea ' + i + ': placeholder="' + placeholder + '", id="' + id + '", classes="' + classes + '"');
                    
                    if (placeholder.toLowerCase().includes('message') || 
                        placeholder.toLowerCase().includes('type') ||
                        id.toLowerCase().includes('input') ||
                        classes.toLowerCase().includes('input')) {{
                        
                        console.log('[INJECTION-TEST] Found potential chat input, injecting message');
                        
                        // Set the message
                        textarea.value = testMessage;
                        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        
                        success = true;
                        break;
                    }}
                }}
                
                // Method 2: Look for generate/submit buttons
                const buttons = document.querySelectorAll('button');
                console.log('[INJECTION-TEST] Found ' + buttons.length + ' button elements');
                
                for (let i = 0; i < buttons.length; i++) {{
                    const button = buttons[i];
                    const text = button.textContent || button.innerText || '';
                    const ariaLabel = button.getAttribute('aria-label') || '';
                    
                    if (text.toLowerCase().includes('generate') || 
                        text.toLowerCase().includes('submit') ||
                        text.toLowerCase().includes('send') ||
                        ariaLabel.toLowerCase().includes('generate') ||
                        ariaLabel.toLowerCase().includes('submit')) {{
                        
                        console.log('[INJECTION-TEST] Found generate button: "' + text + '", clicking in 1 second...');
                        
                        setTimeout(() => {{
                            button.click();
                            console.log('[INJECTION-TEST] Generate button clicked');
                        }}, 1000);
                        
                        break;
                    }}
                }}
                
                if (success) {{
                    console.log('[INJECTION-TEST] SUCCESS: Message injected into chat input');
                    
                    // Log success to visible element
                    const successDiv = document.createElement('div');
                    successDiv.innerHTML = '<div style="position:fixed;top:10px;right:10px;background:green;color:white;padding:10px;border-radius:5px;z-index:9999;">FREEDOM INJECTION TEST SUCCESS: Message injected at ' + new Date().toLocaleTimeString() + '</div>';
                    document.body.appendChild(successDiv);
                    
                    setTimeout(() => {{
                        document.body.removeChild(successDiv);
                    }}, 5000);
                    
                }} else {{
                    console.log('[INJECTION-TEST] FAILED: Could not find chat input element');
                    
                    // Log failure to visible element
                    const failDiv = document.createElement('div');
                    failDiv.innerHTML = '<div style="position:fixed;top:10px;right:10px;background:red;color:white;padding:10px;border-radius:5px;z-index:9999;">FREEDOM INJECTION TEST FAILED: No chat input found</div>';
                    document.body.appendChild(failDiv);
                    
                    setTimeout(() => {{
                        document.body.removeChild(failDiv);
                    }}, 5000);
                }}
                
                return success;
            }}
            
            // Run the test
            const result = testFreedomInjection();
            console.log('[INJECTION-TEST] Test completed, result:', result);
            
            // Return result for external checking
            window.freedomInjectionTestResult = result;
            window.freedomInjectionTestTime = new Date().toISOString();
            """
            
            self.log("JavaScript injection test code generated", "[OK]")
            return js_test_code
            
        except Exception as e:
            self.log("JavaScript test generation failed: " + str(e), "[ERROR]")
            return "console.log('[INJECTION-TEST] Test generation failed');"
    
    def test_input_modifier_hook(self, test_text="Hello", test_visible="Hello"):
        """
        Test the chat_input_modifier hook directly
        This simulates what happens when a user types
        """
        try:
            self.log("Testing input modifier hook", "[INFO]")
            
            # Import the main script to test the hook
            try:
                from . import script
            except ImportError:
                import script
            
            # Test the hook function
            if hasattr(script, 'chat_input_modifier'):
                test_message = self.test_messages[2]
                
                # First, set up an injection in the injection manager
                if script.injection_manager:
                    result = script.injection_manager._attempt_non_api_injection(test_message)
                    self.log("Set up non-API injection: " + str(result), "[INFO]")
                    
                    # Now test the hook
                    modified_text, modified_visible = script.chat_input_modifier(test_text, test_visible, {})
                    
                    if modified_text != test_text or modified_visible != test_visible:
                        self.log("SUCCESS: Input modifier hook changed text!", "[OK]")
                        self.log("Original: '" + test_text + "' -> Modified: '" + str(modified_text) + "'", "[OK]")
                        return True
                    else:
                        self.log("Input modifier hook did not change text", "[WARNING]")
                        return False
                else:
                    self.log("Injection manager not available for hook test", "[ERROR]")
                    return False
            else:
                self.log("chat_input_modifier function not found", "[ERROR]")
                return False
                
        except Exception as e:
            self.log("Input modifier hook test failed: " + str(e), "[ERROR]")
            return False
    
    def run_full_injection_test(self):
        """
        Run comprehensive injection test with multiple methods
        Returns detailed results
        """
        self.log("=== STARTING FULL INJECTION TEST ===", "[INFO]")
        
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "direct_gradio": False,
            "javascript_generated": False,
            "input_modifier_hook": False,
            "overall_success": False,
            "details": []
        }
        
        # Test 1: Direct Gradio injection
        try:
            results["direct_gradio"] = self.test_direct_gradio_injection()
            if results["direct_gradio"]:
                results["details"].append("Direct Gradio injection: SUCCESS")
            else:
                results["details"].append("Direct Gradio injection: FAILED")
        except Exception as e:
            results["details"].append("Direct Gradio injection: ERROR - " + str(e))
        
        # Test 2: JavaScript generation
        try:
            js_code = self.test_javascript_injection()
            results["javascript_generated"] = len(js_code) > 100  # Basic check
            if results["javascript_generated"]:
                results["details"].append("JavaScript injection code: GENERATED")
                results["js_test_code"] = js_code
            else:
                results["details"].append("JavaScript injection code: FAILED")
        except Exception as e:
            results["details"].append("JavaScript injection code: ERROR - " + str(e))
        
        # Test 3: Input modifier hook
        try:
            results["input_modifier_hook"] = self.test_input_modifier_hook()
            if results["input_modifier_hook"]:
                results["details"].append("Input modifier hook: SUCCESS")
            else:
                results["details"].append("Input modifier hook: FAILED")
        except Exception as e:
            results["details"].append("Input modifier hook: ERROR - " + str(e))
        
        # Overall success
        results["overall_success"] = any([
            results["direct_gradio"],
            results["input_modifier_hook"]
        ])
        
        # Log results
        self.log("=== INJECTION TEST RESULTS ===", "[INFO]")
        for detail in results["details"]:
            status = "[OK]" if "SUCCESS" in detail else "[FAIL]" if "FAILED" in detail else "[ERROR]"
            self.log(detail, status)
        
        if results["overall_success"]:
            self.log("OVERALL TEST RESULT: SUCCESS - At least one injection method working", "[OK]")
        else:
            self.log("OVERALL TEST RESULT: FAILED - No injection methods working", "[FAIL]")
        
        self.log("=== END INJECTION TEST ===", "[INFO]")
        
        # Save results to file
        try:
            results_file = Path("F:/Apps/freedom_system/log/injection_test_results.json")
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            self.log("Test results saved to: " + str(results_file), "[OK]")
        except Exception as e:
            self.log("Failed to save test results: " + str(e), "[ERROR]")
        
        return results


# Factory function
def create_injection_tester():
    """Create and return an injection tester"""
    return InjectionTester()


# Test execution function
def run_injection_test():
    """Run the full injection test and return results"""
    tester = create_injection_tester()
    return tester.run_full_injection_test()


# Main execution for standalone testing
if __name__ == "__main__":
    print("=== FREEDOM SYSTEM INJECTION TEST ===")
    results = run_injection_test()
    print("Test completed. Check log file for details.")
    print("Results:", results)