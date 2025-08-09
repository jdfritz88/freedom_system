# AllTalk TTS Integration Standards

This document establishes standards and practices for integrating AllTalk TTS with text-generation-webui, based on successful troubleshooting and implementation patterns.

---

## 🔧 SUBPROCESS MANAGEMENT STANDARDS

### 1. Subprocess Detection Before Creation
**Rule**: Always check for existing processes before creating new ones
```python
def check_existing_alltalk():
    """Check if AllTalk is already running on expected ports"""
    import psutil
    import requests
    
    # Check process list
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'alltalk_tts' in str(proc.info.get('cmdline', [])):
            return True, proc.info['pid']
    
    # Check port availability
    try:
        response = requests.get("http://localhost:7851/api/ready", timeout=2)
        if response.status_code == 200:
            return True, "port_response"
    except:
        pass
    
    return False, None
```

### 2. Conditional Subprocess Creation
**Standard**: Only create subprocess if detection fails
- Test both process list and port response
- Log detection results clearly
- Prevent duplicate subprocess creation

### 3. Subprocess Communication Verification
**Rule**: Verify subprocess is ready before proceeding
```python
def wait_for_alltalk_ready(max_wait=30):
    """Wait for AllTalk to become ready with timeout"""
    import time
    import requests
    
    for attempt in range(max_wait):
        try:
            response = requests.get("http://localhost:7851/api/ready", timeout=2)
            if response.status_code == 200:
                return True
        except:
            time.sleep(1)
    
    return False
```

---

## 🌐 API CONNECTION STANDARDS

### 4. Smart Connection Detection with Retry Logic
**Standard**: Implement progressive retry with exponential backoff
- Initial quick check (1-2 seconds timeout)
- Progressive delays: 1s, 2s, 4s, 8s
- Maximum retry attempts: 5-10 depending on context
- Clear logging of each attempt

### 5. Port Conflict Resolution Protocol
**Rules for Port Management**:
- **Primary Port**: 7851 (AllTalk default)
- **Fallback Port**: 7852 (if 7851 occupied)
- **Detection Order**: Check 7851 first, then 7852
- **Configuration Update**: Update extension config if port changes

```python
def find_available_port(preferred_ports=[7851, 7852]):
    """Find first available port from preferred list"""
    import socket
    
    for port in preferred_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    
    return None
```

### 6. Connection Health Monitoring
**Standard**: Implement connection health checks
- Periodic health checks during operation
- Graceful degradation on connection loss
- Automatic reconnection attempts
- User notification of connection status

---

## 🛠️ ERROR HANDLING STANDARDS

### 7. Timeout Management
**Rules**:
- **Initial Connection**: 5-10 seconds maximum
- **API Calls**: 2-5 seconds per call
- **Health Checks**: 1-2 seconds
- **Always provide timeout parameters**

### 8. Graceful Error Recovery
**Standard**: Handle all connection scenarios
```python
try:
    response = requests.get(url, timeout=timeout)
    # Process successful response
except requests.exceptions.Timeout:
    # Log timeout, attempt retry or fallback
    pass
except requests.exceptions.ConnectionError:
    # Log connection error, check if service is running
    pass
except Exception as e:
    # Log unexpected error, provide user feedback
    pass
```

### 9. User-Friendly Error Messages
**Communication Standard**: Explain errors in "high school talk"
- Avoid technical jargon
- Explain what went wrong in simple terms
- Provide clear next steps
- Example: "AllTalk isn't responding. This usually means it's starting up or there's a port conflict. Waiting 10 seconds and trying again..."

---

## 🔄 INTEGRATION TESTING PRACTICES

### 10. Incremental Testing Protocol
**Standard**: Test each change individually
1. Make single change
2. Test immediately
3. Verify functionality
4. Document result before next change

### 11. Feature Preservation Testing
**Rule**: Verify all existing features after modifications
- CUDA support maintained
- All TTS voices available
- Voice quality unchanged
- Performance metrics maintained

### 12. Integration Point Testing
**Standard**: Test all communication channels
- Extension to AllTalk API
- AllTalk to audio output
- Error handling paths
- Configuration loading/saving

---

## 📦 EXTENSION DEVELOPMENT STANDARDS

### 13. Circular Import Prevention
**Rules**:
- Use conditional imports when possible
- Implement lazy loading for non-critical modules
- Clear separation of initialization and runtime code
- Document all external dependencies

```python
def lazy_import_alltalk():
    """Import AllTalk modules only when needed"""
    try:
        import alltalk_tts
        return alltalk_tts
    except ImportError as e:
        logger.warning(f"AllTalk import failed: {e}")
        return None
```

### 14. Version Compatibility Management
**Standard**: Handle version mismatches gracefully
- Check version compatibility on startup
- Provide clear version requirement messages
- Support multiple version ranges when possible
- Document minimum and maximum supported versions

### 15. Environment Isolation
**Rule**: Respect environment boundaries
- Use extension-specific configuration
- Avoid modifying global text-generation-webui settings
- Maintain separate log files for AllTalk operations
- Clean up resources on extension disable

---

## 🔧 ENVIRONMENT MANAGEMENT

### 16. Python Environment Verification
**Standard**: Verify correct environment before operations
```python
import sys
import os

def verify_environment():
    """Ensure running in correct Python environment"""
    expected_env = "text-generation-webui"  # or your expected env name
    current_env = os.path.basename(sys.prefix)
    
    if expected_env not in current_env:
        logger.warning(f"May be running in wrong environment: {current_env}")
    
    return current_env
```

### 17. Dependency Verification
**Rule**: Check all required packages before startup
- Verify AllTalk TTS installation
- Check audio output libraries
- Confirm CUDA availability if required
- Test import of all required modules

---

## 📊 LOGGING AND MONITORING STANDARDS

### 18. Comprehensive Operation Logging
**Standard**: Log all significant operations
- Subprocess creation attempts and results
- API connection attempts and responses
- Port detection and selection
- Error conditions and recovery actions
- Performance metrics (response times, etc.)

### 19. Log Format Standardization
**Rule**: Use consistent log format across all AllTalk operations
```python
import logging
import datetime

def setup_alltalk_logging():
    """Configure standardized logging for AllTalk operations"""
    formatter = logging.Formatter(
        '%(asctime)s - AllTalk-%(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler = logging.FileHandler('log/alltalk_operations.log')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('alltalk')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
```

---

## 🚀 PERFORMANCE STANDARDS

### 20. Response Time Requirements
**Standards**:
- **Initial connection**: < 10 seconds
- **TTS generation request**: < 5 seconds to start
- **Health check**: < 2 seconds
- **Configuration changes**: < 3 seconds

### 21. Resource Usage Monitoring
**Rule**: Monitor and limit resource consumption
- Track memory usage of subprocess
- Monitor CPU usage during TTS generation
- Implement resource cleanup on shutdown
- Provide resource usage feedback to user

---

## 📋 TESTING CHECKLIST

### Before Deployment
- [ ] Subprocess detection works correctly
- [ ] API connection establishes successfully
- [ ] Port conflict resolution functions
- [ ] All TTS voices available
- [ ] CUDA support functional
- [ ] Error handling tested
- [ ] Resource cleanup verified
- [ ] User interface responsive
- [ ] Logging captures all operations
- [ ] Performance meets standards

### Integration Testing Sequence
1. **Clean Environment Test**: Start with no AllTalk running
2. **Existing Process Test**: Start with AllTalk already running
3. **Port Conflict Test**: Occupy port 7851, verify fallback to 7852
4. **Connection Failure Test**: Simulate network issues
5. **Resource Exhaustion Test**: Test under high load
6. **Recovery Test**: Test recovery after service interruption

---

## 🎯 USER COMMUNICATION STANDARDS

### 22. Technical Explanation Guidelines
**Rule**: Explain technical concepts in accessible language
- Use analogies from everyday life
- Avoid acronyms and technical jargon
- Provide context for why something matters
- Break complex processes into simple steps

### 23. Status Communication
**Standard**: Keep users informed during operations
- Show progress for long-running operations
- Explain what's happening during waits
- Provide estimated time remaining
- Clear indication of success/failure

Example status messages:
- "Starting AllTalk TTS service... this usually takes 10-15 seconds"
- "Checking if AllTalk is already running on your computer..."
- "Found AllTalk running on port 7851, connecting now..."
- "AllTalk isn't responding on the usual port, trying backup port..."

---

## ⚠️ CRITICAL SUCCESS FACTORS

1. **Always detect before creating** - Prevents duplicate processes
2. **Test incrementally** - Makes debugging manageable
3. **Preserve all features** - Maintain CUDA support and voice quality
4. **Use clear timeouts** - Prevents hanging operations
5. **Implement retry logic** - Handles temporary connection issues
6. **Log everything important** - Enables troubleshooting
7. **Communicate clearly** - Users understand what's happening
8. **Clean up resources** - Prevents system resource leaks
9. **Handle all error cases** - Graceful degradation
10. **Test thoroughly** - Verify all integration points work

---

*This document should be updated based on new integration challenges and successful resolution patterns.*