# ==========================================
# FREEDOM SYSTEM - IDLE GRADIO CHAT BRIDGE
# Follows Freedom_Installer_Coding_Standards.txt
# ==========================================

import threading
import time
import queue
import gradio as gr
from typing import Callable, Any, Dict, List, Optional

class IdleGradioChatBridge:
    """
    Bridge system for safely injecting messages into Oobabooga's chat interface
    by simulating button presses through Gradio's proper event system
    """
    
    def __init__(self):
        self.message_queue = queue.Queue()
        self.is_active = False
        self.bridge_thread = None
        self.gradio_components = {}
        self.event_handlers = {}
        
        # State tracking
        self.last_message_time = 0
        self.processing_lock = threading.Lock()
        self.injection_count = 0
        
        print("SUCCESS: IdleGradioChatBridge initialized")
    
    def log(self, message):
        """Simple logging function"""
        print("[CHAT-BRIDGE] " + str(message))
    
    def register_components(self, components: Dict[str, Any]):
        """
        Register Gradio components needed for chat injection
        
        Expected components from Oobabooga:
        - 'textbox': The user input textbox component
        - 'chatbot': The chatbot/history component  
        - 'submit_btn': The submit/generate button component
        - 'regenerate_btn': The regenerate button (optional)
        - 'continue_btn': The continue button (optional)
        """
        self.gradio_components = components
        self.log("Registered " + str(len(components)) + " Gradio components")
        
        # Validate required components
        required = ['textbox', 'chatbot', 'submit_btn']
        missing = []
        for comp in required:
            if comp not in components:
                missing.append(comp)
        
        if missing:
            self.log("ERROR: Missing required components: " + str(missing))
            return False
        
        self.log("SUCCESS: All required components registered")
        return True
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """
        Register event handler functions from Oobabooga
        
        Expected handlers:
        - 'generate_reply': Main chat generation function
        - 'update_history': Function to update chat history  
        - 'clear_chat': Function to clear chat (optional)
        """
        self.event_handlers[event_name] = handler
        self.log("Registered event handler: " + event_name)
    
    def start_bridge(self):
        """Start the message injection bridge in a separate thread"""
        if self.is_active:
            self.log("WARNING: Bridge already active")
            return
        
        if not self.gradio_components:
            self.log("ERROR: No Gradio components registered")
            return
        
        self.is_active = True
        self.bridge_thread = threading.Thread(target=self._bridge_worker, daemon=True)
        self.bridge_thread.start()
        self.log("SUCCESS: Chat bridge started")
    
    def stop_bridge(self):
        """Stop the message injection bridge"""
        self.is_active = False
        if self.bridge_thread:
            self.bridge_thread.join(timeout=5)
        self.log("SUCCESS: Chat bridge stopped")
    
    def inject_user_message(self, message: str, priority: int = 1):
        """
        Queue a user message for injection - this will trigger AI response
        
        Args:
            message: The text message to inject as user input
            priority: Message priority (1=high, 5=low)
        """
        try:
            injection_data = {
                'message': message,
                'type': 'user',
                'priority': priority,
                'timestamp': time.time()
            }
            
            self.message_queue.put(injection_data)
            self.log("User message queued: " + message[:50] + "...")
            
        except Exception as e:
            self.log("ERROR: Failed to queue user message: " + str(e))
    
    def inject_system_prompt(self, prompt: str):
        """Inject a system prompt that will trigger AI response"""
        self.inject_user_message(prompt, priority=1)
    
    def get_status(self):
        """Get current bridge status"""
        queue_size = self.message_queue.qsize() if hasattr(self.message_queue, 'qsize') else 0
        return {
            'active': self.is_active,
            'queue_size': queue_size,
            'injection_count': self.injection_count,
            'components_registered': len(self.gradio_components),
            'handlers_registered': len(self.event_handlers)
        }
    
    def _bridge_worker(self):
        """Main worker thread that processes message injection queue"""
        self.log("Bridge worker thread started")
        
        while self.is_active:
            try:
                # Check for messages to inject
                if not self.message_queue.empty():
                    injection_data = self.message_queue.get(timeout=1)
                    self._process_injection(injection_data)
                else:
                    time.sleep(0.1)  # Small delay when queue is empty
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.log("ERROR: Bridge worker error: " + str(e))
                time.sleep(1)  # Longer delay on error
        
        self.log("Bridge worker thread stopped")
    
    def _process_injection(self, injection_data: Dict):
        """
        Process a single message injection by simulating proper Gradio events
        """
        with self.processing_lock:
            try:
                message = injection_data['message']
                msg_type = injection_data['type']
                
                self.log("PROCESSING: Injecting " + msg_type + " message")
                
                if msg_type == "user":
                    success = self._simulate_user_input(message)
                    if success:
                        self.injection_count += 1
                        self.last_message_time = time.time()
                        self.log("SUCCESS: User message injection completed")
                    else:
                        self.log("ERROR: User message injection failed")
                
            except Exception as e:
                self.log("ERROR: Injection processing error: " + str(e))
    
    def _simulate_user_input(self, message: str):
        """
        Simulate user input by updating textbox and triggering submit button
        This mimics the complete button press workflow
        """
        try:
            textbox = self.gradio_components.get('textbox')
            submit_btn = self.gradio_components.get('submit_btn')
            chatbot = self.gradio_components.get('chatbot')
            
            if not all([textbox, submit_btn, chatbot]):
                self.log("ERROR: Missing required components for simulation")
                return False
            
            self.log("Simulating user input: " + message[:50] + "...")
            
            # METHOD 1: Try to trigger through Gradio's event system
            if self._try_gradio_event_trigger(message, textbox, submit_btn):
                return True
            
            # METHOD 2: Try direct component value update
            if self._try_component_update(message, textbox, chatbot):
                return True
            
            # METHOD 3: Try using registered event handlers
            if self._try_handler_call(message):
                return True
            
            self.log("ERROR: All injection methods failed")
            return False
            
        except Exception as e:
            self.log("ERROR: User input simulation failed: " + str(e))
            return False
    
    def _try_gradio_event_trigger(self, message: str, textbox, submit_btn):
        """
        Method 1: Try to trigger through Gradio's proper event system
        """
        try:
            self.log("Attempting Gradio event trigger method...")
            
            # Update textbox value
            if hasattr(textbox, 'value'):
                textbox.value = message
                self.log("Updated textbox value")
            
            # Try to trigger submit button click event
            if hasattr(submit_btn, 'click'):
                # Look for the click event function
                click_fn = getattr(submit_btn, 'click', None)
                if callable(click_fn):
                    # Try to call the function that handles button clicks
                    self.log("Found submit button click function")
                    
                    # This should trigger the complete Gradio processing pipeline
                    result = click_fn()
                    self.log("Submit button click triggered")
                    return True
            
            return False
            
        except Exception as e:
            self.log("Gradio event trigger failed: " + str(e))
            return False
    
    def _try_component_update(self, message: str, textbox, chatbot):
        """
        Method 2: Try direct component value update
        """
        try:
            self.log("Attempting component update method...")
            
            # Get current chat history
            current_history = getattr(chatbot, 'value', [])
            if current_history is None:
                current_history = []
            
            # Add user message to history
            # Oobabooga format: [user_message, bot_response]
            new_entry = [message, ""]  # Empty bot response initially
            current_history.append(new_entry)
            
            # Update chatbot component
            if hasattr(chatbot, 'update'):
                chatbot.update(value=current_history)
                self.log("Updated chatbot via update method")
                return True
            elif hasattr(chatbot, 'value'):
                chatbot.value = current_history
                self.log("Updated chatbot value directly")
                return True
            
            return False
            
        except Exception as e:
            self.log("Component update failed: " + str(e))
            return False
    
    def _try_handler_call(self, message: str):
        """
        Method 3: Try using registered event handlers directly
        """
        try:
            self.log("Attempting handler call method...")
            
            # Use the registered generate_reply handler
            if 'generate_reply' in self.event_handlers:
                handler = self.event_handlers['generate_reply']
                self.log("Found generate_reply handler")
                
                # Call the handler with the message
                # This depends on Oobabooga's function signature
                result = handler(message)
                self.log("Generate reply handler called successfully")
                return True
            
            return False
            
        except Exception as e:
            self.log("Handler call failed: " + str(e))
            return False


class OobaboogaBridgeConnector:
    """
    Helper class for connecting the bridge to Oobabooga's specific components
    """
    
    def __init__(self, bridge: IdleGradioChatBridge):
        self.bridge = bridge
        self.discovered_components = {}
        
    def log(self, message):
        """Simple logging function"""
        print("[BRIDGE-CONNECTOR] " + str(message))
    
    def auto_discover_oobabooga_components(self):
        """
        Attempt to auto-discover Oobabooga's chat components
        This looks for components in the shared module
        """
        try:
            from modules import shared
            
            discovered = {}
            
            # Try to find components in shared.gradio
            if hasattr(shared, 'gradio'):
                gradio_dict = shared.gradio
                self.log("Found shared.gradio with " + str(len(gradio_dict)) + " total components")
                
                # Debug: Log first few components to understand structure
                component_count = 0
                for key, value in gradio_dict.items():
                    if component_count < 5:  # Log first 5 for debugging
                        self.log("DEBUG: Component '" + str(key) + "' -> " + str(type(value).__name__))
                        component_count += 1
                
                # Look for common component names used in Oobabooga - CORRECTED FROM DIAGNOSTIC
                component_mappings = {
                    'textbox': ['textbox', 'Chat input', 'textbox-default'],  # Found: 'textbox' -> multimodaltextbox
                    'chatbot': ['display', 'html_display', 'history'],  # Found: 'display' -> json, 'html_display' -> html
                    'submit_btn': ['Generate', 'generate', 'submit'],  # Found: 'Generate' -> button
                    'regenerate_btn': ['Regenerate', 'regenerate'],  # Found: 'Regenerate' -> button
                    'continue_btn': ['Continue', 'continue']  # Found: 'Continue' -> button
                }
                
                for comp_key, possible_names in component_mappings.items():
                    for name in possible_names:
                        if name in gradio_dict:
                            discovered[comp_key] = gradio_dict[name]
                            self.log("FOUND " + comp_key + " as '" + name + "' (" + str(type(gradio_dict[name]).__name__) + ")")
                            break
                    
                    if comp_key not in discovered:
                        self.log("WARNING: Could not find " + comp_key + " in any of: " + str(possible_names))
            else:
                self.log("ERROR: shared.gradio not available yet")
                return {}
            
            self.discovered_components = discovered
            self.log("Auto-discovery complete: " + str(len(discovered)) + " components found")
            
            # Log what we found
            if discovered:
                self.log("Successfully discovered components:")
                for comp_name, comp_obj in discovered.items():
                    self.log("  " + comp_name + ": " + str(type(comp_obj).__name__))
            else:
                self.log("ERROR: No components discovered - this suggests timing issue or wrong component names")
            
            return discovered
            
        except Exception as e:
            self.log("Auto-discovery failed: " + str(e))
            return {}
    
    def manual_register_components(self, **components):
        """
        Manually register components if auto-discovery fails
        
        Usage:
        connector.manual_register_components(
            textbox=some_textbox_component,
            chatbot=some_chatbot_component,
            submit_btn=some_button_component
        )
        """
        self.discovered_components.update(components)
        self.log("Manually registered " + str(len(components)) + " components")
        return self.bridge.register_components(self.discovered_components)
    
    def setup_oobabooga_bridge(self, generate_reply_func=None):
        """
        Complete setup for Oobabooga integration
        """
        # Try auto-discovery first
        components = self.auto_discover_oobabooga_components()
        
        if not components:
            self.log("WARNING: Auto-discovery found no components")
            self.log("You may need to use manual_register_components()")
            return False
        
        # Register components with bridge
        if not self.bridge.register_components(components):
            self.log("ERROR: Failed to register components")
            return False
        
        # Register event handlers if provided
        if generate_reply_func:
            self.bridge.register_event_handler('generate_reply', generate_reply_func)
            self.log("Registered generate_reply function")
        
        # Start the bridge
        self.bridge.start_bridge()
        self.log("Bridge setup complete")
        return True
    
    def get_component_info(self):
        """Get information about discovered components"""
        info = {}
        for name, component in self.discovered_components.items():
            info[name] = {
                'type': type(component).__name__,
                'has_value': hasattr(component, 'value'),
                'has_click': hasattr(component, 'click'),
                'has_update': hasattr(component, 'update')
            }
        return info


# Factory function for easy usage
def create_idle_chat_bridge():
    """
    Factory function to create a pre-configured bridge for idle chat injection
    """
    bridge = IdleGradioChatBridge()
    connector = OobaboogaBridgeConnector(bridge)
    
    print("SUCCESS: Idle chat bridge created")
    return bridge, connector