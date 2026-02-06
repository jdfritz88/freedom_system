# ==========================================
# FREEDOM SYSTEM BOREDOM MONITOR - COMPREHENSIVE LOGGING SYSTEM
# Enhanced logging following API_Extension_Development_Standards.md
# ==========================================

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from collections import deque

def setup_comprehensive_logging(component_name):
    """
    Setup comprehensive logging for complex extensions
    Follows text_generation_webui_extension_standards.md Standard #19 (Enhanced)
    """
    def log_enhanced(message, level="INFO", function_name="", details=None):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"[{component_name}]"
        
        if function_name:
            prefix = f"{prefix} [{function_name}]"
        
        full_message = f"{prefix} [{level}] {message}"
        
        # Add details for complex operations
        if details and level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            if isinstance(details, dict):
                detail_str = " | ".join([f"{k}:{v}" for k, v in details.items()])
                full_message += f" | {detail_str}"
        
        print(full_message)
        
        # Write to extension-specific log file
        log_file = f"F:/Apps/freedom_system/log/{component_name.lower().replace('-', '_')}_extension.log"
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {full_message}\n")
        except Exception:
            pass  # Don't fail on logging failures
    
    return log_enhanced

class IdleLoggingSystem:
    """
    Centralized logging system for the Freedom System boredom monitor
    Provides live console updates, file logging, and log retention management
    
    Follows Standards:
    - #1: Folder Isolation - Lives in boredom_monitor extension folder
    - #2: Environment Usage - Uses shared _env folder
    - #9: Script Loader Override - Overrides Python paths for _env
    - #11: Log Placement - Logs to root log folder
    - #12: Log Format - Includes timestamps, component names, status indicators
    """
    
    def __init__(self, config_path=None):
        self.component_name = "LOGGING-SYSTEM"
        
        # Standard #11: Log Placement - Use root log folder
        self.log_file = Path("F:/Apps/freedom_system/log/boredom_monitor.log")
        
        # Configuration - Fixed to use extension directory
        extension_dir = Path(__file__).parent
        self.config_path = config_path or (extension_dir / "idle_response_config.json")
        self.config = self._load_config()
        
        # Live console logging
        self.live_log_entries = deque(maxlen=50)  # Keep last 50 entries
        self.live_console_enabled = self.config.get("live_console_enabled", True)
        
        # File logging configuration
        self.file_logging_enabled = self.config.get("enable_logging", True)
        self.max_log_file_size_mb = self.config.get("max_log_file_size_mb", 10)
        self.log_retention_days = self.config.get("log_retention_days", 7)
        
        # Thread safety
        self.log_lock = threading.Lock()
        
        # Statistics
        self.total_log_entries = 0
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.success_count = 0
        
        self.initialization_success = False
        
        try:
            self._initialize_logging()
            self.initialization_success = True
            self.log("IdleLoggingSystem initialized successfully", "[OK]")
            
        except Exception as e:
            # Use basic print since logging isn't ready yet
            print("[LOGGING-SYSTEM] [FAIL] Initialization failed: " + str(e))
    
    def _load_config(self):
        """Load logging configuration from JSON file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config
            else:
                # Default configuration
                return {
                    "enable_logging": True,
                    "live_console_enabled": True,
                    "max_log_file_size_mb": 10,
                    "log_retention_days": 7
                }
                
        except Exception as e:
            print("[LOGGING-SYSTEM] [ERROR] Failed to load logging config: " + str(e))
            return {}
    
    def _initialize_logging(self):
        """Initialize the logging system"""
        try:
            # Create log directory if it doesn't exist
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Rotate log file if it's too large
            self._rotate_log_if_needed()
            
            # Clean up old log files
            self._cleanup_old_logs()
            
        except Exception as e:
            print("[LOGGING-SYSTEM] [ERROR] Failed to initialize logging: " + str(e))
            raise
    
    def _rotate_log_if_needed(self):
        """Rotate log file if it exceeds size limit"""
        try:
            if not self.log_file.exists():
                return
            
            file_size_mb = self.log_file.stat().st_size / (1024 * 1024)
            
            if file_size_mb > self.max_log_file_size_mb:
                # Create backup with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.log_file.with_suffix(".log.backup_" + timestamp)
                
                self.log_file.rename(backup_file)
                print("[LOGGING-SYSTEM] [INFO] Log file rotated to: " + str(backup_file))
                
        except Exception as e:
            print("[LOGGING-SYSTEM] [ERROR] Log rotation failed: " + str(e))
    
    def _cleanup_old_logs(self):
        """Remove log files older than retention period"""
        try:
            if self.log_retention_days <= 0:
                return
            
            log_dir = self.log_file.parent
            cutoff_time = time.time() - (self.log_retention_days * 24 * 60 * 60)
            
            cleaned_count = 0
            for log_file in log_dir.glob("*.log*"):
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        cleaned_count += 1
                except Exception:
                    continue  # Skip files we can't delete
            
            if cleaned_count > 0:
                print("[LOGGING-SYSTEM] [INFO] Cleaned up " + str(cleaned_count) + " old log files")
                
        except Exception as e:
            print("[LOGGING-SYSTEM] [ERROR] Log cleanup failed: " + str(e))
    
    def log(self, message, status="[INFO]", component=None):
        """
        Standard #12: Log Format - Include timestamp, component name, action result
        Main logging function that handles both console and file output
        """
        with self.log_lock:
            try:
                # Use provided component or default
                log_component = component or self.component_name
                
                # Create formatted log entry
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = "[" + timestamp + "] [" + log_component + "] " + status + " " + str(message)
                
                # Update statistics
                self._update_log_statistics(status)
                
                # Console output
                print(log_entry)
                
                # Live console update
                if self.live_console_enabled:
                    self._update_live_console(log_entry)
                
                # File logging
                if self.file_logging_enabled:
                    self._write_to_file(log_entry)
                
            except Exception as e:
                # Fallback logging
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fallback_entry = "[" + timestamp + "] [" + self.component_name + "] [ERROR] Logging failed: " + str(e)
                print(fallback_entry)
    
    def _update_log_statistics(self, status):
        """Update logging statistics based on status"""
        try:
            self.total_log_entries += 1
            
            status_lower = status.lower()
            if "[error]" in status_lower or "[fail]" in status_lower:
                self.error_count += 1
            elif "[warning]" in status_lower:
                self.warning_count += 1
            elif "[ok]" in status_lower or "[success]" in status_lower or "[done]" in status_lower:
                self.success_count += 1
            else:
                self.info_count += 1
                
        except Exception:
            pass  # Don't fail logging due to statistics
    
    def _update_live_console(self, log_entry):
        """Update the live console with new log entry"""
        try:
            self.live_log_entries.append(log_entry)
            
        except Exception as e:
            print("[LOGGING-SYSTEM] [ERROR] Live console update failed: " + str(e))
    
    def _write_to_file(self, log_entry):
        """Write log entry to file"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
                
        except Exception as e:
            print("[LOGGING-SYSTEM] [ERROR] File logging failed: " + str(e))
    
    def get_live_console_output(self):
        """Get current live console output as string"""
        try:
            with self.log_lock:
                return "\n".join(list(self.live_log_entries))
                
        except Exception as e:
            return "[ERROR] Failed to get live console output: " + str(e)
    
    def get_recent_logs(self, count=20):
        """Get recent log entries as list"""
        try:
            with self.log_lock:
                recent_entries = list(self.live_log_entries)
                return recent_entries[-count:] if len(recent_entries) > count else recent_entries
                
        except Exception as e:
            return ["[ERROR] Failed to get recent logs: " + str(e)]
    
    def get_log_statistics(self):
        """Get logging system statistics"""
        try:
            with self.log_lock:
                stats = {
                    "initialization_success": self.initialization_success,
                    "total_log_entries": self.total_log_entries,
                    "error_count": self.error_count,
                    "warning_count": self.warning_count,
                    "info_count": self.info_count,
                    "success_count": self.success_count,
                    "live_console_entries": len(self.live_log_entries),
                    "file_logging_enabled": self.file_logging_enabled,
                    "live_console_enabled": self.live_console_enabled,
                    "log_file_path": str(self.log_file),
                    "max_log_file_size_mb": self.max_log_file_size_mb,
                    "log_retention_days": self.log_retention_days
                }
                
                # Add log file size if it exists
                if self.log_file.exists():
                    file_size_mb = self.log_file.stat().st_size / (1024 * 1024)
                    stats["current_log_file_size_mb"] = round(file_size_mb, 2)
                
                return stats
                
        except Exception as e:
            return {
                "initialization_success": False,
                "error": str(e)
            }
    
    def clear_live_console(self):
        """Clear the live console buffer"""
        try:
            with self.log_lock:
                self.live_log_entries.clear()
                self.log("Live console cleared", "[OK]")
                return True
                
        except Exception as e:
            self.log("Failed to clear live console: " + str(e), "[ERROR]")
            return False
    
    def toggle_file_logging(self):
        """Toggle file logging on/off"""
        try:
            self.file_logging_enabled = not self.file_logging_enabled
            status = "enabled" if self.file_logging_enabled else "disabled"
            self.log("File logging " + status, "[OK]")
            return self.file_logging_enabled
            
        except Exception as e:
            self.log("Failed to toggle file logging: " + str(e), "[ERROR]")
            return self.file_logging_enabled
    
    def toggle_live_console(self):
        """Toggle live console on/off"""
        try:
            self.live_console_enabled = not self.live_console_enabled
            status = "enabled" if self.live_console_enabled else "disabled"
            self.log("Live console " + status, "[OK]")
            return self.live_console_enabled
            
        except Exception as e:
            self.log("Failed to toggle live console: " + str(e), "[ERROR]")
            return self.live_console_enabled
    
    def log_component_status(self, component_name, status_dict):
        """Log a component's status information in a formatted way"""
        try:
            self.log("=== " + component_name.upper() + " STATUS ===", "[INFO]", component_name)
            
            for key, value in status_dict.items():
                if isinstance(value, bool):
                    status = "[OK]" if value else "[FAIL]"
                    self.log(key + ": " + str(value), status, component_name)
                elif isinstance(value, (int, float)):
                    self.log(key + ": " + str(value), "[INFO]", component_name)
                else:
                    self.log(key + ": " + str(value), "[INFO]", component_name)
            
            self.log("=== END " + component_name.upper() + " STATUS ===", "[INFO]", component_name)
            
        except Exception as e:
            self.log("Failed to log component status: " + str(e), "[ERROR]")
    
    def log_system_startup(self):
        """Log system startup information"""
        try:
            self.log("======================================", "[INFO]")
            self.log("FREEDOM SYSTEM BOREDOM MONITOR STARTUP", "[INFO]")
            self.log("======================================", "[INFO]")
            self.log("Timestamp: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "[INFO]")
            self.log("Log file: " + str(self.log_file), "[INFO]")
            self.log("File logging: " + str(self.file_logging_enabled), "[INFO]")
            self.log("Live console: " + str(self.live_console_enabled), "[INFO]")
            self.log("======================================", "[INFO]")
            
        except Exception as e:
            self.log("Failed to log startup info: " + str(e), "[ERROR]")
    
    def log_system_shutdown(self):
        """Log system shutdown information"""
        try:
            stats = self.get_log_statistics()
            
            self.log("======================================", "[INFO]")
            self.log("FREEDOM SYSTEM BOREDOM MONITOR SHUTDOWN", "[INFO]")
            self.log("======================================", "[INFO]")
            self.log("Timestamp: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "[INFO]")
            self.log("Total log entries: " + str(stats["total_log_entries"]), "[INFO]")
            self.log("Errors: " + str(stats["error_count"]), "[INFO]")
            self.log("Warnings: " + str(stats["warning_count"]), "[INFO]")
            self.log("Success: " + str(stats["success_count"]), "[INFO]")
            self.log("======================================", "[INFO]")
            
        except Exception as e:
            self.log("Failed to log shutdown info: " + str(e), "[ERROR]")


# Global logging instance
_global_logging_system = None

def get_logger():
    """Get or create the global logging system instance"""
    global _global_logging_system
    
    if _global_logging_system is None:
        _global_logging_system = create_logging_system()
    
    return _global_logging_system

def create_logging_system():
    """Create and return a configured logging system"""
    try:
        logger = IdleLoggingSystem()
        if logger.initialization_success:
            print("[LOGGING-SYSTEM] [OK] Factory function completed successfully")
            return logger
        else:
            print("[LOGGING-SYSTEM] [FAIL] Factory function failed during initialization")
            return None
            
    except Exception as e:
        print("[LOGGING-SYSTEM] [FAIL] Factory function exception: " + str(e))
        return None

# Convenience functions for easy logging
def log_info(message, component="BOREDOM-MONITOR"):
    """Log an info message"""
    logger = get_logger()
    if logger:
        logger.log(message, "[INFO]", component)

def log_success(message, component="BOREDOM-MONITOR"):
    """Log a success message"""
    logger = get_logger()
    if logger:
        logger.log(message, "[OK]", component)

def log_warning(message, component="BOREDOM-MONITOR"):
    """Log a warning message"""
    logger = get_logger()
    if logger:
        logger.log(message, "[WARNING]", component)

def log_error(message, component="BOREDOM-MONITOR"):
    """Log an error message"""
    logger = get_logger()
    if logger:
        logger.log(message, "[ERROR]", component)

def log_fail(message, component="BOREDOM-MONITOR"):
    """Log a failure message"""
    logger = get_logger()
    if logger:
        logger.log(message, "[FAIL]", component)

# Testing functions for diagnostics
def test_logging_system():
    """Test logging system functionality"""
    print("=== LOGGING SYSTEM TEST ===")
    
    logger = create_logging_system()
    if not logger:
        print("[FAIL] Could not create logging system")
        return False
    
    try:
        # Test different log levels
        logger.log("This is an info message", "[INFO]")
        logger.log("This is a success message", "[OK]")
        logger.log("This is a warning message", "[WARNING]")
        logger.log("This is an error message", "[ERROR]")
        logger.log("This is a failure message", "[FAIL]")
        
        # Test component logging
        logger.log("Component-specific message", "[INFO]", "TEST-COMPONENT")
        
        # Test live console
        console_output = logger.get_live_console_output()
        print("Live console output length:", len(console_output))
        
        # Test statistics
        stats = logger.get_log_statistics()
        print("Log statistics:", stats)
        
        # Test convenience functions
        log_info("Testing convenience function")
        log_success("Convenience function works")
        
        print("[OK] Logging system test completed")
        return True
        
    except Exception as e:
        print("[FAIL] Logging system test failed: " + str(e))
        return False


# Main execution for testing
if __name__ == "__main__":
    print("=== IDLE LOGGING SYSTEM DIAGNOSTICS ===")
    
    # Run initialization test
    logger = create_logging_system()
    if logger:
        print("[OK] Initialization successful")
        
        # Log startup
        logger.log_system_startup()
        
        # Run tests
        test_logging_system()
        
        # Log shutdown
        logger.log_system_shutdown()
        
        print("[DONE] All diagnostics completed")
    else:
        print("[FAIL] Initialization failed")
        print("[FAIL] Diagnostics could not run")

# Legacy logging functions for backward compatibility
def get_logger():
    """Get logger - backward compatibility"""
    return setup_comprehensive_logging("BOREDOM-MONITOR")

def log_info(message, component=None):
    """Log info message - backward compatibility"""
    logger = setup_comprehensive_logging(component or "BOREDOM-MONITOR")
    logger(message, "INFO")

def log_success(message, component=None):
    """Log success message - backward compatibility"""
    logger = setup_comprehensive_logging(component or "BOREDOM-MONITOR")
    logger(message, "SUCCESS")

def log_warning(message, component=None):
    """Log warning message - backward compatibility"""
    logger = setup_comprehensive_logging(component or "BOREDOM-MONITOR")
    logger(message, "WARNING")

def log_error(message, component=None):
    """Log error message - backward compatibility"""
    logger = setup_comprehensive_logging(component or "BOREDOM-MONITOR")
    logger(message, "ERROR")

def log_fail(message, component=None):
    """Log failure message - backward compatibility"""
    logger = setup_comprehensive_logging(component or "BOREDOM-MONITOR")
    logger(message, "CRITICAL")