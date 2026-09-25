console.log("Boredom Monitor extension script loaded");

// Auto-refresh functionality to replace gr.Timer
function setupAutoRefresh() {
    const refreshButton = document.getElementById('boredom_refresh');
    if (refreshButton) {
        // Auto-click the refresh button every 3 seconds to update the UI
        setInterval(() => {
            refreshButton.click();
        }, 3000);
        
        console.log("Auto-refresh timer set up (3 second intervals)");
    } else {
        // Retry finding the button after a delay
        setTimeout(setupAutoRefresh, 1000);
    }
}

// Auto-scroll console output to bottom when new content is added
function autoScrollConsole() {
    const consoleOutputs = document.querySelectorAll('.console-output textarea');
    consoleOutputs.forEach(textarea => {
        if (textarea) {
            textarea.scrollTop = textarea.scrollHeight;
        }
    });
}

// Enhanced console styling and behavior
function enhanceConsoleOutput() {
    const consoleOutputs = document.querySelectorAll('.console-output textarea');
    consoleOutputs.forEach(textarea => {
        if (textarea && !textarea.classList.contains('boredom-enhanced')) {
            // Mark as enhanced to avoid duplicate processing
            textarea.classList.add('boredom-enhanced');
            
            // Apply console-like styling
            textarea.style.backgroundColor = '#1e1e1e';
            textarea.style.color = '#00ff00';
            textarea.style.fontFamily = 'Consolas, "Courier New", monospace';
            textarea.style.fontSize = '12px';
            textarea.style.lineHeight = '1.4';
            textarea.style.border = '1px solid #333';
            textarea.style.borderRadius = '4px';
            textarea.style.padding = '8px';
            
            // Make it read-only with better UX
            textarea.readOnly = true;
            textarea.style.cursor = 'default';
            
            // Auto-scroll to bottom when content changes
            const observer = new MutationObserver(() => {
                textarea.scrollTop = textarea.scrollHeight;
            });
            
            observer.observe(textarea, {
                childList: true,
                subtree: true,
                characterData: true
            });
        }
    });
}

// Add manual controls for the extension
function addBoredomControls() {
    const boredomMarkdown = Array.from(document.querySelectorAll('h3')).find(h3 => 
        h3.textContent.includes('Boredom Monitor Extension')
    );
    
    if (boredomMarkdown && !document.getElementById('boredom-manual-controls')) {
        const boredomSection = boredomMarkdown.closest('div[class*="group"]') || boredomMarkdown.parentElement;
        
        const controlsDiv = document.createElement('div');
        controlsDiv.id = 'boredom-manual-controls';
        controlsDiv.style.marginTop = '10px';
        controlsDiv.style.padding = '10px';
        controlsDiv.style.border = '1px solid #444';
        controlsDiv.style.borderRadius = '4px';
        controlsDiv.style.backgroundColor = '#2a2a2a';
        
        controlsDiv.innerHTML = `
            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                <button id="trigger-idle-now" style="
                    padding: 6px 12px; 
                    background: #4a90e2; 
                    color: white; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer;
                    font-size: 12px;
                ">Trigger Idle Now</button>
                
                <button id="reset-cooldown" style="
                    padding: 6px 12px; 
                    background: #e24a4a; 
                    color: white; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer;
                    font-size: 12px;
                ">Reset Cooldown</button>
                
                <button id="clear-console" style="
                    padding: 6px 12px; 
                    background: #666; 
                    color: white; 
                    border: none; 
                    border-radius: 4px; 
                    cursor: pointer;
                    font-size: 12px;
                ">Clear Console</button>
                
                <span style="color: #888; font-size: 11px; margin-left: 10px;">
                    Manual controls for testing and debugging
                </span>
            </div>
        `;
        
        // Insert after the settings row
        const settingsRow = boredomSection.querySelector('div[class*=console.log("Boredom Monitor extension script loaded");

// Update countdown timer in HTML
function updateCountdown() {
    const countdownElement = document.getElementById('boredom-countdown');
    if (countdownElement) {
        // This would need to get data from Python backend
        // For now, just show a placeholder
        countdownElement.textContent = "Next check: calculating...";
    }
}

// Auto-refresh functionality
function setupAutoRefresh() {
    const refreshButton = document.getElementById('boredom_refresh');
    if (refreshButton) {
        // Auto-click the refresh button every 5 seconds
        setInterval(() => {
            refreshButton.click();
        }, 5000);
        
        console.log("Boredom Monitor auto-refresh set up");
    } else {
        setTimeout(setupAutoRefresh, 1000);
    }
}

// Enhanced console styling
function enhanceConsoleOutput() {
    const consoleOutputs = document.querySelectorAll('.console-output textarea');
    consoleOutputs.forEach(textarea => {
        if (textarea && !textarea.classList.contains('boredom-enhanced')) {
            textarea.classList.add('boredom-enhanced');
            
            // Compact console styling
            textarea.style.backgroundColor = '#1a1a1a';
            textarea.style.color = '#00ff00';
            textarea.style.fontFamily = 'Consolas, "Courier New", monospace';
            textarea.style.fontSize = '11px';
            textarea.style.lineHeight = '1.2';
            textarea.style.border = '1px solid #333';
            textarea.style.borderRadius = '3px';
            textarea.style.padding = '4px';
            textarea.readOnly = true;
            
            // Auto-scroll to bottom
            textarea.scrollTop = textarea.scrollHeight;
        }
    });
}

// Initialize enhancements
function initBoredomEnhancements() {
    enhanceConsoleOutput();
    setupAutoRefresh();
    updateCountdown();
}

// Run on load and DOM changes
document.addEventListener('DOMContentLoaded', initBoredomEnhancements);

const observer = new MutationObserver(() => {
    setTimeout(initBoredomEnhancements, 100);
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// Periodic check
setInterval(initBoredomEnhancements, 3000);

console.log("Boredom Monitor script ready");