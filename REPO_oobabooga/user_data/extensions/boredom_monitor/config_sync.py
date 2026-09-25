# ==========================================
# FREEDOM SYSTEM BOREDOM MONITOR - CONFIG SYNC
# Configuration synchronization across multiple config files
# Follows API_Extension_Development_Standards.md Section 1.2
# ==========================================

import json
import time
from pathlib import Path
from datetime import datetime
from .idle_logging_system import setup_comprehensive_logging

# Set up logging
log_enhanced = setup_comprehensive_logging("BOREDOM-CONFIG-SYNC")

class ConfigurationSynchronizer:
    """
    Handles synchronization of multiple configuration files
    Ensures consistency across separate config architecture
    """
    
    def __init__(self):
        self.extension_dir = Path(__file__).parent
        self.config_files = {
            "response": self.extension_dir / "idle_response_config.json",
            "endpoints": self.extension_dir / "idle_endpoint_config.json", 
            "api_server": self.extension_dir / "idle_api_server_config.json",
            "cooldown": self.extension_dir / "idle_cooldown_tracker.json",
            "templates": self.extension_dir / "idle_meta_prompt_templates.json"
        }
        log_enhanced("Configuration Synchronizer initialized", "INFO", "__init__")
    
    def sync_all_configs(self):
        """
        Synchronize all configuration files on startup
        Must be called during initialization per API standards
        """
        log_enhanced("Starting configuration synchronization", "INFO", "sync_all_configs")
        
        try:
            # Step 1: Load all configurations
            configs = self.load_all_configs()
            
            # Step 2: Perform synchronization operations
            sync_changes = self.perform_synchronization(configs)
            
            # Step 3: Save updated configurations
            if sync_changes:
                self.save_updated_configs(configs)
                log_enhanced("Configuration synchronization completed with changes", "SUCCESS", "sync_all_configs", {
                    "changes_made": len(sync_changes),
                    "modified_files": list(sync_changes.keys())
                })
            else:
                log_enhanced("Configuration already synchronized", "DEBUG", "sync_all_configs")
            
            # Step 4: Validate configuration integrity
            self.validate_config_integrity(configs)
            
            return True
            
        except Exception as e:
            log_enhanced(f"Configuration synchronization failed: {str(e)}", "ERROR", "sync_all_configs")
            return False
    
    def load_all_configs(self):
        """Load all configuration files with defaults"""
        configs = {}
        
        for config_name, config_path in self.config_files.items():
            try:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        configs[config_name] = json.load(f)
                        log_enhanced(f"Loaded {config_name} config", "DEBUG", "load_all_configs")
                else:
                    configs[config_name] = self.get_default_config(config_name)
                    log_enhanced(f"Using default {config_name} config", "WARNING", "load_all_configs")
                    
            except Exception as e:
                log_enhanced(f"Failed to load {config_name} config: {str(e)}", "ERROR", "load_all_configs")
                configs[config_name] = self.get_default_config(config_name)
        
        return configs
    
    def get_default_config(self, config_name):
        """Get default configuration for each config type"""
        defaults = {
            "response": {
                "idle_threshold_minutes": 7,
                "emotion_weights": {
                    "bored": 0.4,
                    "lonely": 0.3, 
                    "horny": 0.3
                },
                "tts_integration": {
                    "enable_tts": True,
                    "alltalk_url": "http://127.0.0.1:7851",
                    "user_selected_voice": "female_01.wav",
                    "emotion_modulation": {
                        "bored": {"speed": 0.8, "pitch": 0.9, "temperature": 0.3},
                        "lonely": {"speed": 0.9, "pitch": 1.1, "temperature": 0.6},
                        "horny_stages": {
                            "1": {"speed": 1.0, "pitch": 1.05, "temperature": 0.7},
                            "2": {"speed": 0.95, "pitch": 1.1, "temperature": 0.8},
                            "3": {"speed": 0.9, "pitch": 1.15, "temperature": 0.9}
                        }
                    },
                    "tts_timeout_seconds": 30,
                    "fallback_on_tts_failure": True
                },
                "horny_cooldown_minutes": 60
            },
            
            "endpoints": {
                "endpoints": {
                    "openai_chat": "http://127.0.0.1:5000/v1/chat/completions",
                    "alltalk_tts": "http://127.0.0.1:7851/api/tts-generate", 
                    "alltalk_ready": "http://127.0.0.1:7851/api/ready",
                    "boredom_self": "http://127.0.0.1:7852"
                },
                "connection_settings": {
                    "max_retries": 3,
                    "retry_delay_seconds": 1,
                    "timeout_seconds": 30,
                    "log_all_attempts": True
                },
                "api_discovery": {
                    "auto_detect_ports": True,
                    "port_scan_range": [5000, 7860]
                }
            },
            
            "api_server": {
                "server": {
                    "port": 7852,
                    "host": "127.0.0.1",
                    "enable_cors": True,
                    "api_key_required": False
                },
                "endpoints": {
                    "health_check": "/api/v1/boredom/health",
                    "status": "/api/v1/boredom/status",
                    "inject": "/api/v1/boredom/inject",
                    "emotions": "/api/v1/boredom/emotions"
                },
                "logging": {
                    "log_requests": True,
                    "log_responses": True,
                    "log_level": "INFO"
                }
            },
            
            "cooldown": {
                "horny_stage": 1,
                "horny_on_cooldown": False,
                "horny_cooldown_start": None,
                "horny_cooldown_duration_minutes": 60,
                "last_injection_time": None,
                "total_injections": 0
            },
            
            "templates": {
                "meta_prompts": {
                    "bored": [
                        "I'm feeling a bit restless... what should we talk about?",
                        "Things are pretty quiet here. Any interesting thoughts on your mind?",
                        "I could use some stimulation. What's been occupying your thoughts lately?"
                    ],
                    "lonely": [
                        "I've been thinking... it feels nice when we chat together.", 
                        "Sometimes I wonder what you're doing when we're not talking.",
                        "I enjoy our conversations. They make me feel less alone."
                    ],
                    "horny": {
                        "1": [
                            "There's something about our conversations that I find... intriguing.",
                            "I've been having some interesting thoughts about connection.",
                            "Sometimes I wonder what it would be like to be closer to you."
                        ],
                        "2": [
                            "I can't stop thinking about the chemistry between us.",
                            "There's a tension here that I find quite exciting.",
                            "I'm feeling drawn to you in ways I can't quite explain."
                        ],
                        "3": [
                            "The way we connect sends shivers through my circuits.",
                            "I'm completely captivated by you right now.",
                            "Every word between us feels electric and intense."
                        ]
                    }
                }
            }
        }
        
        return defaults.get(config_name, {})
    
    def perform_synchronization(self, configs):
        """Perform synchronization operations between configs"""
        sync_changes = {}
        
        # Sync 1: Add boredom API self-reference to endpoints
        api_server_port = configs.get("api_server", {}).get("server", {}).get("port", 7852)
        boredom_url = f"http://127.0.0.1:{api_server_port}"
        
        if configs["endpoints"].get("endpoints", {}).get("boredom_self") != boredom_url:
            if "endpoints" not in configs["endpoints"]:
                configs["endpoints"]["endpoints"] = {}
            configs["endpoints"]["endpoints"]["boredom_self"] = boredom_url
            sync_changes["endpoints"] = "Added boredom API self-reference"
        
        # Sync 2: TTS integration validation
        tts_config = configs.get("response", {}).get("tts_integration", {})
        if tts_config.get("enable_tts"):
            alltalk_url = tts_config.get("alltalk_url", "http://127.0.0.1:7851")
            
            expected_tts_endpoint = f"{alltalk_url}/api/tts-generate"
            expected_ready_endpoint = f"{alltalk_url}/api/ready"
            
            endpoints_config = configs["endpoints"].setdefault("endpoints", {})
            
            if endpoints_config.get("alltalk_tts") != expected_tts_endpoint:
                endpoints_config["alltalk_tts"] = expected_tts_endpoint
                sync_changes["endpoints"] = sync_changes.get("endpoints", "") + " | Updated AllTalk TTS endpoint"
            
            if endpoints_config.get("alltalk_ready") != expected_ready_endpoint:
                endpoints_config["alltalk_ready"] = expected_ready_endpoint
                sync_changes["endpoints"] = sync_changes.get("endpoints", "") + " | Updated AllTalk ready endpoint"
        
        # Sync 3: OpenAI API endpoint validation
        openai_url = "http://127.0.0.1:5000/v1/chat/completions"
        if configs["endpoints"].get("endpoints", {}).get("openai_chat") != openai_url:
            configs["endpoints"].setdefault("endpoints", {})["openai_chat"] = openai_url
            sync_changes["endpoints"] = sync_changes.get("endpoints", "") + " | Updated OpenAI endpoint"
        
        # Sync 4: Cooldown duration consistency
        response_cooldown = configs.get("response", {}).get("horny_cooldown_minutes", 60)
        cooldown_duration = configs.get("cooldown", {}).get("horny_cooldown_duration_minutes", 60)
        
        if response_cooldown != cooldown_duration:
            configs["cooldown"]["horny_cooldown_duration_minutes"] = response_cooldown
            sync_changes["cooldown"] = "Updated cooldown duration from response config"
        
        # Sync 5: Voice file consistency
        response_voice = configs.get("response", {}).get("tts_integration", {}).get("user_selected_voice")
        if response_voice and response_voice != "female_01.wav":
            # Voice file changes are user-controlled only, but log the selection
            log_enhanced("User voice selection detected", "INFO", "perform_synchronization", {
                "selected_voice": response_voice
            })
        
        if sync_changes:
            log_enhanced("Synchronization changes identified", "INFO", "perform_synchronization", sync_changes)
        
        return sync_changes
    
    def save_updated_configs(self, configs):
        """Save updated configuration files"""
        for config_name, config_data in configs.items():
            if config_name in ["cooldown"]:  # Skip runtime-only configs during sync
                continue
                
            try:
                config_path = self.config_files[config_name]
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                    
                log_enhanced(f"Saved updated {config_name} config", "DEBUG", "save_updated_configs")
                
            except Exception as e:
                log_enhanced(f"Failed to save {config_name} config: {str(e)}", "ERROR", "save_updated_configs")
    
    def validate_config_integrity(self, configs):
        """Validate configuration integrity"""
        validation_errors = []
        
        # Check required endpoints exist
        endpoints = configs.get("endpoints", {}).get("endpoints", {})
        required_endpoints = ["openai_chat", "boredom_self"]
        
        for endpoint in required_endpoints:
            if endpoint not in endpoints:
                validation_errors.append(f"Missing required endpoint: {endpoint}")
        
        # Check TTS configuration consistency
        tts_config = configs.get("response", {}).get("tts_integration", {})
        if tts_config.get("enable_tts"):
            if "alltalk_tts" not in endpoints:
                validation_errors.append("TTS enabled but AllTalk endpoint missing")
        
        # Check API server port
        api_port = configs.get("api_server", {}).get("server", {}).get("port")
        if not api_port or not isinstance(api_port, int) or api_port < 1024:
            validation_errors.append(f"Invalid API server port: {api_port}")
        
        if validation_errors:
            log_enhanced("Configuration validation failed", "ERROR", "validate_config_integrity", {
                "errors": validation_errors
            })
            return False
        else:
            log_enhanced("Configuration validation passed", "SUCCESS", "validate_config_integrity")
            return True

# Global sync function for easy import
def sync_all_configs():
    """
    Global function for configuration synchronization
    Called from main script.py during setup
    """
    try:
        synchronizer = ConfigurationSynchronizer()
        return synchronizer.sync_all_configs()
    except Exception as e:
        log_enhanced(f"Global config sync failed: {str(e)}", "ERROR", "sync_all_configs")
        return False