/**
 * Browser-Side Verification for Injection Tests
 * ==============================================
 * This JavaScript runs in the user's browser and reports back to the server
 * when test messages are detected in the chat UI.
 *
 * How it works:
 * 1. MutationObserver watches #chat for new .message-body elements
 * 2. When a message containing [INJECTION-TEST] is found, it reports to the server
 * 3. Server receives confirmation that the browser actually shows the message
 */

(function() {
    'use strict';

    // Configuration
    const TEST_MESSAGE_PREFIX = '[INJECTION-TEST]';
    const CALLBACK_ENDPOINT = '/api/v1/internal/boredom_monitor/browser_verification';
    const VERIFICATION_LOG_ID = 'browser-verification-log';

    // Track already-reported messages to avoid duplicates
    const reportedMessages = new Set();

    /**
     * Log to console and optionally to a debug element
     */
    function logVerification(message, level = 'INFO') {
        const timestamp = new Date().toISOString().substr(11, 12);
        console.log(`[BROWSER-VERIFY] [${level}] ${timestamp} ${message}`);
    }

    /**
     * Report a found message back to the server
     */
    async function reportMessageFound(messageText, elementInfo) {
        // Create a hash to track this specific message
        const messageHash = messageText.substring(0, 100);

        if (reportedMessages.has(messageHash)) {
            logVerification(`Already reported: ${messageHash}`, 'DEBUG');
            return;
        }

        reportedMessages.add(messageHash);

        const payload = {
            found: true,
            message_text: messageText,
            element_info: elementInfo,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            chat_element_exists: !!document.getElementById('chat'),
            message_count: document.querySelectorAll('#chat .message-body').length
        };

        logVerification(`Reporting message found: ${messageText.substring(0, 50)}...`);

        try {
            const response = await fetch(CALLBACK_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                logVerification('Successfully reported to server', 'SUCCESS');
            } else {
                logVerification(`Server returned ${response.status}`, 'WARNING');
            }
        } catch (error) {
            logVerification(`Failed to report: ${error.message}`, 'ERROR');
        }
    }

    /**
     * Check a single element for test messages
     */
    function checkElementForTestMessage(element) {
        const text = element.textContent || element.innerText || '';

        if (text.includes(TEST_MESSAGE_PREFIX)) {
            logVerification(`Found test message in element`);

            const elementInfo = {
                tagName: element.tagName,
                className: element.className,
                id: element.id || null,
                dataIndex: element.getAttribute('data-index'),
                parentClass: element.parentElement ? element.parentElement.className : null
            };

            reportMessageFound(text, elementInfo);
            return true;
        }
        return false;
    }

    /**
     * Scan all current messages for test messages
     */
    function scanAllMessages() {
        const chatElement = document.getElementById('chat');
        if (!chatElement) {
            logVerification('Chat element not found', 'WARNING');
            return 0;
        }

        const messageBodies = chatElement.querySelectorAll('.message-body');
        let foundCount = 0;

        messageBodies.forEach((body) => {
            if (checkElementForTestMessage(body)) {
                foundCount++;
            }
        });

        logVerification(`Scanned ${messageBodies.length} messages, found ${foundCount} test messages`);
        return foundCount;
    }

    /**
     * Set up MutationObserver to watch for new messages
     */
    function setupObserver() {
        const chatElement = document.getElementById('chat');
        if (!chatElement) {
            logVerification('Chat element not found, retrying in 1 second...', 'WARNING');
            setTimeout(setupObserver, 1000);
            return;
        }

        // Find a suitable parent to observe - walk up until we find a stable container
        // or fall back to chatElement itself if DOM structure is unexpected
        let observeTarget = chatElement;
        try {
            // Try to find gradio-app or main container for broader observation
            const gradioApp = document.querySelector('gradio-app') || document.querySelector('.gradio-container');
            if (gradioApp) {
                observeTarget = gradioApp;
                logVerification('Observing gradio-app container');
            } else if (chatElement.parentNode && chatElement.parentNode.parentNode) {
                // Fall back to parent containers if available
                observeTarget = chatElement.parentNode.parentNode;
                logVerification('Observing chat parent container');
            } else {
                logVerification('Observing chat element directly');
            }
        } catch (e) {
            logVerification(`DOM traversal error: ${e.message}, observing chat directly`, 'WARNING');
        }

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                // Check added nodes
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Check if this node is a message body
                        if (node.classList && node.classList.contains('message-body')) {
                            checkElementForTestMessage(node);
                        }

                        // Check child message bodies
                        const messageBodies = node.querySelectorAll ? node.querySelectorAll('.message-body') : [];
                        messageBodies.forEach((body) => {
                            checkElementForTestMessage(body);
                        });
                    }
                });

                // Also check if character data changed (text content updates)
                if (mutation.type === 'characterData') {
                    const parent = mutation.target.parentElement;
                    if (parent && parent.closest('.message-body')) {
                        checkElementForTestMessage(parent.closest('.message-body'));
                    }
                }
            });
        });

        const config = {
            childList: true,
            subtree: true,
            characterData: true
        };

        observer.observe(observeTarget, config);
        logVerification('MutationObserver started - watching for test messages');

        // Do an initial scan
        scanAllMessages();
    }

    /**
     * Report current browser state (for verification endpoint queries)
     */
    function getBrowserState() {
        const chatElement = document.getElementById('chat');
        const messageBodies = chatElement ? chatElement.querySelectorAll('.message-body') : [];

        const testMessages = [];
        messageBodies.forEach((body, index) => {
            const text = body.textContent || '';
            if (text.includes(TEST_MESSAGE_PREFIX)) {
                testMessages.push({
                    index: index,
                    text: text.substring(0, 200),
                    dataIndex: body.closest('[data-index]')?.getAttribute('data-index')
                });
            }
        });

        return {
            chat_exists: !!chatElement,
            total_messages: messageBodies.length,
            test_messages_found: testMessages.length,
            test_messages: testMessages,
            timestamp: new Date().toISOString()
        };
    }

    // Expose function globally for server to call via JavaScript execution
    window.boredomMonitorVerification = {
        scan: scanAllMessages,
        getState: getBrowserState,
        checkElement: checkElementForTestMessage
    };

    // Start watching when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupObserver);
    } else {
        setupObserver();
    }

    logVerification('Browser verification script loaded');
})();
