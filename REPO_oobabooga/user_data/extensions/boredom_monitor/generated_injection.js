
// Gradio Shadow DOM Injection Function
function injectGradioChat(message) {
    console.log('[Boredom Monitor] Attempting Shadow DOM injection...');

    // Find the Gradio app element
    const gradioApp = document.getElementsByTagName('gradio-app')[0];
    if (!gradioApp) {
        console.error('[Boredom Monitor] gradio-app element not found');
        return false;
    }

    if (!gradioApp.shadowRoot) {
        console.error('[Boredom Monitor] Shadow Root not accessible');
        return false;
    }

    // Try multiple selector strategies
    const selectors = [
        'textarea',
        '#chatbot textarea',
        '.chat-input textarea',
        'textarea[placeholder*="Send"]',
        'textarea[data-testid="textbox"]'
    ];

    for (let selector of selectors) {
        const input = gradioApp.shadowRoot.querySelector(selector);
        if (input) {
            console.log('[Boredom Monitor] Found input:', selector);

            // Set the value
            input.value = message;

            // Trigger input event
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));

            // Find and click submit button
            const submitSelectors = [
                'button[type="submit"]',
                'button.primary',
                'button:has(svg)',
                'button[aria-label*="Send"]'
            ];

            for (let btnSelector of submitSelectors) {
                const submitBtn = gradioApp.shadowRoot.querySelector(btnSelector);
                if (submitBtn) {
                    console.log('[Boredom Monitor] Clicking submit button');
                    setTimeout(() => submitBtn.click(), 100);
                    return true;
                }
            }
        }
    }

    console.error('[Boredom Monitor] No suitable input found');
    return false;
}

// Execute injection
injectGradioChat("Sequential Test #5 - Method 5: JavaScript DOM");
