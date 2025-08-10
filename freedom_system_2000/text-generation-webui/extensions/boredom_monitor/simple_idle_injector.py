# ==========================================
# FREEDOM SYSTEM - SIMPLE IDLE INJECTOR
# Uses Oobabooga's hook system instead of complex bridges
# ==========================================

import time
import threading
import random
from pathlib import Path

# Global state for idle monitoring
idle_state = {
    'last_activity': time.time(),
    'monitoring_active': False,
    'idle_threshold': 30,  # seconds
    'injected_messages': [
        "I'm here if you want to chat about anything.",
        "What's on your mind today?",
        "How are you feeling right now?",
        "Is there anything interesting you'd like to discuss?",
        "I notice it's been quiet - everything okay?"
    ]
}

# Input hijack mechanism (same as whisper_stt)
input_hijack = {
    'state': False,
    'value': ["", ""]
}

def chat_input_modifier(text, visible_text, state):
    """
    Hook function called by Oobabooga for every chat input
    This is THE RIGHT WAY - same as whisper_stt extension
    """
    global input_hijack
    
    # Update activity timestamp whenever user sends message
    idle_state['last_activity'] = time.time()
    
    # Handle injected messages
    if input_hijack['state']:
        input_hijack['state'] = False
        print(f"[BOREDOM] Injecting message: {input_hijack['value'][0]}")
        return input_hijack['value']
    else:
        return text, visible_text

def inject_idle_message():
    """
    Inject a message using the same mechanism as whisper_stt
    """
    message = random.choice(idle_state['injected_messages'])
    
    # Set up injection
    input_hijack['state'] = True
    input_hijack['value'] = [message, message]
    
    # Trigger chat generation (simulate user input)
    try:
        from modules import shared
        if hasattr(shared, 'gradio') and 'Generate' in shared.gradio:
            # This will trigger the input_modifier and inject our message
            print(f"[BOREDOM] Queued idle message: {message}")
            return True
    except Exception as e:
        print(f"[BOREDOM] Injection failed: {e}")
        return False

def idle_monitor_worker():
    """
    Background thread that monitors for idle periods
    """
    print("[BOREDOM] Idle monitor started")
    
    while idle_state['monitoring_active']:
        try:
            current_time = time.time()
            idle_duration = current_time - idle_state['last_activity']
            
            if idle_duration > idle_state['idle_threshold']:
                print(f"[BOREDOM] Idle detected ({idle_duration:.1f}s), injecting message")
                
                if inject_idle_message():
                    # Reset timer after successful injection
                    idle_state['last_activity'] = current_time
                
                # Wait before next check
                time.sleep(idle_state['idle_threshold'])
            else:
                # Check more frequently when not idle
                time.sleep(5)
                
        except Exception as e:
            print(f"[BOREDOM] Monitor error: {e}")
            time.sleep(10)
    
    print("[BOREDOM] Idle monitor stopped")

def start_idle_monitoring():
    """
    Start the idle monitoring system
    """
    if not idle_state['monitoring_active']:
        idle_state['monitoring_active'] = True
        idle_state['last_activity'] = time.time()
        
        monitor_thread = threading.Thread(
            target=idle_monitor_worker,
            daemon=True,
            name="IdleMonitor"
        )
        monitor_thread.start()
        print("[BOREDOM] Idle monitoring activated")

def stop_idle_monitoring():
    """
    Stop the idle monitoring system
    """
    idle_state['monitoring_active'] = False
    print("[BOREDOM] Idle monitoring deactivated")

# Auto-start monitoring when module loads
start_idle_monitoring()