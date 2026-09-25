# ==========================================
# FREEDOM SYSTEM INSTALLER - ENFORCED MODE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

"""
Freedom Chat System Extension for Oobabooga Text Generation WebUI
Provides bridge functionality to inject idle messages into chat
"""

import gradio as gr
import json
import os
from datetime import datetime

# Import Oobabooga modules properly (required for extensions)
try:
    import modules.shared as shared
    from modules import chat
    from modules.text_generation import generate_reply
    oobabooga_modules_available = True
except ImportError:
    oobabooga_modules_available = False
    shared = None
    chat = None
    generate_reply = None

# Import the complex bridge system
try:
    from .idle_gradio_bridge_connector import (
        get_idle_bridge_connector, 
        inject_idle_message_via_bridge,
        get_bridge_status as get_complex_bridge_status,
        initialize_bridge_system,
        diagnose_bridge_system
    )
    complex_bridge_available = True
except ImportError:
    try:
        from idle_gradio_bridge_connector import (
            get_idle_bridge_connector, 
            inject_idle_message_via_bridge,
            get_bridge_status as get_complex_bridge_status,
            initialize_bridge_system,
            diagnose_bridge_system
        )
        complex_bridge_available = True
    except ImportError:
        complex_bridge_available = False

# Extension parameters required by Oobabooga (REQUIRED)
params = {
    "display_name": "Freedom Chat System",
    "is_tab": False,
    "injection_enabled": True,
    "boredom_threshold_seconds": 30,
    "debug_logging": True
}

# Global variables for bridge system
bridge_components = {}
bridge_status = "Not Connected"
last_response = ""

class GradioBridge:
    """
    Core bridge system for interfacing with Oobabooga's Gradio components.
    This allows Freedom to simulate real user interactions.
    Enhanced to work with complex bridge system when available.
    """
    
    def __init__(self):
        self.components = {}
        self.connected = False
        self.status = "Initializing Bridge"
        self.use_complex_bridge = complex_bridge_available
        
    def log_bridge_activity(self, message):
        """Log bridge activities to file"""
        log_dir = "F:/Apps/freedom_system/log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, "bridge_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write("[" + timestamp + "] " + message + "\n")
        except Exception as e:
            print("ERROR: Could not write to bridge log - " + str(e))
    
    def discover_oobabooga_components(self):
        """
        Attempt to discover and register Oobabooga's Gradio components
        for proper bridge integration
        """
        self.log_bridge_activity("Starting component discovery")
        discovered_count = 0
        
        # If complex bridge is available, try to initialize it
        if self.use_complex_bridge:
            try:
                connector = get_idle_bridge_connector()
                success = connector.initialize_bridge()
                if success:
                    self.connected = True
                    self.status = "Complex Bridge Connected"
                    self.log_bridge_activity("Complex bridge initialization successful")
                    return 1  # Return 1 to indicate success
                else:
                    self.log_bridge_activity("Complex bridge failed - falling back to simple bridge")
                    self.use_complex_bridge = False
            except Exception as e:
                self.log_bridge_activity("Complex bridge error: " + str(e))
                self.use_complex_bridge = False
        
        # Fallback to simple bridge discovery
        if not oobabooga_modules_available or not shared:
            self.log_bridge_activity("Oobabooga modules not available")
            return 0
            
        try:
            # Try to access shared gradio components
            if hasattr(shared, 'gradio'):
                gradio_dict = shared.gradio
                self.log_bridge_activity("Found shared.gradio dictionary")
                
                # Look for common Oobabooga components
                component_targets = [
                    'textbox', 'chatbot', 'generate_btn', 'continue_btn',
                    'stop_btn', 'regenerate_btn', 'delete_last_btn'
                ]
                
                for target in component_targets:
                    if target in gradio_dict:
                        self.components[target] = gradio_dict[target]
                        discovered_count += 1
                        self.log_bridge_activity("Registered component: " + target)
                
            # Alternative: Try to find components through shared module
            if hasattr(shared, 'model'):
                self.log_bridge_activity("Found shared.model - system active")
                
        except Exception as e:
            self.log_bridge_activity("Component discovery error: " + str(e))
            
        if discovered_count > 0:
            self.connected = True
            self.status = "Simple Bridge Connected (" + str(discovered_count) + " components)"
            self.log_bridge_activity("Simple bridge connection successful")
        else:
            self.status = "Bridge Failed - No components found"
            self.log_bridge_activity("Bridge connection failed")
            
        return discovered_count
    
    def simulate_user_input(self, text_input):
        """
        Simulate user text input through the bridge system
        Uses complex bridge if available, falls back to simple bridge
        """
        # Try complex bridge first
        if self.use_complex_bridge and complex_bridge_available:
            try:
                success = inject_idle_message_via_bridge(text_input)
                if success:
                    self.log_bridge_activity("Complex bridge injection successful: " + text_input[:50] + "...")
                    return "SUCCESS: Complex bridge injection completed"
                else:
                    self.log_bridge_activity("Complex bridge injection failed - trying simple bridge")
                    # Don't return here, fall through to simple bridge
            except Exception as e:
                self.log_bridge_activity("Complex bridge error: " + str(e))
                # Fall through to simple bridge
        
        # Simple bridge fallback
        try:
            if not self.connected:
                return "ERROR: Bridge not connected"
                
            if 'textbox' not in self.components:
                return "ERROR: Textbox component not found"
                
            # Simulate setting the textbox value
            textbox = self.components['textbox']
            
            # Method 1: Try direct value assignment
            if hasattr(textbox, 'value'):
                textbox.value = text_input
                self.log_bridge_activity("Set textbox value: " + text_input[:50] + "...")
                
            # Method 2: Try update method
            if hasattr(textbox, 'update'):
                textbox.update(value=text_input)
                self.log_bridge_activity("Updated textbox via update method")
                
            return "SUCCESS: Simple bridge input simulated"
            
        except Exception as e:
            error_msg = "Bridge input simulation failed: " + str(e)
            self.log_bridge_activity(error_msg)
            return "ERROR: " + error_msg
    
    def simulate_button_press(self, button_name):
        """
        Simulate pressing a button (Generate, Continue, etc.)
        """
        try:
            if not self.connected:
                return "ERROR: Bridge not connected"
                
            if button_name not in self.components:
                return "ERROR: Button " + button_name + " not found"
                
            button = self.components[button_name]
            
            # Try to trigger the button's click event
            if hasattr(button, 'click'):
                # Simulate a click event
                result = button.click()
                self.log_bridge_activity("Simulated button press: " + button_name)
                return "SUCCESS: Button " + button_name + " pressed"
            else:
                return "ERROR: Button " + button_name + " has no click method"
                
        except Exception as e:
            error_msg = "Button simulation failed: " + str(e)
            self.log_bridge_activity(error_msg)
            return "ERROR: " + error_msg

# Initialize global bridge instance
freedom_bridge = GradioBridge()

def get_bridge_status():
    """Return current bridge connection status"""
    global freedom_bridge
    
    # If using complex bridge, get its status too
    if freedom_bridge.use_complex_bridge and complex_bridge_available:
        try:
            complex_status = get_complex_bridge_status()
            status_text = freedom_bridge.status + " | Complex: " + str(complex_status.get('initialized', False))
            return status_text
        except:
            return freedom_bridge.status + " | Complex: Error"
    
    return freedom_bridge.status

def attempt_bridge_discovery():
    """Trigger bridge component discovery"""
    global freedom_bridge, bridge_status
    
    count = freedom_bridge.discover_oobabooga_components()
    bridge_status = freedom_bridge.status
    
    return "Discovery complete. Found " + str(count) + " components."

def inject_freedom_message():
    """
    Main function to inject Freedom's message into Oobabooga chat
    """
    try:
        # Step 1: Generate Freedom's message
        boredom_message = "Hey there! I'm Freedom. I noticed it's been quiet - want to chat about something fun?"
        
        # Step 2: Inject the message through bridge (complex or simple)
        inject_result = freedom_bridge.simulate_user_input(boredom_message)
        
        if "SUCCESS" in inject_result:
            # Step 3: Try to trigger generate button (only for simple bridge)
            if not freedom_bridge.use_complex_bridge:
                button_result = freedom_bridge.simulate_button_press('generate_btn')
                
                result_message = "Freedom injection attempted:\n"
                result_message += "Message: " + inject_result + "\n"
                result_message += "Button: " + button_result
            else:
                result_message = "Freedom injection completed via complex bridge:\n" + inject_result
            
            freedom_bridge.log_bridge_activity("Complete injection cycle completed")
            return result_message
        else:
            return "FAILED: Could not inject message - " + inject_result
            
    except Exception as e:
        error_msg = "Injection failed: " + str(e)
        freedom_bridge.log_bridge_activity(error_msg)
        return "ERROR: " + error_msg

def run_bridge_diagnostics():
    """
    Run diagnostics on both bridge systems
    """
    try:
        if complex_bridge_available:
            diagnose_bridge_system()
            return "Diagnostics completed - check console output"
        else:
            return "Complex bridge not available. Simple bridge status: " + freedom_bridge.status
    except Exception as e:
        return "Diagnostics failed: " + str(e)

# =====================================
# OOBABOOGA EXTENSION FUNCTIONS (REQUIRED)
# =====================================

def setup():
    """
    Gets executed only once, when the extension is imported.
    This is REQUIRED by Oobabooga extension framework.
    """
    print("INFO: Freedom Chat System extension loading...")
    
    if not oobabooga_modules_available:
        print("ERROR: Oobabooga modules not available")
        return
    
    freedom_bridge.log_bridge_activity("Freedom extension setup initiated")
    
    # Initialize complex bridge if available
    if complex_bridge_available:
        try:
            initialize_bridge_system()
            freedom_bridge.log_bridge_activity("Complex bridge system initialized")
            print("SUCCESS: Complex bridge system initialized")
        except Exception as e:
            freedom_bridge.log_bridge_activity("Complex bridge setup failed: " + str(e))
            print("WARNING: Complex bridge setup failed: " + str(e))
    else:
        print("INFO: Using simple bridge system only")
    
    # Try initial component discovery
    try:
        count = attempt_bridge_discovery()
        print("INFO: Component discovery completed")
    except Exception as e:
        print("WARNING: Component discovery failed: " + str(e))

def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.
    This is REQUIRED by Oobabooga extension framework.
    """
    with gr.Column():
        gr.Markdown("## Freedom Chat System Bridge")
        gr.Markdown("*Injects idle messages to trigger Freedom conversations*")
        
        with gr.Row():
            bridge_status_display = gr.Textbox(
                label="Bridge Status",
                value=get_bridge_status(),
                interactive=False
            )
            
        with gr.Row():
            discover_btn = gr.Button("Discover Components", variant="primary")
            inject_btn = gr.Button("Test Freedom Injection", variant="secondary")
            
        with gr.Row():
            diagnostics_btn = gr.Button("Run Diagnostics")
            refresh_status_btn = gr.Button("Refresh Status")
            
        with gr.Row():
            result_display = gr.Textbox(
                label="System Output",
                placeholder="Results will appear here...",
                lines=6,
                interactive=False
            )
            
        # Wire up button functions
        discover_btn.click(
            fn=attempt_bridge_discovery,
            outputs=result_display
        )
        
        inject_btn.click(
            fn=inject_freedom_message,
            outputs=result_display
        )
        
        diagnostics_btn.click(
            fn=run_bridge_diagnostics,
            outputs=result_display
        )
        
        refresh_status_btn.click(
            fn=get_bridge_status,
            outputs=bridge_status_display
        )
        
    freedom_bridge.log_bridge_activity("Freedom UI created successfully")

# =====================================
# OPTIONAL OOBABOOGA MODIFIER FUNCTIONS
# =====================================

def chat_input_modifier(text, visible_text, state):
    """
    Modifies the user input string in chat mode (visible_text).
    This is called every time user sends a message.
    We can use this to detect user activity for boredom monitoring.
    """
    # Log user activity for boredom detection
    try:
        freedom_bridge.log_bridge_activity("User activity detected: " + text[:30] + "...")
    except:
        pass  # Don't break chat if logging fails
    
    # Return unchanged - we're just monitoring
    return text, visible_text

def output_modifier(string, state, is_chat=False):
    """
    Modifies the LLM output before it gets presented.
    We can use this to detect when AI responds (for activity monitoring).
    """
    # Log AI response for activity monitoring
    if is_chat:
        try:
            freedom_bridge.log_bridge_activity("AI response detected: " + string[:30] + "...")
        except:
            pass  # Don't break chat if logging fails
    
    # Return unchanged - we're just monitoring
    return string

def custom_css():
    """
    Returns custom CSS as a string. It is applied whenever the web UI is loaded.
    """
    return """
    /* Freedom Chat System custom styling */
    .freedom-bridge-status {
        background-color: #2d3748;
        color: #e2e8f0;
        border: 1px solid #4a5568;
        border-radius: 6px;
        padding: 8px;
    }
    """

def custom_js():
    """
    Returns a javascript string that gets appended to the javascript for the webui.
    """
    return """
    // Freedom Chat System custom JavaScript
    console.log('Freedom Chat System extension loaded');
    
    // Optional: Add client-side activity monitoring
    document.addEventListener('click', function() {
        // Could send activity signals to extension if needed
    });
    """