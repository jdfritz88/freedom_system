/**
 * Browser-Side Injection Verification Module
 * ==========================================
 *
 * This script monitors the text-generation-webui DOM to verify
 * that injected messages actually appear in the UI.
 *
 * CRITICAL: Previous injection attempts failed because they only SENT
 * messages without verifying they appeared. This script provides
 * comprehensive DOM monitoring and verification.
 *
 * Usage:
 *   1. Paste this into the browser console
 *   2. Or inject via extension's custom_js() hook
 *   3. Call: InjectionVerifier.expectAndVerify("message text")
 */

(function() {
    'use strict';

    // =========================================================================
    // INJECTION VERIFIER CLASS
    // =========================================================================

    window.InjectionVerifier = {
        // Configuration
        config: {
            defaultTimeout: 10000,
            pollInterval: 100,
            verbose: true
        },

        // State
        observer: null,
        pendingVerifications: new Map(),
        verificationLogs: [],
        idCounter: 0,

        // =====================================================================
        // INITIALIZATION
        // =====================================================================

        init: function() {
            this.log('InjectionVerifier initializing...');
            this.startMutationObserver();
            this.log('InjectionVerifier ready');
            return this;
        },

        // =====================================================================
        // LOGGING
        // =====================================================================

        log: function(message, level = 'INFO') {
            const timestamp = new Date().toISOString().substr(11, 12);
            const logEntry = `[${timestamp}] [${level}] ${message}`;

            if (this.config.verbose) {
                if (level === 'ERROR') {
                    console.error(logEntry);
                } else if (level === 'WARN') {
                    console.warn(logEntry);
                } else {
                    console.log(logEntry);
                }
            }

            this.verificationLogs.push({
                timestamp: Date.now(),
                level: level,
                message: message
            });
        },

        // =====================================================================
        // DOM MONITORING
        // =====================================================================

        startMutationObserver: function() {
            const messagesDiv = document.querySelector('.messages');
            if (!messagesDiv) {
                this.log('WARNING: .messages container not found - will retry', 'WARN');
                setTimeout(() => this.startMutationObserver(), 1000);
                return;
            }

            if (this.observer) {
                this.observer.disconnect();
            }

            this.observer = new MutationObserver((mutations) => {
                this.handleMutations(mutations);
            });

            this.observer.observe(messagesDiv, {
                childList: true,
                subtree: true,
                characterData: true
            });

            this.log('MutationObserver started on .messages container');
        },

        handleMutations: function(mutations) {
            for (const mutation of mutations) {
                if (mutation.type === 'childList') {
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.checkNodeForPendingVerifications(node);
                        }
                    }
                } else if (mutation.type === 'characterData') {
                    // Text content changed
                    const parentElement = mutation.target.parentElement;
                    if (parentElement) {
                        this.checkNodeForPendingVerifications(parentElement);
                    }
                }
            }
        },

        checkNodeForPendingVerifications: function(node) {
            const textContent = node.textContent || '';
            const dataRaw = node.getAttribute ? node.getAttribute('data-raw') : '';
            const combined = textContent + ' ' + dataRaw;

            for (const [id, verification] of this.pendingVerifications) {
                if (combined.includes(verification.expectedText)) {
                    this.log(`FOUND expected message #${id}: "${verification.expectedText.substring(0, 50)}..."`);

                    // Mark as verified
                    verification.resolve({
                        verified: true,
                        id: id,
                        element: node,
                        foundIn: textContent.includes(verification.expectedText) ? 'textContent' :
                                 dataRaw.includes(verification.expectedText) ? 'data-raw' : 'unknown',
                        timestamp: Date.now(),
                        duration_ms: Date.now() - verification.startTime
                    });

                    // Remove from pending
                    this.pendingVerifications.delete(id);
                }
            }
        },

        // =====================================================================
        // VERIFICATION METHODS
        // =====================================================================

        /**
         * Set up expectation for a message and return a Promise
         */
        expectMessage: function(expectedText, timeout = null) {
            timeout = timeout || this.config.defaultTimeout;
            const id = ++this.idCounter;

            this.log(`Expecting message #${id}: "${expectedText.substring(0, 50)}..."`);

            return new Promise((resolve) => {
                const startTime = Date.now();

                // Set timeout
                const timer = setTimeout(() => {
                    this.pendingVerifications.delete(id);
                    this.log(`TIMEOUT waiting for message #${id}`, 'WARN');
                    resolve({
                        verified: false,
                        id: id,
                        timeout: true,
                        duration_ms: Date.now() - startTime
                    });
                }, timeout);

                // Store verification
                this.pendingVerifications.set(id, {
                    expectedText: expectedText,
                    startTime: startTime,
                    timer: timer,
                    resolve: (result) => {
                        clearTimeout(timer);
                        resolve(result);
                    }
                });
            });
        },

        /**
         * Immediately check if message exists in DOM (no waiting)
         */
        checkDomNow: function(expectedText) {
            this.log(`Checking DOM for: "${expectedText.substring(0, 50)}..."`);

            const results = {
                found: false,
                locations: []
            };

            // Check message bodies
            const messageBodies = document.querySelectorAll('.message .message-body');
            for (let i = 0; i < messageBodies.length; i++) {
                const body = messageBodies[i];
                if (body.textContent.includes(expectedText)) {
                    results.found = true;
                    results.locations.push({
                        type: 'message-body',
                        index: i,
                        textContent: body.textContent.substring(0, 200)
                    });
                }
            }

            // Check data-raw attributes
            const messagesWithRaw = document.querySelectorAll('.message[data-raw]');
            for (let i = 0; i < messagesWithRaw.length; i++) {
                const msg = messagesWithRaw[i];
                const raw = msg.getAttribute('data-raw');
                if (raw && raw.includes(expectedText)) {
                    results.found = true;
                    results.locations.push({
                        type: 'data-raw',
                        index: i,
                        dataRaw: raw.substring(0, 200)
                    });
                }
            }

            this.log(results.found ? `FOUND in ${results.locations.length} location(s)` : 'NOT FOUND');
            return results;
        },

        /**
         * Wait and poll for message
         */
        waitForMessage: function(expectedText, timeout = null, pollInterval = null) {
            timeout = timeout || this.config.defaultTimeout;
            pollInterval = pollInterval || this.config.pollInterval;

            this.log(`Waiting for message: "${expectedText.substring(0, 50)}..."`);

            return new Promise((resolve) => {
                const startTime = Date.now();

                const check = () => {
                    const result = this.checkDomNow(expectedText);

                    if (result.found) {
                        this.log(`FOUND after ${Date.now() - startTime}ms`);
                        resolve({
                            verified: true,
                            ...result,
                            duration_ms: Date.now() - startTime
                        });
                        return;
                    }

                    if (Date.now() - startTime < timeout) {
                        setTimeout(check, pollInterval);
                    } else {
                        this.log(`TIMEOUT after ${timeout}ms`, 'WARN');
                        resolve({
                            verified: false,
                            timeout: true,
                            duration_ms: Date.now() - startTime
                        });
                    }
                };

                check();
            });
        },

        /**
         * Get current message count in DOM
         */
        getMessageCount: function() {
            const messages = document.querySelectorAll('.messages .message');
            return messages.length;
        },

        /**
         * Get last message text
         */
        getLastMessage: function() {
            const messageBodies = document.querySelectorAll('.message .message-body');
            if (messageBodies.length > 0) {
                const last = messageBodies[messageBodies.length - 1];
                return {
                    text: last.textContent,
                    index: messageBodies.length - 1
                };
            }
            return null;
        },

        /**
         * Create a message count monitor
         */
        createCountMonitor: function() {
            const initialCount = this.getMessageCount();
            const self = this;

            return {
                initialCount: initialCount,

                verify: function(expectedIncrease = 1, timeout = null) {
                    timeout = timeout || self.config.defaultTimeout;

                    return new Promise((resolve) => {
                        const startTime = Date.now();

                        const check = () => {
                            const currentCount = self.getMessageCount();
                            const actualIncrease = currentCount - initialCount;

                            if (actualIncrease >= expectedIncrease) {
                                self.log(`Count increased: ${initialCount} -> ${currentCount}`);
                                resolve({
                                    verified: true,
                                    initialCount: initialCount,
                                    finalCount: currentCount,
                                    actualIncrease: actualIncrease,
                                    duration_ms: Date.now() - startTime
                                });
                                return;
                            }

                            if (Date.now() - startTime < timeout) {
                                setTimeout(check, self.config.pollInterval);
                            } else {
                                self.log(`Count change timeout: ${initialCount} -> ${currentCount}`, 'WARN');
                                resolve({
                                    verified: false,
                                    initialCount: initialCount,
                                    finalCount: currentCount,
                                    actualIncrease: actualIncrease,
                                    timeout: true
                                });
                            }
                        };

                        check();
                    });
                }
            };
        },

        // =====================================================================
        // COMPREHENSIVE VERIFICATION
        // =====================================================================

        /**
         * Run all verification methods and return combined result
         */
        comprehensiveVerify: async function(expectedText, timeout = null) {
            timeout = timeout || this.config.defaultTimeout;

            this.log(`Starting comprehensive verification for: "${expectedText.substring(0, 50)}..."`);

            const results = {
                expectedText: expectedText,
                startTime: Date.now(),
                methods: {},
                overallVerified: false,
                confirmations: 0
            };

            // Method 1: Immediate DOM check
            const immediateCheck = this.checkDomNow(expectedText);
            results.methods.immediate = {
                verified: immediateCheck.found,
                details: immediateCheck
            };
            if (immediateCheck.found) results.confirmations++;

            // Method 2: Wait for message
            const waitResult = await this.waitForMessage(expectedText, timeout / 2);
            results.methods.waitFor = {
                verified: waitResult.verified,
                details: waitResult
            };
            if (waitResult.verified) results.confirmations++;

            // Method 3: Message count check
            const countMonitor = this.createCountMonitor();
            // Note: This requires knowing initial count before injection
            // For post-injection verification, just check if count > 0
            const countResult = {
                verified: this.getMessageCount() > 0,
                count: this.getMessageCount()
            };
            results.methods.count = countResult;
            if (countResult.verified) results.confirmations++;

            // Method 4: data-raw attribute check
            const dataRawResult = this.checkDataRawContains(expectedText);
            results.methods.dataRaw = dataRawResult;
            if (dataRawResult.found) results.confirmations++;

            results.duration_ms = Date.now() - results.startTime;
            results.overallVerified = results.confirmations >= 2;

            this.log(`Comprehensive verification: ${results.confirmations}/4 confirmations - ${results.overallVerified ? 'VERIFIED' : 'NOT VERIFIED'}`);

            return results;
        },

        checkDataRawContains: function(expectedText) {
            const messages = document.querySelectorAll('.message[data-raw]');
            for (let i = 0; i < messages.length; i++) {
                const raw = messages[i].getAttribute('data-raw');
                if (raw && raw.includes(expectedText)) {
                    return {
                        found: true,
                        index: i,
                        dataRaw: raw.substring(0, 200)
                    };
                }
            }
            return { found: false };
        },

        // =====================================================================
        // UTILITY METHODS
        // =====================================================================

        /**
         * Get all verification logs
         */
        getLogs: function(count = null) {
            if (count) {
                return this.verificationLogs.slice(-count);
            }
            return this.verificationLogs;
        },

        /**
         * Clear logs
         */
        clearLogs: function() {
            this.verificationLogs = [];
            this.log('Logs cleared');
        },

        /**
         * Stop observer
         */
        stop: function() {
            if (this.observer) {
                this.observer.disconnect();
                this.observer = null;
                this.log('MutationObserver stopped');
            }
        },

        /**
         * Restart observer
         */
        restart: function() {
            this.stop();
            this.startMutationObserver();
        },

        /**
         * Get status
         */
        getStatus: function() {
            return {
                observerActive: !!this.observer,
                pendingVerifications: this.pendingVerifications.size,
                messageCount: this.getMessageCount(),
                logCount: this.verificationLogs.length
            };
        }
    };

    // =========================================================================
    // AUTO-INITIALIZE
    // =========================================================================

    // Initialize on load
    if (document.readyState === 'complete') {
        window.InjectionVerifier.init();
    } else {
        window.addEventListener('load', () => {
            window.InjectionVerifier.init();
        });
    }

    // Also expose as shorthand
    window.IV = window.InjectionVerifier;

    console.log('InjectionVerifier loaded. Use window.InjectionVerifier or window.IV');
    console.log('Example: await IV.comprehensiveVerify("test message")');

})();
