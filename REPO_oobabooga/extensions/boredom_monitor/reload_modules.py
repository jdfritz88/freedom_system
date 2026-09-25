#!/usr/bin/env python3
"""
Module Reloader for Boredom Monitor Extension
Allows hot-reloading of modules without restarting the server
"""

import sys
import importlib
from pathlib import Path

def reload_boredom_modules():
    """
    Force reload of all boredom monitor modules to pick up code changes
    This is necessary because Python caches imported modules
    """
    
    modules_to_reload = [
        'extensions.boredom_monitor.idle_emotion_manager',
        'extensions.boredom_monitor.api_client',
        'extensions.boredom_monitor.idle_boredom_detector',
        'extensions.boredom_monitor.config_sync',
        'extensions.boredom_monitor.idle_logging_system'
    ]
    
    reloaded = []
    failed = []
    
    for module_name in modules_to_reload:
        try:
            if module_name in sys.modules:
                # Module is loaded, reload it
                module = sys.modules[module_name]
                importlib.reload(module)
                reloaded.append(module_name)
                print(f"[RELOAD] Successfully reloaded: {module_name}")
            else:
                print(f"[RELOAD] Module not loaded yet: {module_name}")
        except Exception as e:
            failed.append((module_name, str(e)))
            print(f"[RELOAD] Failed to reload {module_name}: {e}")
    
    # Summary
    print(f"\n[RELOAD] Summary:")
    print(f"  Reloaded: {len(reloaded)} modules")
    print(f"  Failed: {len(failed)} modules")
    
    if failed:
        print("\n[RELOAD] Failed modules:")
        for module_name, error in failed:
            print(f"  - {module_name}: {error}")
    
    return len(failed) == 0

def reinitialize_emotion_manager():
    """
    Create a new instance of IdleEmotionManager with the reloaded module
    """
    try:
        # First reload the module
        if 'extensions.boredom_monitor.idle_emotion_manager' in sys.modules:
            module = sys.modules['extensions.boredom_monitor.idle_emotion_manager']
            importlib.reload(module)
            
            # Now create new instance with reloaded class
            from extensions.boredom_monitor.idle_emotion_manager import IdleEmotionManager
            manager = IdleEmotionManager()
            
            # Test that new methods exist
            if hasattr(manager, 'get_current_emotion') and \
               hasattr(manager, 'get_horny_stage') and \
               hasattr(manager, 'is_cooldown_active'):
                print("[RELOAD] IdleEmotionManager has all required methods")
                return manager
            else:
                print("[RELOAD] ERROR: IdleEmotionManager missing required methods!")
                missing = []
                if not hasattr(manager, 'get_current_emotion'):
                    missing.append('get_current_emotion')
                if not hasattr(manager, 'get_horny_stage'):
                    missing.append('get_horny_stage')
                if not hasattr(manager, 'is_cooldown_active'):
                    missing.append('is_cooldown_active')
                print(f"[RELOAD] Missing methods: {', '.join(missing)}")
                return None
        else:
            print("[RELOAD] Module not in sys.modules, cannot reload")
            return None
            
    except Exception as e:
        print(f"[RELOAD] Failed to reinitialize IdleEmotionManager: {e}")
        return None

if __name__ == "__main__":
    print("=== BOREDOM MONITOR MODULE RELOADER ===")
    print("\nReloading all modules...")
    
    if reload_boredom_modules():
        print("\n[SUCCESS] All modules reloaded successfully")
        
        print("\nTesting IdleEmotionManager reload...")
        manager = reinitialize_emotion_manager()
        if manager:
            print("[SUCCESS] IdleEmotionManager reinitialized with new methods")
        else:
            print("[FAIL] IdleEmotionManager reinitialization failed")
    else:
        print("\n[FAIL] Some modules failed to reload")