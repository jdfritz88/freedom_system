# ==========================================
# FREEDOM SYSTEM - IDLE GRADIO BRIDGE CONNECTOR
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

import os
import time
import threading
from pathlib import Path

# Import the bridge system
try:
    from .idle_gradio_chat_bridge import create_idle_chat_bridge
    bridge_available = True
except ImportError:
    try:
        from idle_gradio_chat_bridge import create_idle_chat_bridge
        bridge_available = True
    except ImportError:
        bridge_available = False
        print("ERROR: Could not import idle_gradio_chat_bridge")

class IdleBridgeConnector:
    """
    Connector that integrates the chat bridge with the existing boredom monitor
    """
    
    def __init__(self):
        self.bridge = None
        self.connector = None
        self.is_initialized = False
        self.setup_attempted = False
        
        # Configuration - Enhanced with timing fixes
        self.max_setup_attempts = 5
        self.setup_retry_delay = 2  # seconds
        self.delayed_retry_interval = 10  # seconds for background retries
        
        # Background initialization
        self.background_init_thread = None
        self.shutdown_background = False
        
        print("SUCCESS: IdleBridgeConnector initialized")
        
        # Start background initialization thread
        self._start_background_initialization()
    
    def log(self, message):
        """Simple logging function"""
        print("[BRIDGE-CONNECTOR] " + str(message))
    
    def _start_background_initialization(self):
        """Start background thread to initialize bridge when UI is ready"""
        if self.background_init_thread is None:
            self.background_init_thread = threading.Thread(
                target=self._background_initialization_worker,
                daemon=True,
                name="BridgeInitializer"
            )
            self.background_init_thread.start()
            self.log("Background initialization thread started")
    
    def _background_initialization_worker(self):
        """Background worker that waits for UI components to be available"""
        self.log("Background initialization worker started")
        
        while not self.shutdown_background and not self.is_initialized:
            try:
                # Check if Oobabooga components are now available
                from modules import shared
                
                if hasattr(shared, 'gradio') and len(shared.gradio) > 0:
                    self.log("UI components detected (" + str(len(shared.gradio)) + " components)")
                    
                    # Try to initialize now that components exist
                    if self.initialize_bridge():
                        self.log("Background initialization successful!")
                        break
                    else:
                        self.log("Background initialization failed, will retry")
                else:
                    self.log("UI components not ready yet (gradio dict size: " + str(len(shared.gradio) if hasattr(shared, 'gradio') else 0) + ")")
                
                # Wait before next check
                time.sleep(self.delayed_retry_interval)
                
            except Exception as e:
                self.log("Background initialization error: " + str(e))
                time.sleep(self.delayed_retry_interval)
        
        if not self.shutdown_background:
            self.log("Background initialization worker finished")
        else:
            self.log("Background initialization worker shutdown")
    
    def initialize_bridge(self):
        """
        Initialize the chat bridge system
        """
        if not bridge_available:
            self.log("ERROR: Bridge system not available")
            return False
        
        if self.is_initialized:
            self.log("Bridge already initialized")
            return True
        
        try:
            # Create bridge and connector
            self.bridge, self.connector = create_idle_chat_bridge()
            self.log("Bridge system created successfully")
            
            # Try to set up Oobabooga integration
            if self._attempt_oobabooga_setup():
                self.is_initialized = True
                self.log("Bridge initialization complete")
                return True
            else:
                self.log("Bridge created but Oobabooga setup pending")
                return False
                
        except Exception as e:
            self.log("ERROR: Bridge initialization failed: " + str(e))
            return False
    
    def _attempt_oobabooga_setup(self):
        """
        Attempt to set up Oobabooga integration with retries
        """
        if self.setup_attempted:
            return self.is_initialized
        
        self.setup_attempted = True
        
        for attempt in range(self.max_setup_attempts):
            try:
                self.log("Attempting Oobabooga setup (attempt " + str(attempt + 1) + ")")
                
                # Try to import Oobabooga modules
                try:
                    from modules import shared
                    from modules.text_generation import generate_reply
                    oobabooga_available = True
                    self.log("Oobabooga modules found")
                except ImportError:
                    oobabooga_available = False
                    self.log("Oobabooga modules not yet available")
                
                if oobabooga_available:
                    # Try to set up the bridge
                    success = self.connector.setup_oobabooga_bridge(generate_reply)
                    
                    if success:
                        self.log("Oobabooga bridge setup successful")
                        return True
                    else:
                        self.log("Bridge setup failed, will retry")
                
                # Wait before retry
                if attempt < self.max_setup_attempts - 1:
                    time.sleep(self.setup_retry_delay)
                
            except Exception as e:
                self.log("Setup attempt failed: " + str(e))
                if attempt < self.max_setup_attempts - 1:
                    time.sleep(self.setup_retry_delay)
        
        self.log("All setup attempts failed - bridge available but not connected")
        return False
    
    def retry_setup(self):
        """
        Manually retry Oobabooga setup
        """
        self.setup_attempted = False
        return self._attempt_oobabooga_setup()
    
    def inject_idle_message(self, message: str):
        """
        Main function to inject an idle message into chat
        This is what the boredom monitor will call
        """
        # METHOD 1: Try bridge system if initialized
        if self.is_initialized:
            try:
                self.bridge.inject_user_message(message)
                self.log("Message injection queued via bridge successfully")
                return True
            except Exception as e:
                self.log("ERROR: Bridge injection failed: " + str(e))
                # Fall through to fallback method
        
        # METHOD 2: Use direct injection method (WORKING FROM PREVIOUS IMPLEMENTATION)  
        try:
            self.log("Using fallback direct injection method")
            return self._inject_message_properly(message)
            
        except Exception as e:
            self.log("ERROR: Fallback injection failed: " + str(e))
            return False
    
    def _inject_message_properly(self, message):
        """
        WORKING AUTO-INJECTION: Uses Oobabooga's extension hook system
        This is the CORRECT way - works with Gradio's event system, not against it
        """
        try:
            from modules import shared
            
            # METHOD 1: Inject into textbox component (proper chat input)
            if hasattr(shared, 'gradio') and 'textbox' in shared.gradio:
                textbox_component = shared.gradio['textbox']
                
                # Set the message in the textbox
                textbox_component.value = {"text": message, "files": []}
                
                # Also update the Chat input state if it exists
                if 'Chat input' in shared.gradio:
                    shared.gradio['Chat input'].value = message
                
                self.log("Message injected into chat textbox")
                return True
            
            # METHOD 2: Direct chat history manipulation (fallback)
            elif hasattr(shared, 'gradio') and 'history' in shared.gradio:
                history_component = shared.gradio['history']
                current_history = history_component.value
                
                # Add our message to both internal and visible history
                new_entry = [message, '']  # [user_message, ai_response]
                current_history['internal'].append(new_entry)
                current_history['visible'].append(new_entry)
                
                # Update the component
                history_component.value = current_history
                
                self.log("Message injected via direct history manipulation (fallback)")
                return True
            
            # METHOD 2: Try HTML display update
            elif hasattr(shared, 'gradio') and 'html_display' in shared.gradio:
                # This would need more complex HTML generation
                self.log("HTML display injection not yet implemented")
                return False
                
            else:
                self.log("ERROR: No suitable injection method available")
                return False
                
        except Exception as e:
            self.log("ERROR: Direct injection failed: " + str(e))
            return False
    
    def inject_system_prompt(self, prompt: str):
        """
        Inject a system prompt (same as user message but clearer naming)
        """
        return self.inject_idle_message(prompt)
    
    def get_bridge_status(self):
        """
        Get detailed status of the bridge system
        """
        if not self.bridge:
            return {
                'available': bridge_available,
                'initialized': False,
                'error': 'Bridge not created'
            }
        
        bridge_status = self.bridge.get_status()
        
        return {
            'available': bridge_available,
            'initialized': self.is_initialized,
            'setup_attempted': self.setup_attempted,
            'bridge_active': bridge_status.get('active', False),
            'queue_size': bridge_status.get('queue_size', 0),
            'injection_count': bridge_status.get('injection_count', 0),
            'components_registered': bridge_status.get('components_registered', 0),
            'handlers_registered': bridge_status.get('handlers_registered', 0)
        }
    
    def get_component_info(self):
        """
        Get information about discovered Gradio components
        """
        if not self.connector:
            return {}
        
        return self.connector.get_component_info()
    
    def manual_setup_components(self, **components):
        """
        Manually register components if auto-discovery fails
        
        Usage:
        connector.manual_setup_components(
            textbox=textbox_component,
            chatbot=chatbot_component,
            submit_btn=submit_button
        )
        """
        if not self.connector:
            self.log("ERROR: Connector not available")
            return False
        
        try:
            success = self.connector.manual_register_components(**components)
            if success:
                self.is_initialized = True
                self.log("Manual component setup successful")
            return success
            
        except Exception as e:
            self.log("ERROR: Manual setup failed: " + str(e))
            return False
    
    def shutdown(self):
        """
        Shutdown the bridge system
        """
        # Stop background initialization
        self.shutdown_background = True
        if self.background_init_thread and self.background_init_thread.is_alive():
            self.log("Stopping background initialization thread")
            # Give it some time to finish
            self.background_init_thread.join(timeout=2)
        
        # Stop bridge
        if self.bridge:
            self.bridge.stop_bridge()
            self.log("Bridge shutdown complete")


# Global instance for easy access from boredom monitor
_global_bridge_connector = None

def get_idle_bridge_connector():
    """
    Get or create the global bridge connector instance
    """
    global _global_bridge_connector
    
    if _global_bridge_connector is None:
        _global_bridge_connector = IdleBridgeConnector()
    
    return _global_bridge_connector

def inject_idle_message_via_bridge(message: str):
    """
    Convenience function for the boredom monitor to inject messages
    This is the main function that script.py will call
    """
    connector = get_idle_bridge_connector()
    return connector.inject_idle_message(message)

def get_bridge_status():
    """
    Convenience function to get bridge status
    """
    connector = get_idle_bridge_connector()
    return connector.get_bridge_status()

def initialize_bridge_system():
    """
    Initialize the bridge system - call this from script.py setup()
    This now just ensures the background initialization is running
    """
    connector = get_idle_bridge_connector()
    # The background thread is already started in __init__
    # Just return True since we're handling initialization in background
    return True

def retry_bridge_setup():
    """
    Retry bridge setup - useful if initial setup failed
    """
    connector = get_idle_bridge_connector()
    return connector.retry_setup()

# Diagnostic function for troubleshooting
def diagnose_bridge_system():
    """
    Run diagnostics on the bridge system
    """
    print("=== BRIDGE SYSTEM DIAGNOSTICS ===")
    
    # Check if bridge module is available
    print("Bridge module available: " + str(bridge_available))
    
    if not bridge_available:
        print("ERROR: Bridge module not found")
        print("Make sure idle_gradio_chat_bridge.py is in the same directory")
        return
    
    # Check connector status
    connector = get_idle_bridge_connector()
    status = connector.get_bridge_status()
    
    print("Bridge Status:")
    for key, value in status.items():
        print("  " + str(key) + ": " + str(value))
    
    # Check component info
    component_info = connector.get_component_info()
    if component_info:
        print("Component Info:")
        for name, info in component_info.items():
            print("  " + str(name) + ": " + str(info))
    else:
        print("No components discovered yet")
    
    # Check Oobabooga modules
    try:
        from modules import shared
        print("Oobabooga 'shared' module: Available")
    except ImportError:
        print("Oobabooga 'shared' module: Not available")
    
    try:
        from modules.text_generation import generate_reply
        print("Oobabooga 'generate_reply' function: Available")
    except ImportError:
        print("Oobabooga 'generate_reply' function: Not available")
    
    print("=== DIAGNOSTICS COMPLETE ===")

# Test function
def test_bridge_injection():
    """
    Test the bridge system with a simple message
    """
    test_message = "This is a test message from the bridge system."
    
    print("Testing bridge injection...")
    success = inject_idle_message_via_bridge(test_message)
    
    if success:
        print("SUCCESS: Test message injection completed")
    else:
        print("ERROR: Test message injection failed")
        diagnose_bridge_system()
    
    return success