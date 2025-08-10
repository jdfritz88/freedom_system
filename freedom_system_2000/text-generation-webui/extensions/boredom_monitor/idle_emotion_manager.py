# ==========================================
# FREEDOM SYSTEM - IDLE EMOTION MANAGER
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
import random
import time
from datetime import datetime, timedelta

class IdleEmotionManager:
    """
    Manages emotional states and horny progression logic for the Freedom System
    Handles sequential horny stages (1->2->3->60min cooldown) and other emotion types
    
    Follows Standards:
    - #1: Folder Isolation - Lives in boredom_monitor extension folder
    - #2: Environment Usage - Uses shared _env folder
    - #9: Script Loader Override - Overrides Python paths for _env
    - #11: Log Placement - Logs to root log folder
    - #12: Log Format - Includes timestamps, component names, status indicators
    """
    
    def __init__(self, config_path=None, templates_path=None, cooldown_path=None):
        self.component_name = "EMOTION-MANAGER"
        
        # Standard #11: Log Placement - Use root log folder
        self.log_file = Path("F:/Apps/freedom_system/log/boredom_monitor.log")
        
        # Configuration file paths - Fixed to use extension directory
        extension_dir = Path(__file__).parent
        self.config_path = config_path or (extension_dir / "idle_response_config.json")
        self.templates_path = templates_path or (extension_dir / "idle_meta_prompt_templates.json")  
        self.cooldown_path = cooldown_path or (extension_dir / "idle_cooldown_tracker.json")
        
        # Initialize state
        self.current_emotion = None
        self.horny_stage = 1
        self.initialization_success = False
        
        try:
            # Load configuration
            self.config = self._load_config()
            self.templates = self._load_templates()
            self.cooldown_data = self._load_cooldown_data()
            
            self.initialization_success = True
            self.log("IdleEmotionManager initialized successfully", "[OK]")
            
        except Exception as e:
            self.log("IdleEmotionManager initialization failed: " + str(e), "[FAIL]")
            # Set defaults to prevent crashes
            self.config = self._get_default_config()
            self.templates = {}
            self.cooldown_data = self._get_default_cooldown_data()
    
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
    
    def _get_default_config(self):
        """Default configuration if file loading fails"""
        return {
            "idle_minutes": 7,
            "horny_cooldown_minutes": 60,
            "category_weights": {
                "bored": 0.4,
                "lonely": 0.4,
                "horny": 0.2
            },
            "enable_logging": True
        }
    
    def _get_default_cooldown_data(self):
        """Default cooldown data if file loading fails"""
        return {
            "horny_stage": 1,
            "horny_cooldown_until": None
        }
    
    def _load_config(self):
        """Load emotion configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.log("Configuration loaded from " + str(config_file), "[OK]")
                return config
            else:
                self.log("Configuration file not found, using defaults", "[WARNING]")
                return self._get_default_config()
                
        except Exception as e:
            self.log("Failed to load config: " + str(e), "[ERROR]")
            return self._get_default_config()
    
    def _load_templates(self):
        """Load message templates from JSON file"""
        try:
            templates_file = Path(self.templates_path)
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                self.log("Templates loaded from " + str(templates_file), "[OK]")
                return templates
            else:
                self.log("Templates file not found", "[WARNING]")
                return {}
                
        except Exception as e:
            self.log("Failed to load templates: " + str(e), "[ERROR]")
            return {}
    
    def _load_cooldown_data(self):
        """Load cooldown tracking data from JSON file"""
        try:
            cooldown_file = Path(self.cooldown_path)
            if cooldown_file.exists():
                with open(cooldown_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.log("Cooldown data loaded from " + str(cooldown_file), "[OK]")
                return data
            else:
                self.log("Cooldown file not found, using defaults", "[INFO]")
                return self._get_default_cooldown_data()
                
        except Exception as e:
            self.log("Failed to load cooldown data: " + str(e), "[ERROR]")
            return self._get_default_cooldown_data()
    
    def _save_cooldown_data(self):
        """Save cooldown tracking data to JSON file"""
        try:
            cooldown_file = Path(self.cooldown_path)
            with open(cooldown_file, 'w', encoding='utf-8') as f:
                json.dump(self.cooldown_data, f, indent=2)
            self.log("Cooldown data saved to " + str(cooldown_file), "[OK]")
            return True
            
        except Exception as e:
            self.log("Failed to save cooldown data: " + str(e), "[FAIL]")
            return False
    
    def is_horny_on_cooldown(self):
        """Check if horny mood is currently on cooldown"""
        if not self.cooldown_data.get("horny_cooldown_until"):
            return False
        
        try:
            cooldown_until = datetime.fromisoformat(self.cooldown_data["horny_cooldown_until"])
            current_time = datetime.now()
            
            if current_time < cooldown_until:
                remaining = cooldown_until - current_time
                remaining_minutes = int(remaining.total_seconds() / 60)
                self.log("Horny mood on cooldown for " + str(remaining_minutes) + " more minutes", "[INFO]")
                return True
            else:
                # Cooldown expired, reset horny stage
                self.cooldown_data["horny_stage"] = 1
                self.cooldown_data["horny_cooldown_until"] = None
                if self._save_cooldown_data():
                    self.log("Horny cooldown expired, stage reset to 1", "[OK]")
                return False
                
        except Exception as e:
            self.log("Cooldown check failed: " + str(e), "[ERROR]")
            return False
    
    def select_emotion_type(self):
        """
        Select an emotion type based on weights and cooldown rules
        Returns: 'bored', 'lonely', or 'horny'
        """
        try:
            weights = self.config.get("category_weights", {})
            
            # Check if horny is on cooldown
            if self.is_horny_on_cooldown():
                # Remove horny from selection, redistribute weights
                available_weights = {}
                total_weight = 0
                
                for emotion, weight in weights.items():
                    if emotion != "horny":
                        available_weights[emotion] = weight
                        total_weight += weight
                
                # Normalize weights
                if total_weight > 0:
                    for emotion in available_weights:
                        available_weights[emotion] = available_weights[emotion] / total_weight
            else:
                available_weights = weights
            
            # Select emotion based on weights
            emotions = list(available_weights.keys())
            weights_list = list(available_weights.values())
            
            if not emotions:
                self.log("No emotions available, defaulting to bored", "[WARNING]")
                return "bored"
            
            selected_emotion = random.choices(emotions, weights=weights_list)[0]
            self.log("Selected emotion: " + selected_emotion, "[OK]")
            
            return selected_emotion
            
        except Exception as e:
            self.log("Emotion selection failed: " + str(e), "[ERROR]")
            return "bored"  # Safe fallback
    
    def get_current_horny_stage(self):
        """Get the current horny progression stage"""
        return self.cooldown_data.get("horny_stage", 1)
    
    def advance_horny_stage(self):
        """
        Advance horny stage and handle cooldown activation
        Stage progression: 1 -> 2 -> 3 -> 60-minute cooldown -> reset to 1
        """
        try:
            current_stage = self.get_current_horny_stage()
            
            if current_stage == 1:
                # Progress to stage 2
                self.cooldown_data["horny_stage"] = 2
                self.log("Horny progression: Stage 1 -> Stage 2", "[OK]")
                
            elif current_stage == 2:
                # Progress to stage 3
                self.cooldown_data["horny_stage"] = 3
                self.log("Horny progression: Stage 2 -> Stage 3", "[OK]")
                
            elif current_stage == 3:
                # Activate 60-minute cooldown
                cooldown_minutes = self.config.get("horny_cooldown_minutes", 60)
                cooldown_until = datetime.now() + timedelta(minutes=cooldown_minutes)
                
                self.cooldown_data["horny_stage"] = 1  # Reset for next cycle
                self.cooldown_data["horny_cooldown_until"] = cooldown_until.isoformat()
                
                self.log("Horny progression: Stage 3 -> " + str(cooldown_minutes) + "-minute cooldown activated", "[OK]")
            
            # Save changes
            if not self._save_cooldown_data():
                self.log("Failed to save horny progression state", "[FAIL]")
                return current_stage
            
            return self.cooldown_data["horny_stage"]
            
        except Exception as e:
            self.log("Horny stage advancement failed: " + str(e), "[FAIL]")
            return self.get_current_horny_stage()
    
    def generate_emotional_message(self, emotion_type=None):
        """
        Generate an emotional message based on type and current state
        Handles horny progression logic automatically
        """
        try:
            if emotion_type is None:
                emotion_type = self.select_emotion_type()
            
            self.current_emotion = emotion_type
            
            if emotion_type == "horny":
                message = self._generate_horny_message()
            else:
                message = self._generate_regular_message(emotion_type)
            
            self.log("Generated " + emotion_type + " message successfully", "[OK]")
            return message
            
        except Exception as e:
            self.log("Message generation failed: " + str(e), "[FAIL]")
            return "Freedom wants to chat..."  # Safe fallback
    
    def _generate_horny_message(self):
        """Generate horny message and advance progression"""
        try:
            current_stage = self.get_current_horny_stage()
            
            # Get templates for horny messages
            horny_templates = self.templates.get("horny", [])
            
            if len(horny_templates) >= 3:
                # Use stage-specific template (0-indexed)
                template = horny_templates[current_stage - 1]
            else:
                # Fallback if not enough templates
                template = "Freedom is feeling horny and wants attention..."
            
            # Advance to next stage for future injections
            next_stage = self.advance_horny_stage()
            
            self.log("Generated horny message (stage " + str(current_stage) + "), next stage: " + str(next_stage), "[OK]")
            return template
            
        except Exception as e:
            self.log("Horny message generation failed: " + str(e), "[ERROR]")
            return "Freedom is feeling frisky..."
    
    def _generate_regular_message(self, emotion_type):
        """Generate message for bored/lonely emotions (no cooldown)"""
        try:
            templates = self.templates.get(emotion_type, [])
            
            if templates:
                template = random.choice(templates)
            else:
                # Fallback messages
                fallback_messages = {
                    "bored": "Freedom is bored and wants something to do...",
                    "lonely": "Freedom feels lonely and needs attention..."
                }
                template = fallback_messages.get(emotion_type, "Freedom wants to chat...")
            
            self.log("Generated " + emotion_type + " message (no cooldown)", "[OK]")
            return template
            
        except Exception as e:
            self.log("Regular message generation failed: " + str(e), "[ERROR]")
            return "Freedom wants to chat..."
    
    def get_emotion_status(self):
        """Get current emotion system status"""
        try:
            horny_on_cooldown = self.is_horny_on_cooldown()
            horny_stage = self.get_current_horny_stage()
            
            status = {
                "current_emotion": self.current_emotion,
                "horny_stage": horny_stage,
                "horny_on_cooldown": horny_on_cooldown,
                "available_emotions": [],
                "initialization_success": self.initialization_success
            }
            
            # Determine available emotions
            weights = self.config.get("category_weights", {})
            for emotion in weights.keys():
                if emotion == "horny" and horny_on_cooldown:
                    continue
                status["available_emotions"].append(emotion)
            
            if horny_on_cooldown and self.cooldown_data.get("horny_cooldown_until"):
                try:
                    cooldown_until = datetime.fromisoformat(self.cooldown_data["horny_cooldown_until"])
                    remaining = cooldown_until - datetime.now()
                    status["horny_cooldown_remaining_minutes"] = max(0, int(remaining.total_seconds() / 60))
                except Exception:
                    status["horny_cooldown_remaining_minutes"] = 0
            
            self.log("Emotion status retrieved successfully", "[OK]")
            return status
            
        except Exception as e:
            self.log("Failed to get emotion status: " + str(e), "[ERROR]")
            return {
                "current_emotion": None,
                "horny_stage": 1,
                "horny_on_cooldown": False,
                "available_emotions": ["bored"],
                "initialization_success": False,
                "error": str(e)
            }
    
    def reset_horny_progression(self):
        """Reset horny progression to stage 1 and clear cooldown (for testing)"""
        try:
            self.cooldown_data["horny_stage"] = 1
            self.cooldown_data["horny_cooldown_until"] = None
            
            if self._save_cooldown_data():
                self.log("Horny progression reset to stage 1, cooldown cleared", "[OK]")
                return True
            else:
                self.log("Failed to save horny progression reset", "[FAIL]")
                return False
                
        except Exception as e:
            self.log("Horny progression reset failed: " + str(e), "[FAIL]")
            return False
    
    def force_horny_cooldown(self, minutes=None):
        """Force activate horny cooldown for testing purposes"""
        try:
            cooldown_minutes = minutes or self.config.get("horny_cooldown_minutes", 60)
            cooldown_until = datetime.now() + timedelta(minutes=cooldown_minutes)
            
            self.cooldown_data["horny_cooldown_until"] = cooldown_until.isoformat()
            
            if self._save_cooldown_data():
                self.log("Forced horny cooldown for " + str(cooldown_minutes) + " minutes", "[OK]")
                return True
            else:
                self.log("Failed to save forced cooldown", "[FAIL]")
                return False
                
        except Exception as e:
            self.log("Force cooldown failed: " + str(e), "[FAIL]")
            return False


# Factory function for easy usage
def create_emotion_manager():
    """Create and return a configured emotion manager"""
    try:
        manager = IdleEmotionManager()
        if manager.initialization_success:
            print("[EMOTION-MANAGER] [OK] Factory function completed successfully")
            return manager
        else:
            print("[EMOTION-MANAGER] [FAIL] Factory function failed during initialization")
            return None
            
    except Exception as e:
        print("[EMOTION-MANAGER] [FAIL] Factory function exception: " + str(e))
        return None


# Testing functions for diagnostics
def test_emotion_generation():
    """Test emotion generation and progression"""
    print("=== EMOTION MANAGER TEST ===")
    
    manager = create_emotion_manager()
    if not manager:
        print("[FAIL] Could not create emotion manager")
        return False
    
    try:
        # Test emotion selection
        for i in range(5):
            emotion = manager.select_emotion_type()
            message = manager.generate_emotional_message(emotion)
            print("Test " + str(i + 1) + ": " + emotion + " - " + message[:50] + "...")
            
            # Show status
            status = manager.get_emotion_status()
            print("  Status: Stage " + str(status["horny_stage"]) + 
                  ", Cooldown: " + str(status["horny_on_cooldown"]))
            print()
            
            time.sleep(1)  # Small delay between tests
        
        print("[OK] Emotion generation test completed")
        return True
        
    except Exception as e:
        print("[FAIL] Emotion generation test failed: " + str(e))
        return False


def test_horny_progression():
    """Test horny progression specifically"""
    print("=== HORNY PROGRESSION TEST ===")
    
    manager = create_emotion_manager()
    if not manager:
        print("[FAIL] Could not create emotion manager")
        return False
    
    try:
        manager.reset_horny_progression()  # Start fresh
        
        # Generate 3 horny messages to test progression
        for i in range(3):
            message = manager.generate_emotional_message("horny")
            status = manager.get_emotion_status()
            
            print("Horny test " + str(i + 1) + ":")
            print("  Message: " + message[:70] + "...")
            print("  Stage after: " + str(status["horny_stage"]))
            print("  On cooldown: " + str(status["horny_on_cooldown"]))
            
            if status["horny_on_cooldown"]:
                print("  Cooldown remaining: " + str(status.get("horny_cooldown_remaining_minutes", 0)) + " minutes")
            print()
        
        print("[OK] Horny progression test completed")
        return True
        
    except Exception as e:
        print("[FAIL] Horny progression test failed: " + str(e))
        return False


# Main execution for testing
if __name__ == "__main__":
    print("=== IDLE EMOTION MANAGER DIAGNOSTICS ===")
    
    # Run initialization test
    manager = create_emotion_manager()
    if manager:
        print("[OK] Initialization successful")
        
        # Run tests
        test_emotion_generation()
        test_horny_progression()
        
        print("[DONE] All diagnostics completed")
    else:
        print("[FAIL] Initialization failed")
        print("[FAIL] Diagnostics could not run")