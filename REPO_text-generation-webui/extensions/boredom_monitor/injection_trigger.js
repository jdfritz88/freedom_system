// JavaScript to trigger the hidden injection button when background threads queue messages
// This is the bridge between background Python threads and Gradio's event system

let lastQueueSize = 0;

function checkForPendingInjections() {
    // Poll the backend to check if there are pending injections
    fetch('/api/v1/internal/boredom_monitor/queue_status')
        .then(response => response.json())
        .then(data => {
            if (data.queue_size > 0 && data.queue_size !== lastQueueSize) {
                lastQueueSize = data.queue_size;
                console.log(`[BOREDOM-INJECT] ${data.queue_size} message(s) pending - triggering injection`);

                // Find and click the hidden injection button
                const injectBtn = document.getElementById('boredom_inject_hidden_btn');
                if (injectBtn) {
                    injectBtn.click();
                    console.log('[BOREDOM-INJECT] Clicked hidden injection button');
                } else {
                    console.error('[BOREDOM-INJECT] Hidden injection button not found!');
                }
            }
        })
        .catch(err => {
            // Silently handle errors to avoid console spam
            if (err.message && !err.message.includes('Failed to fetch')) {
                console.error('[BOREDOM-INJECT] Error:', err);
            }
        });
}

// Poll every 1 second for pending injections
setInterval(checkForPendingInjections, 1000);
console.log('[BOREDOM-INJECT] Injection polling started (1s interval)');
