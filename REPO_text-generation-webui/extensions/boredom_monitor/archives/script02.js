// ==========================================
// FREEDOM SYSTEM INSTALLER - ENFORCED MODE
// Follows Freedom_Installer_Coding_Standards.txt
// ==========================================

// Freedom System Idle Boredom Extension - Frontend Controls
let freedomBoredomInterval = null;
let lastStatusUpdate = 0;
let isMonitoring = false;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('INFO: Freedom Boredom System frontend initialized');
    initializeBoredomControls();
    startStatusUpdates();
});

function initializeBoredomControls() {
    // Add event listeners to existing controls
    const enableCheckbox = document.getElementById('freedom_boredom_enabled');
    const monitorToggle = document.getElementById('freedom_monitor_toggle');
    const configForm = document.getElementById('freedom_config_form');
    
    if (enableCheckbox) {
        enableCheckbox.addEventListener('change', handleEnableToggle);
    }
    
    if (monitorToggle) {
        monitorToggle.addEventListener('click', handleMonitorToggle);
    }
    
    if (configForm) {
        configForm.addEventListener('submit', handleConfigSubmit);
    }
    
    // Initialize template management
    initializeTemplateControls();
    
    // Initialize endpoint testing
    initializeEndpointControls();
}

function handleEnableToggle(event) {
    const enabled = event.target.checked;
    console.log('INFO: Boredom system ' + (enabled ? 'enabled' : 'disabled'));
    
    // Send update to backend
    fetch('/api/extension/freedom_boredom/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            enabled: enabled
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('SUCCESS: Configuration updated');
        updateStatusDisplay();
    })
    .catch(error => {
        console.log('ERROR: Failed to update configuration - ' + error.message);
    });
}

function handleMonitorToggle(event) {
    event.preventDefault();
    
    const action = isMonitoring ? 'stop' : 'start';
    
    fetch('/api/extension/freedom_boredom/monitor/' + action, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            isMonitoring = !isMonitoring;
            updateMonitorButton();
            console.log('SUCCESS: Monitor ' + action + 'ed');
        } else {
            console.log('ERROR: Failed to ' + action + ' monitor');
        }
    })
    .catch(error => {
        console.log('ERROR: Monitor toggle failed - ' + error.message);
    });
}

function handleConfigSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const config = {};
    
    // Convert form data to config object
    for (let [key, value] of formData.entries()) {
        if (key.includes('minutes') || key.includes('hour')) {
            config[key] = parseInt(value) || 0;
        } else if (key.includes('enabled')) {
            config[key] = value === 'true' || value === 'on';
        } else {
            config[key] = value;
        }
    }
    
    // Send configuration update
    fetch('/api/extension/freedom_boredom/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('SUCCESS: Configuration saved');
            showNotification('Configuration updated successfully', 'success');
            updateStatusDisplay();
        } else {
            console.log('ERROR: Failed to save configuration');
            showNotification('Failed to save configuration', 'error');
        }
    })
    .catch(error => {
        console.log('ERROR: Configuration save failed - ' + error.message);
        showNotification('Configuration save failed', 'error');
    });
}

function initializeTemplateControls() {
    const addButton = document.getElementById('add_template_btn');
    const removeButton = document.getElementById('remove_template_btn');
    const templateInput = document.getElementById('new_template_input');
    const templateSelect = document.getElementById('template_select');
    
    if (addButton && templateInput) {
        addButton.addEventListener('click', function() {
            const template = templateInput.value.trim();
            if (template) {
                addTemplate(template);
                templateInput.value = '';
            }
        });
    }
    
    if (removeButton && templateSelect) {
        removeButton.addEventListener('click', function() {
            const template = templateSelect.value;
            if (template) {
                removeTemplate(template);
            }
        });
    }
}

function addTemplate(template) {
    fetch('/api/extension/freedom_boredom/template/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            template: template
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('SUCCESS: Template added');
            refreshTemplateList();
            showNotification('Template added successfully', 'success');
        } else {
            console.log('ERROR: Failed to add template');
            showNotification('Failed to add template', 'error');
        }
    })
    .catch(error => {
        console.log('ERROR: Template add failed - ' + error.message);
        showNotification('Template add failed', 'error');
    });
}

function removeTemplate(template) {
    fetch('/api/extension/freedom_boredom/template/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            template: template
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('SUCCESS: Template removed');
            refreshTemplateList();
            showNotification('Template removed successfully', 'success');
        } else {
            console.log('ERROR: Failed to remove template');
            showNotification('Failed to remove template', 'error');
        }
    })
    .catch(error => {
        console.log('ERROR: Template remove failed - ' + error.message);
        showNotification('Template remove failed', 'error');
    });
}

function refreshTemplateList() {
    fetch('/api/extension/freedom_boredom/templates')
    .then(response => response.json())
    .then(data => {
        const templateSelect = document.getElementById('template_select');
        if (templateSelect && data.templates) {
            templateSelect.innerHTML = '';
            data.templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template;
                option.textContent = template;
                templateSelect.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.log('ERROR: Failed to refresh template list - ' + error.message);
    });
}

function initializeEndpointControls() {
    const testButton = document.getElementById('test_endpoints_btn');
    const resetButton = document.getElementById('reset_tracker_btn');
    
    if (testButton) {
        testButton.addEventListener('click', testEndpoints);
    }
    
    if (resetButton) {
        resetButton.addEventListener('click', resetTracker);
    }
}

function testEndpoints() {
    const testButton = document.getElementById('test_endpoints_btn');
    const resultsDiv = document.getElementById('endpoint_test_results');
    
    if (testButton) {
        testButton.disabled = true;
        testButton.textContent = 'Testing...';
    }
    
    fetch('/api/extension/freedom_boredom/test_endpoints')
    .then(response => response.json())
    .then(data => {
        if (resultsDiv) {
            let html = '<h4>Endpoint Test Results:</h4>';
            
            for (let endpoint in data.results) {
                const result = data.results[endpoint];
                const status = result.status;
                const statusClass = status === 'online' ? 'success' : 
                                  status === 'disabled' ? 'warning' : 'error';
                
                html += '<div class="endpoint-result ' + statusClass + '">';
                html += '<strong>' + endpoint + ':</strong> ' + status.toUpperCase();
                if (result.code) {
                    html += ' (HTTP ' + result.code + ')';
                }
                if (result.error) {
                    html += '<br><small>' + result.error + '</small>';
                }
                html += '</div>';
            }
            
            resultsDiv.innerHTML = html;
        }
        
        console.log('SUCCESS: Endpoint test completed');
    })
    .catch(error => {
        console.log('ERROR: Endpoint test failed - ' + error.message);
        if (resultsDiv) {
            resultsDiv.innerHTML = '<div class="error">Test failed: ' + error.message + '</div>';
        }
    })
    .finally(() => {
        if (testButton) {
            testButton.disabled = false;
            testButton.textContent = 'Test Endpoints';
        }
    });
}

function resetTracker() {
    if (confirm('Are you sure you want to reset the activity tracker? This will clear cooldowns and response counters.')) {
        fetch('/api/extension/freedom_boredom/reset_tracker', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('SUCCESS: Tracker reset');
                showNotification('Activity tracker reset successfully', 'success');
                updateStatusDisplay();
            } else {
                console.log('ERROR: Failed to reset tracker');
                showNotification('Failed to reset tracker', 'error');
            }
        })
        .catch(error => {
            console.log('ERROR: Tracker reset failed - ' + error.message);
            showNotification('Tracker reset failed', 'error');
        });
    }
}

function startStatusUpdates() {
    // Update status every 30 seconds
    if (freedomBoredomInterval) {
        clearInterval(freedomBoredomInterval);
    }
    
    freedomBoredomInterval = setInterval(updateStatusDisplay, 30000);
    
    // Initial update
    updateStatusDisplay();
}

function updateStatusDisplay() {
    fetch('/api/extension/freedom_boredom/status')
    .then(response => response.json())
    .then(data => {
        updateStatusElements(data.status);
        isMonitoring = data.status.running;
        updateMonitorButton();
        lastStatusUpdate = Date.now();
    })
    .catch(error => {
        console.log('ERROR: Status update failed - ' + error.message);
    });
}

function updateStatusElements(status) {
    // Update status indicators
    const elements = {
        'status_running': status.running ? 'Running' : 'Stopped',
        'status_enabled': status.enabled ? 'Enabled' : 'Disabled',
        'status_idle_time': Math.floor(status.idle_seconds / 60) + ' minutes',
        'status_cooldown': status.cooldown_active ? 'Active' : 'Inactive',
        'status_hourly_count': status.responses_this_hour + '/hour',
        'status_can_trigger': status.can_trigger ? 'Ready' : 'Not Ready',
        'status_bridge': status.bridge_enabled ? 'Enabled' : 'Disabled',
        'status_dual_injection': status.dual_injection ? 'Enabled' : 'Disabled'
    };
    
    for (let id in elements) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
            
            // Add status classes
            element.className = 'status-value';
            if (id === 'status_running') {
                element.classList.add(status.running ? 'status-good' : 'status-bad');
            } else if (id === 'status_can_trigger') {
                element.classList.add(status.can_trigger ? 'status-good' : 'status-warning');
            } else if (id === 'status_cooldown') {
                element.classList.add(status.cooldown_active ? 'status-warning' : 'status-good');
            }
        }
    }
}

function updateMonitorButton() {
    const button = document.getElementById('freedom_monitor_toggle');
    if (button) {
        button.textContent = isMonitoring ? 'Stop Monitoring' : 'Start Monitoring';
        button.className = 'btn ' + (isMonitoring ? 'btn-warning' : 'btn-success');
    }
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'freedom-notification freedom-' + type;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Activity tracking - update activity when user interacts
function trackUserActivity() {
    fetch('/api/extension/freedom_boredom/activity', {
        method: 'POST'
    })
    .catch(error => {
        console.log('WARNING: Activity tracking failed - ' + error.message);
    });
}

// Track various user activities
document.addEventListener('click', trackUserActivity);
document.addEventListener('keypress', trackUserActivity);
document.addEventListener('scroll', trackUserActivity);

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (freedomBoredomInterval) {
        clearInterval(freedomBoredomInterval);
    }
});

console.log('INFO: Freedom Boredom System frontend controls loaded');