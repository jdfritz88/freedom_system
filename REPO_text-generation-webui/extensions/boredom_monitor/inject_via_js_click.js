// JavaScript to inject messages by programmatically clicking "Send dummy reply" button
// This script polls for injection requests and executes them

function checkForInjectionRequest() {
    // Poll the backend for pending injection requests
    fetch('/api/v1/internal/boredom_monitor/pending_injection')
        .then(response => response.json())
        .then(data => {
            if (data.has_pending && data.message) {
                console.log('[BOREDOM-INJECT-JS] Injecting message:', data.message);

                // Find the chat input textbox using proper elem_id selector
                const chatInput = findChatInput();
                if (chatInput) {
                    // Set the value and dispatch events to notify Gradio
                    chatInput.value = data.message;
                    chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                    chatInput.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log('[BOREDOM-INJECT-JS] Set chat input value');
                } else {
                    console.error('[BOREDOM-INJECT-JS] Chat input not found!');
                }

                // Find and click the "Send dummy reply" button
                const dummyReplyBtn = findButtonByText('Send dummy reply');
                if (dummyReplyBtn) {
                    console.log('[BOREDOM-INJECT-JS] Clicking Send dummy reply button');
                    dummyReplyBtn.click();
                } else {
                    console.error('[BOREDOM-INJECT-JS] Send dummy reply button not found!');
                }
            }
        })
        .catch(err => console.error('[BOREDOM-INJECT-JS] Error:', err));
}

/**
 * Find the chat input textarea using multiple selector strategies
 * Based on text-generation-webui ui_chat.py elem_id assignments
 */
function findChatInput() {
    // Strategy 1: Direct elem_id selector (most reliable)
    const chatInputContainer = document.getElementById('chat-input');
    if (chatInputContainer) {
        const textarea = chatInputContainer.querySelector('textarea');
        if (textarea) return textarea;
    }

    // Strategy 2: Fallback selectors for different Gradio versions
    const selectors = [
        '#chat-input textarea',
        '#chat-input-container textarea',
        'textarea[data-testid="textbox"]',
        '.chat-input textarea',
        'textarea[placeholder*="Send a message"]',
        'textarea[placeholder*="message"]'
    ];

    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
            console.log('[BOREDOM-INJECT-JS] Found input via selector:', selector);
            return element;
        }
    }

    return null;
}

/**
 * Find a button by its text content
 */
function findButtonByText(text) {
    const buttons = Array.from(document.querySelectorAll('button'));
    return buttons.find(btn => btn.textContent.includes(text));
}

// Poll every 2 seconds for injection requests
setInterval(checkForInjectionRequest, 2000);
console.log('[BOREDOM-INJECT-JS] Injection polling started');
