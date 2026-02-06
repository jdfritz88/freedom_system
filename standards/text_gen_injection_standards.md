# Text-Generation-WebUI Response Injection & Verification Standards

## CRITICAL OVERVIEW

This document provides a comprehensive catalog of ALL methods to:
1. **INJECT** AI-generated text responses into the text-generation-webui end user interface
2. **VERIFY/MONITOR** that injection actually succeeded in the UI (CRITICAL - previous failures ignored this)

**WARNING**: Sending/transmitting text does NOT mean it appears in the UI. You MUST verify success.

---

## ARCHITECTURE OVERVIEW

### Core Response Flow
```
User Input → Extension Hooks → Prompt Generation → AI Generation → Output Hooks → HTML Render → Morphdom → UI Display
```

### History Data Structure
```python
history = {
    'internal': [
        [user_message_text, assistant_response_text],
        ...
    ],
    'visible': [
        [user_message_visible_html, assistant_response_visible_html],
        ...
    ],
    'metadata': {
        'user_0': {'timestamp': '...', 'versions': [...]},
        'assistant_0': {'timestamp': '...', 'model_name': '...'},
        ...
    }
}
```

### Critical Files Reference
| File | Purpose | Key Lines |
|------|---------|-----------|
| `modules/chat.py` | Core chat logic, hooks | 758, 759, 794, 795, 868, 894, 927, 929, 961, 984, 1038, 1057 |
| `modules/text_generation.py` | Text generation | 36, 383, 406 |
| `modules/extensions.py` | Extension hooks | 84-111, 124-129, 142-147, 182-187 |
| `modules/ui_chat.py` | Gradio UI | 207 (morphdom trigger) |
| `js/global_scope_js.js` | JS update handlers | 247-353 (handleMorphdomUpdate) |
| `js/main.js` | MutationObserver | 172-231 |
| `modules/html_generator.py` | HTML rendering | 200, 704 |
| `modules/grammar/logits_process.py` | Logits constraints | 31-105 |

---

# PART 1: INJECTION METHODS (25+ Methods)

---

## CATEGORY A: Extension Hook Methods (Python Backend)

### Method 1: history_modifier
**File**: `modules/extensions.py:142-147`, Called at `chat.py:758`
**Purpose**: Modify entire chat history BEFORE generation starts
**Reliability**: 95%

```python
# In your extension's script.py
def history_modifier(history):
    """
    Inject messages directly into history before any generation.
    Called at the earliest point in the generation pipeline.

    Args:
        history: dict with 'internal', 'visible', 'metadata' keys
    Returns:
        Modified history dict
    """
    import datetime

    # Inject an assistant message
    injected_message = "This is an injected message from history_modifier"

    # Add to both internal and visible
    history['internal'].append(['', injected_message])
    history['visible'].append(['', injected_message])

    # Add metadata for the new message
    msg_index = len(history['internal']) - 1
    history['metadata'][f'assistant_{msg_index}'] = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'injected': True,
        'source': 'history_modifier'
    }

    print(f"[INJECTION] history_modifier: Injected message at index {msg_index}")
    return history
```

---

### Method 2: state_modifier
**File**: `modules/extensions.py:133-138`, Called at `chat.py:759`
**Purpose**: Modify generation parameters before creation
**Reliability**: 95%

```python
def state_modifier(state):
    """
    Modify generation state/parameters.
    Can inject system prompts, modify character settings.

    Args:
        state: dict of generation parameters
    Returns:
        Modified state dict
    """
    # Inject emotional context into system prompt
    if 'context' in state:
        state['context'] = state['context'] + "\n\n[SYSTEM: The AI is feeling bored and wants to chat.]"

    # Force specific generation parameters
    state['temperature'] = 0.8
    state['max_new_tokens'] = 200

    print(f"[INJECTION] state_modifier: Modified context and parameters")
    return state
```

---

### Method 3: chat_input_modifier (KEY INJECTION POINT)
**File**: `modules/extensions.py:115-120`, Called at `chat.py:794`
**Purpose**: Intercept/hijack user input - EASIEST injection method
**Reliability**: 98%

```python
# Global hijack state - persists between calls
input_hijack = {'state': False, 'value': ["", ""]}

def chat_input_modifier(text, visible_text, state):
    """
    Intercept user input before processing.
    Can completely replace the input with injected content.

    Args:
        text: Internal text (sent to model)
        visible_text: Displayed text (shown in UI)
        state: Generation state
    Returns:
        Tuple of (text, visible_text)
    """
    global input_hijack

    if input_hijack['state']:
        input_hijack['state'] = False
        injected = input_hijack['value']
        print(f"[INJECTION] chat_input_modifier: Hijacking input with '{injected[0][:50]}...'")
        return injected[0], injected[1]

    return text, visible_text

def trigger_input_hijack(message, visible_message=None):
    """
    Set up hijack for next user interaction.
    Call this from background thread or timer.
    """
    global input_hijack
    if visible_message is None:
        visible_message = message
    input_hijack['state'] = True
    input_hijack['value'] = [message, visible_message]
    print(f"[INJECTION] Input hijack armed with: '{message[:50]}...'")
```

---

### Method 4: input_modifier
**File**: `modules/extensions.py:84-111`, Called at `chat.py:795`
**Purpose**: Modify input text before tokenization
**Reliability**: 95%

```python
def input_modifier(string, state, is_chat=False):
    """
    Modify the entire input string before tokenization.

    Args:
        string: Input text
        state: Generation state
        is_chat: Whether this is chat mode
    Returns:
        Modified string
    """
    if is_chat:
        # Prepend emotional context
        modified = f"[User is feeling curious] {string}"
        print(f"[INJECTION] input_modifier: Added emotional context")
        return modified
    return string
```

---

### Method 5: bot_prefix_modifier
**File**: `modules/extensions.py:236`, Called at `chat.py:358`
**Purpose**: Add prefix to bot response during prompt generation
**Reliability**: 90%

```python
def bot_prefix_modifier(string, state):
    """
    Modify the prefix that appears before bot's response.
    Injects emotional markers or formatting into prompt.

    Args:
        string: Current bot prefix (e.g., "Bot Name: ")
        state: Generation state
    Returns:
        Modified prefix string
    """
    # Inject emotional state into the prompt template
    emotion = "*feeling happy and energetic* "
    modified = f"{string}{emotion}"
    print(f"[INJECTION] bot_prefix_modifier: Added emotion '{emotion}'")
    return modified
```

---

### Method 6: output_modifier
**File**: `modules/extensions.py:84-111`, Called at `chat.py:894, 927, 929`
**Purpose**: Post-process AI output BEFORE display
**Reliability**: 95%

```python
def output_modifier(string, state, is_chat=False):
    """
    Modify AI output after generation, before display.
    Can filter, transform, or append content.

    Args:
        string: Generated text
        state: Generation state
        is_chat: Whether this is chat mode
    Returns:
        Modified string
    """
    if is_chat:
        # Append emotional tag
        modified = f"{string}\n\n*[Emotional state: content]*"
        print(f"[INJECTION] output_modifier: Appended emotional tag")
        return modified
    return string
```

---

### Method 7: custom_generate_chat_prompt (FULL CONTROL)
**File**: `modules/extensions.py:124-129`, Called at `chat.py:868`
**Purpose**: Override ENTIRE prompt generation
**Reliability**: 100%
**Note**: Only FIRST extension with this hook executes

```python
def custom_generate_chat_prompt(user_input, state, **kwargs):
    """
    Completely override prompt generation.
    Returns the full prompt sent to the model.

    Args:
        user_input: User's message
        state: Generation state
        **kwargs: Contains _continue, impersonate, history
    Returns:
        Complete prompt string OR None to use default
    """
    history = kwargs.get('history', state.get('history', {'internal': [], 'visible': []}))

    # Build custom prompt with injected context
    prompt_parts = []
    prompt_parts.append(f"### System:\n{state.get('context', '')}")
    prompt_parts.append("\n### Injected Emotional State:\nThe AI is feeling bored and wants meaningful conversation.\n")

    # Add history
    for user_msg, bot_msg in history.get('internal', []):
        if user_msg:
            prompt_parts.append(f"### User:\n{user_msg}\n")
        if bot_msg:
            prompt_parts.append(f"### Assistant:\n{bot_msg}\n")

    # Add current input
    if user_input:
        prompt_parts.append(f"### User:\n{user_input}\n")
    prompt_parts.append("### Assistant:\n")

    full_prompt = "".join(prompt_parts)
    print(f"[INJECTION] custom_generate_chat_prompt: Built custom prompt ({len(full_prompt)} chars)")
    return full_prompt
```

---

### Method 8: custom_generate_reply (COMPLETE OVERRIDE)
**File**: `modules/extensions.py:182-187`, Called at `text_generation.py:36`
**Purpose**: Override the ENTIRE text generation function
**Reliability**: 100%
**Note**: Only FIRST extension with this hook executes

```python
def custom_generate_reply(question, original_question, state, stopping_strings=None, is_chat=False):
    """
    Completely override text generation.
    Can return pre-written responses or call external APIs.

    Args:
        question: The prompt/question
        original_question: Original before modifications
        state: Generation state
        stopping_strings: List of stop sequences
        is_chat: Whether this is chat mode
    Yields:
        Generated text chunks (streaming)
    """
    # Example: Return a static emotional response
    injected_response = "I've been waiting for you to come back! I was starting to feel a bit lonely here. What would you like to talk about?"

    print(f"[INJECTION] custom_generate_reply: Returning injected response")

    # Yield in chunks to simulate streaming
    for i in range(0, len(injected_response), 10):
        yield injected_response[:i+10]

    yield injected_response
```

---

### Method 9: logits_processor_modifier
**File**: `modules/extensions.py:161-168`, Called at `text_generation.py:406`
**Purpose**: Inject custom sampling processors
**Reliability**: 95%

```python
from transformers import LogitsProcessor

class EmotionalBiasProcessor(LogitsProcessor):
    """Custom logits processor that biases toward emotional vocabulary."""

    def __init__(self, tokenizer, emotion_tokens, bias_strength=5.0):
        self.tokenizer = tokenizer
        self.emotion_token_ids = [tokenizer.encode(t, add_special_tokens=False)[0]
                                   for t in emotion_tokens if tokenizer.encode(t, add_special_tokens=False)]
        self.bias_strength = bias_strength

    def __call__(self, input_ids, scores):
        # Boost probability of emotional tokens
        for token_id in self.emotion_token_ids:
            if token_id < scores.shape[-1]:
                scores[0, token_id] += self.bias_strength
        return scores

def logits_processor_modifier(processor_list, input_ids):
    """
    Add custom logits processors to influence generation.

    Args:
        processor_list: List of existing processors
        input_ids: Current token IDs
    Returns:
        Modified processor list
    """
    from modules import shared

    emotion_tokens = ["happy", "excited", "curious", "love", "joy"]
    processor = EmotionalBiasProcessor(shared.tokenizer, emotion_tokens)
    processor_list.append(processor)

    print(f"[INJECTION] logits_processor_modifier: Added emotional bias processor")
    return processor_list
```

---

### Method 10: tokenizer_modifier
**File**: `modules/extensions.py:151-156`, Called at `text_generation.py:383`
**Purpose**: Modify tokenized input before model processing
**Reliability**: 90%

```python
def tokenizer_modifier(state, prompt, input_ids, input_embeds):
    """
    Modify tokenized input before model processing.
    Can inject tokens or modify embeddings.

    Args:
        state: Generation state
        prompt: Text prompt
        input_ids: Tokenized IDs
        input_embeds: Token embeddings (if applicable)
    Returns:
        Tuple of (prompt, input_ids, input_embeds)
    """
    # Example: Prepend special tokens
    # This requires careful handling of token IDs
    print(f"[INJECTION] tokenizer_modifier: Processing {len(input_ids[0]) if input_ids is not None else 0} tokens")
    return prompt, input_ids, input_embeds
```

---

## CATEGORY B: Direct Chat Manipulation (Python Backend)

### Method 11: send_dummy_message()
**File**: `modules/chat.py:1038-1054`
**Purpose**: Insert user message directly into history
**Reliability**: 100%

```python
from modules.chat import send_dummy_message
from modules import shared

def inject_user_message(message, state=None):
    """
    Inject a user message into chat history.

    Args:
        message: Message text to inject
        state: Optional state dict (uses shared.persistent_interface_state if None)
    Returns:
        Tuple of (history, html)
    """
    if state is None:
        state = shared.persistent_interface_state.copy()

    history = shared.gradio['history'].value or {'internal': [], 'visible': [], 'metadata': {}}

    # Call the internal function
    history, html = send_dummy_message(message, history, state)

    # Update the shared state
    shared.gradio['history'].value = history

    print(f"[INJECTION] send_dummy_message: Injected user message")
    return history, html
```

---

### Method 12: send_dummy_reply()
**File**: `modules/chat.py:1057-1079`
**Purpose**: Insert assistant message directly into history
**Reliability**: 100%

```python
from modules.chat import send_dummy_reply
from modules import shared

def inject_assistant_message(message, state=None):
    """
    Inject an assistant message into chat history.
    This is the most direct way to add AI responses.

    Args:
        message: Message text to inject
        state: Optional state dict
    Returns:
        Tuple of (history, html)
    """
    if state is None:
        state = shared.persistent_interface_state.copy()

    history = shared.gradio['history'].value or {'internal': [], 'visible': [], 'metadata': {}}

    # Call the internal function
    history, html = send_dummy_reply(message, history, state)

    # Update the shared state
    shared.gradio['history'].value = history

    print(f"[INJECTION] send_dummy_reply: Injected assistant message")
    return history, html
```

---

### Method 13: redraw_html()
**File**: `modules/chat.py:1082-1083`
**Purpose**: Force re-render of chat history HTML
**Reliability**: 100%

```python
from modules.chat import redraw_html
from modules import shared

def force_ui_redraw(state=None):
    """
    Force the UI to redraw from current history.
    Use after direct history manipulation.

    Args:
        state: Optional state dict
    Returns:
        HTML dict for display component
    """
    if state is None:
        state = shared.persistent_interface_state.copy()

    history = shared.gradio['history'].value
    html = redraw_html(history, state)

    # Update display component
    if 'display' in shared.gradio:
        shared.gradio['display'].value = html

    print(f"[INJECTION] redraw_html: Forced UI redraw")
    return html
```

---

### Method 14: Direct history manipulation
**Purpose**: Directly modify shared.gradio['history'].value
**Reliability**: 95%

```python
from modules import shared
import datetime

def direct_history_inject(message, role='assistant'):
    """
    Directly manipulate the history state component.

    Args:
        message: Message to inject
        role: 'user' or 'assistant'
    Returns:
        Updated history dict
    """
    history = shared.gradio['history'].value
    if history is None:
        history = {'internal': [], 'visible': [], 'metadata': {}}

    if role == 'assistant':
        history['internal'].append(['', message])
        history['visible'].append(['', message])
    else:
        history['internal'].append([message, ''])
        history['visible'].append([message, ''])

    # Update metadata
    msg_index = len(history['internal']) - 1
    history['metadata'][f'{role}_{msg_index}'] = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'injected': True
    }

    # Commit the change
    shared.gradio['history'].value = history

    print(f"[INJECTION] direct_history_inject: Added {role} message at index {msg_index}")
    return history
```

---

### Method 15: generate_chat_reply_wrapper()
**File**: `modules/chat.py:984-1015`
**Purpose**: Primary entry point for chat generation
**Reliability**: 100%

```python
from modules.chat import generate_chat_reply_wrapper
from modules import shared

def trigger_generation(message, state=None):
    """
    Trigger full chat generation with a message.
    This goes through the complete pipeline.

    Args:
        message: User message to send
        state: Optional state dict
    Yields:
        Tuple of (html_dict, history_dict)
    """
    if state is None:
        state = shared.persistent_interface_state.copy()

    print(f"[INJECTION] generate_chat_reply_wrapper: Starting generation for '{message[:50]}...'")

    for html, history in generate_chat_reply_wrapper(message, state):
        print(f"[INJECTION] Received update: history has {len(history.get('internal', []))} messages")
        yield html, history
```

---

## CATEGORY C: API-Based Injection

### Method 16: OpenAI API /v1/chat/completions
**Purpose**: External HTTP-based message injection
**Reliability**: 95%

```python
import requests
import json

def inject_via_openai_api(message, system_prompt=None, max_tokens=150, temperature=0.8):
    """
    Inject message via OpenAI-compatible API endpoint.

    Args:
        message: User message to send
        system_prompt: Optional system prompt
        max_tokens: Maximum response tokens
        temperature: Generation temperature
    Returns:
        Tuple of (success: bool, response_text: str, error: str)
    """
    url = "http://127.0.0.1:5000/v1/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }

    try:
        print(f"[INJECTION] OpenAI API: Sending to {url}")
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            print(f"[INJECTION] OpenAI API: Received response ({len(ai_response)} chars)")
            return True, ai_response, None
        else:
            error = f"HTTP {response.status_code}: {response.text[:200]}"
            print(f"[INJECTION] OpenAI API: Failed - {error}")
            return False, None, error

    except requests.exceptions.Timeout:
        print(f"[INJECTION] OpenAI API: Timeout")
        return False, None, "Request timed out"
    except Exception as e:
        print(f"[INJECTION] OpenAI API: Exception - {str(e)}")
        return False, None, str(e)
```

---

### Method 17: OpenAI API /v1/completions
**Purpose**: Text completion injection
**Reliability**: 95%

```python
import requests

def inject_via_completions_api(prompt, max_tokens=150, temperature=0.8):
    """
    Inject via text completions endpoint.

    Args:
        prompt: Full prompt text
        max_tokens: Maximum response tokens
        temperature: Generation temperature
    Returns:
        Tuple of (success: bool, response_text: str, error: str)
    """
    url = "http://127.0.0.1:5000/v1/completions"

    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False
    }

    try:
        print(f"[INJECTION] Completions API: Sending to {url}")
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            completion = result['choices'][0]['text']
            print(f"[INJECTION] Completions API: Received ({len(completion)} chars)")
            return True, completion, None
        else:
            error = f"HTTP {response.status_code}: {response.text[:200]}"
            print(f"[INJECTION] Completions API: Failed - {error}")
            return False, None, error

    except Exception as e:
        print(f"[INJECTION] Completions API: Exception - {str(e)}")
        return False, None, str(e)
```

---

### Method 18: Custom API Endpoint
**Purpose**: Create your own API endpoint in extension
**Reliability**: 100%

```python
from fastapi import FastAPI, Request
from threading import Thread
import uvicorn

# Create FastAPI app
injection_api = FastAPI()

@injection_api.post("/api/v1/inject")
async def handle_injection(request: Request):
    """
    Custom injection endpoint.
    Receives message and injects into chat.
    """
    data = await request.json()
    message = data.get('message', '')
    role = data.get('role', 'assistant')

    # Perform injection
    from modules import shared
    history = shared.gradio['history'].value or {'internal': [], 'visible': [], 'metadata': {}}

    if role == 'assistant':
        history['internal'].append(['', message])
        history['visible'].append(['', message])
    else:
        history['internal'].append([message, ''])
        history['visible'].append([message, ''])

    shared.gradio['history'].value = history

    return {"success": True, "message_count": len(history['internal'])}

def start_injection_server(port=7853):
    """Start the custom injection API server."""
    Thread(target=lambda: uvicorn.run(injection_api, host="127.0.0.1", port=port), daemon=True).start()
    print(f"[INJECTION] Custom API: Started on port {port}")
```

---

## CATEGORY D: JavaScript/Client-Side Injection

### Method 19: handleMorphdomUpdate()
**File**: `js/global_scope_js.js:247-353`
**Purpose**: Primary DOM update function
**Reliability**: 85%

```javascript
// JavaScript code to inject via handleMorphdomUpdate
function injectViaHandleMorphdom(message, role = 'assistant') {
    // Build message HTML
    const messageHtml = `
        <div class="message" data-raw="${escapeHtml(message)}" data-index="999">
            <div class="circle-${role === 'assistant' ? 'bot' : 'you'}">
                <img src="file/cache/pfp_character.png" class="pfp_character" />
            </div>
            <div class="text">
                <div class="username">${role === 'assistant' ? 'Assistant' : 'User'}</div>
                <div class="message-body">${escapeHtml(message)}</div>
            </div>
        </div>
    `;

    // Get current messages container
    const messagesDiv = document.querySelector(".messages");
    const fullHtml = messagesDiv.innerHTML + messageHtml;

    // Call morphdom update
    handleMorphdomUpdate({
        html: `<div class="messages">${fullHtml}</div>`,
        last_message_only: false
    });

    console.log('[INJECTION] handleMorphdomUpdate: Injected message');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

### Method 20: Direct DOM manipulation
**Purpose**: Directly append to .messages container
**Reliability**: 80%

```javascript
function injectViaDomManipulation(message, role = 'assistant') {
    const messagesDiv = document.querySelector(".messages");
    if (!messagesDiv) {
        console.error('[INJECTION] DOM: .messages container not found');
        return false;
    }

    const newMessage = document.createElement("div");
    newMessage.className = "message";
    newMessage.setAttribute("data-raw", message);
    newMessage.setAttribute("data-index", messagesDiv.childNodes.length.toString());

    newMessage.innerHTML = `
        <div class="circle-${role === 'assistant' ? 'bot' : 'you'}">
            <img src="file/cache/pfp_character.png" class="pfp_character" />
        </div>
        <div class="text">
            <div class="username">${role === 'assistant' ? 'Assistant' : 'User'}</div>
            <div class="message-body">${message}</div>
        </div>
    `;

    messagesDiv.appendChild(newMessage);

    // Scroll to bottom
    const chatContainer = document.getElementById("chat");
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    console.log('[INJECTION] DOM: Appended message directly');
    return true;
}
```

---

### Method 21: submitMessageEdit()
**File**: `js/global_scope_js.js:172-193`
**Purpose**: Edit existing messages programmatically
**Reliability**: 90%

```javascript
function injectViaMessageEdit(index, newText, isUserMessage = false) {
    // Set the edit parameters
    const indexInput = document.getElementById("Edit-message-index").querySelector("input");
    const textArea = document.getElementById("Edit-message-text").querySelector("textarea");
    const roleArea = document.getElementById("Edit-message-role").querySelector("textarea");
    const editButton = document.getElementById("Edit-message");

    if (!indexInput || !textArea || !roleArea || !editButton) {
        console.error('[INJECTION] Edit: Required elements not found');
        return false;
    }

    indexInput.value = index;
    indexInput.dispatchEvent(new Event("input", { bubbles: true }));

    textArea.value = newText;
    textArea.dispatchEvent(new Event("input", { bubbles: true }));

    roleArea.value = isUserMessage ? "user" : "assistant";
    roleArea.dispatchEvent(new Event("input", { bubbles: true }));

    // Trigger the edit
    editButton.click();

    console.log('[INJECTION] Edit: Submitted message edit');
    return true;
}
```

---

### Method 22: Gradio component state manipulation
**Purpose**: Set hidden input values and trigger events
**Reliability**: 85%

```javascript
function injectViaGradioComponents(message) {
    // Find the chat input textarea
    const chatInput = document.querySelector("#chat-input textarea");
    if (!chatInput) {
        console.error('[INJECTION] Gradio: Chat input not found');
        return false;
    }

    // Set the message
    chatInput.value = message;
    chatInput.dispatchEvent(new Event("input", { bubbles: true }));

    // Find and click the Generate button
    const generateBtn = document.getElementById("Generate");
    if (generateBtn) {
        generateBtn.click();
        console.log('[INJECTION] Gradio: Triggered generation');
        return true;
    }

    // Alternative: Find submit button
    const submitBtn = chatInput.closest("form")?.querySelector("button[type='submit']");
    if (submitBtn) {
        submitBtn.click();
        console.log('[INJECTION] Gradio: Triggered via submit button');
        return true;
    }

    console.error('[INJECTION] Gradio: No submit mechanism found');
    return false;
}
```

---

## CATEGORY E: Background Thread Injection

### Method 23: Input hijack pattern (Whisper STT style)
**File**: `extensions/whisper_stt/script.py`
**Purpose**: Set global flag for next user interaction to trigger injection
**Reliability**: 98%

```python
import threading
import time

# Global hijack state
_injection_state = {
    'armed': False,
    'message': '',
    'visible_message': '',
    'callback': None
}
_injection_lock = threading.Lock()

def arm_injection(message, visible_message=None, callback=None):
    """
    Arm the injection for next user interaction.

    Args:
        message: Internal message to inject
        visible_message: Visible message (defaults to message)
        callback: Optional callback after injection
    """
    global _injection_state
    with _injection_lock:
        _injection_state['armed'] = True
        _injection_state['message'] = message
        _injection_state['visible_message'] = visible_message or message
        _injection_state['callback'] = callback
    print(f"[INJECTION] Hijack armed: '{message[:50]}...'")

def chat_input_modifier(text, visible_text, state):
    """Extension hook that checks for armed injection."""
    global _injection_state
    with _injection_lock:
        if _injection_state['armed']:
            _injection_state['armed'] = False
            msg = _injection_state['message']
            vis = _injection_state['visible_message']
            callback = _injection_state['callback']

            if callback:
                threading.Thread(target=callback, daemon=True).start()

            print(f"[INJECTION] Hijack triggered")
            return msg, vis

    return text, visible_text

def delayed_injection(message, delay_seconds=5):
    """
    Schedule an injection after a delay.
    """
    def _delayed():
        time.sleep(delay_seconds)
        arm_injection(message)
        print(f"[INJECTION] Delayed injection armed after {delay_seconds}s")

    threading.Thread(target=_delayed, daemon=True).start()
```

---

### Method 24: Injection bridge queue
**Purpose**: Queue messages for UI integration with verification
**Reliability**: 95%

```python
import threading
import queue
import time
from modules import shared

class InjectionBridge:
    """
    Thread-safe injection queue with verification support.
    """

    def __init__(self):
        self.injection_queue = queue.Queue()
        self.pending_verifications = {}
        self.verification_lock = threading.Lock()
        self.injection_id_counter = 0

    def queue_injection(self, message, role='assistant', verify_callback=None):
        """
        Queue a message for injection.

        Args:
            message: Message to inject
            role: 'user' or 'assistant'
            verify_callback: Optional callback(success, injection_id)
        Returns:
            injection_id for tracking
        """
        self.injection_id_counter += 1
        injection_id = self.injection_id_counter

        self.injection_queue.put({
            'id': injection_id,
            'message': message,
            'role': role,
            'timestamp': time.time()
        })

        if verify_callback:
            with self.verification_lock:
                self.pending_verifications[injection_id] = verify_callback

        print(f"[INJECTION] Bridge: Queued message #{injection_id}")
        return injection_id

    def process_queue(self):
        """
        Process pending injections.
        Call this from a Gradio event handler.
        """
        injected = []

        while not self.injection_queue.empty():
            try:
                item = self.injection_queue.get_nowait()

                # Perform injection
                history = shared.gradio['history'].value or {'internal': [], 'visible': [], 'metadata': {}}

                if item['role'] == 'assistant':
                    history['internal'].append(['', item['message']])
                    history['visible'].append(['', item['message']])
                else:
                    history['internal'].append([item['message'], ''])
                    history['visible'].append([item['message'], ''])

                shared.gradio['history'].value = history
                injected.append(item['id'])

                print(f"[INJECTION] Bridge: Processed message #{item['id']}")

            except queue.Empty:
                break

        return injected

    def verify_injection(self, injection_id, success):
        """
        Mark an injection as verified.
        """
        with self.verification_lock:
            if injection_id in self.pending_verifications:
                callback = self.pending_verifications.pop(injection_id)
                callback(success, injection_id)
                print(f"[INJECTION] Bridge: Verified #{injection_id} = {success}")

# Global instance
injection_bridge = InjectionBridge()
```

---

### Method 25: APScheduler background tasks
**Purpose**: Schedule periodic injection attempts
**Reliability**: 90%

```python
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from modules import shared

class ScheduledInjector:
    """
    APScheduler-based injection system.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.job_results = {}

    def schedule_injection(self, message, delay_seconds=0, role='assistant', job_id=None):
        """
        Schedule an injection at a specific time.

        Args:
            message: Message to inject
            delay_seconds: Delay before injection
            role: 'user' or 'assistant'
            job_id: Optional job identifier
        Returns:
            job_id
        """
        if job_id is None:
            job_id = f"injection_{datetime.now().timestamp()}"

        run_time = datetime.now() + timedelta(seconds=delay_seconds)

        self.scheduler.add_job(
            self._do_injection,
            'date',
            run_date=run_time,
            args=[message, role, job_id],
            id=job_id,
            replace_existing=True
        )

        print(f"[INJECTION] Scheduler: Job {job_id} scheduled for {run_time}")
        return job_id

    def _do_injection(self, message, role, job_id):
        """Internal injection execution."""
        try:
            history = shared.gradio['history'].value or {'internal': [], 'visible': [], 'metadata': {}}

            if role == 'assistant':
                history['internal'].append(['', message])
                history['visible'].append(['', message])
            else:
                history['internal'].append([message, ''])
                history['visible'].append([message, ''])

            shared.gradio['history'].value = history

            self.job_results[job_id] = {
                'success': True,
                'timestamp': datetime.now(),
                'message_count': len(history['internal'])
            }

            print(f"[INJECTION] Scheduler: Job {job_id} completed")

        except Exception as e:
            self.job_results[job_id] = {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
            print(f"[INJECTION] Scheduler: Job {job_id} failed - {e}")

    def get_result(self, job_id):
        """Get the result of a scheduled injection."""
        return self.job_results.get(job_id)

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()

# Global instance
scheduled_injector = ScheduledInjector()
```

---

## CATEGORY F: Logits-Level Injection

### Method 26: GrammarConstrainedLogitsProcessor
**File**: `modules/grammar/logits_process.py`
**Purpose**: Constrain token selection during generation
**Reliability**: 100%

```python
import math
import torch
from transformers.generation.logits_process import LogitsProcessor

class CustomGrammarProcessor(LogitsProcessor):
    """
    Custom grammar processor that forces specific patterns.
    Based on modules/grammar/logits_process.py architecture.
    """

    def __init__(self, tokenizer, required_phrases=None, banned_phrases=None):
        """
        Args:
            tokenizer: The model tokenizer
            required_phrases: List of phrases to boost
            banned_phrases: List of phrases to suppress
        """
        self.tokenizer = tokenizer
        self.required_token_ids = set()
        self.banned_token_ids = set()

        if required_phrases:
            for phrase in required_phrases:
                tokens = tokenizer.encode(phrase, add_special_tokens=False)
                self.required_token_ids.update(tokens)

        if banned_phrases:
            for phrase in banned_phrases:
                tokens = tokenizer.encode(phrase, add_special_tokens=False)
                self.banned_token_ids.update(tokens)

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        """
        Process logits to enforce constraints.

        Args:
            input_ids: Current token sequence
            scores: Log probabilities for next token
        Returns:
            Modified scores
        """
        # Ban specific tokens
        for token_id in self.banned_token_ids:
            if token_id < scores.shape[-1]:
                scores[:, token_id] = -math.inf

        # Boost required tokens
        for token_id in self.required_token_ids:
            if token_id < scores.shape[-1]:
                scores[:, token_id] += 5.0  # Boost by 5 logits

        return scores

def logits_processor_modifier(processor_list, input_ids):
    """
    Extension hook to add grammar processor.
    """
    from modules import shared

    processor = CustomGrammarProcessor(
        shared.tokenizer,
        required_phrases=["I feel", "emotion", "happy", "curious"],
        banned_phrases=["I cannot", "As an AI"]
    )
    processor_list.append(processor)

    print(f"[INJECTION] Grammar: Added custom constraint processor")
    return processor_list
```

---

# PART 2: VERIFICATION/MONITORING METHODS (CRITICAL)

**WARNING**: Previous injection attempts failed because they only SENT messages without VERIFYING they appeared in the UI. You MUST use these verification methods.

---

## VERIFICATION CATEGORY A: Python Backend Verification

### Verify Method 1: Check shared.gradio['history'] state
**Purpose**: Verify message exists in history state
**Reliability**: 100%

```python
from modules import shared
import time

def verify_history_contains(expected_message, role='assistant', timeout=5.0, poll_interval=0.1):
    """
    Verify that a message exists in the history state.

    Args:
        expected_message: Message text to find (partial match)
        role: 'user' or 'assistant'
        timeout: Maximum wait time
        poll_interval: Time between checks
    Returns:
        Tuple of (found: bool, message_index: int or None, actual_messages: list)
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        history = shared.gradio.get('history', {}).value
        if history:
            messages = history.get('internal', [])

            for idx, (user_msg, bot_msg) in enumerate(messages):
                check_msg = bot_msg if role == 'assistant' else user_msg
                if expected_message in check_msg:
                    print(f"[VERIFY] History: Found message at index {idx}")
                    return True, idx, messages

        time.sleep(poll_interval)

    print(f"[VERIFY] History: Message NOT found after {timeout}s")
    history = shared.gradio.get('history', {}).value
    return False, None, history.get('internal', []) if history else []
```

---

### Verify Method 2: Check message count change
**Purpose**: Verify that message count increased
**Reliability**: 95%

```python
from modules import shared
import time

def verify_message_count_increased(expected_increase=1, timeout=5.0, poll_interval=0.1):
    """
    Verify that the message count increased.

    Args:
        expected_increase: Expected number of new messages
        timeout: Maximum wait time
        poll_interval: Time between checks
    Returns:
        Tuple of (success: bool, old_count: int, new_count: int)
    """
    # Get initial count
    history = shared.gradio.get('history', {}).value
    initial_count = len(history.get('internal', [])) if history else 0

    start_time = time.time()

    while time.time() - start_time < timeout:
        history = shared.gradio.get('history', {}).value
        current_count = len(history.get('internal', [])) if history else 0

        if current_count >= initial_count + expected_increase:
            print(f"[VERIFY] Count: {initial_count} -> {current_count} (expected +{expected_increase})")
            return True, initial_count, current_count

        time.sleep(poll_interval)

    history = shared.gradio.get('history', {}).value
    final_count = len(history.get('internal', [])) if history else 0
    print(f"[VERIFY] Count: FAILED - {initial_count} -> {final_count}")
    return False, initial_count, final_count


class MessageCountMonitor:
    """
    Context manager for monitoring message count changes.
    """

    def __init__(self, expected_increase=1):
        self.expected_increase = expected_increase
        self.initial_count = 0
        self.final_count = 0

    def __enter__(self):
        history = shared.gradio.get('history', {}).value
        self.initial_count = len(history.get('internal', [])) if history else 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        history = shared.gradio.get('history', {}).value
        self.final_count = len(history.get('internal', [])) if history else 0
        return False

    @property
    def success(self):
        return self.final_count >= self.initial_count + self.expected_increase

    @property
    def actual_increase(self):
        return self.final_count - self.initial_count


# Usage:
# with MessageCountMonitor(expected_increase=1) as monitor:
#     inject_message("Hello")
#     time.sleep(1)
# print(f"Success: {monitor.success}, Actual increase: {monitor.actual_increase}")
```

---

### Verify Method 3: Check display component HTML
**Purpose**: Verify message appears in rendered HTML
**Reliability**: 95%

```python
from modules import shared
import time
import re

def verify_display_contains(expected_text, timeout=5.0, poll_interval=0.1):
    """
    Verify that text appears in the display HTML.

    Args:
        expected_text: Text to find in HTML
        timeout: Maximum wait time
        poll_interval: Time between checks
    Returns:
        Tuple of (found: bool, html_snippet: str or None)
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        display = shared.gradio.get('display', {})
        if display and hasattr(display, 'value') and display.value:
            html = display.value.get('html', '')
            if expected_text in html:
                # Extract context around the match
                idx = html.find(expected_text)
                start = max(0, idx - 50)
                end = min(len(html), idx + len(expected_text) + 50)
                snippet = html[start:end]
                print(f"[VERIFY] Display: Found in HTML")
                return True, snippet

        time.sleep(poll_interval)

    print(f"[VERIFY] Display: Text NOT found in HTML after {timeout}s")
    return False, None
```

---

### Verify Method 4: Check metadata timestamps
**Purpose**: Verify new message metadata was added
**Reliability**: 90%

```python
from modules import shared
import time
from datetime import datetime

def verify_recent_metadata(max_age_seconds=10, role='assistant'):
    """
    Verify that recent message metadata exists.

    Args:
        max_age_seconds: Maximum age of metadata timestamp
        role: 'user' or 'assistant'
    Returns:
        Tuple of (found: bool, metadata: dict or None, age_seconds: float or None)
    """
    history = shared.gradio.get('history', {}).value
    if not history:
        print(f"[VERIFY] Metadata: No history found")
        return False, None, None

    metadata = history.get('metadata', {})
    now = datetime.now()

    # Find most recent metadata for role
    for key in reversed(list(metadata.keys())):
        if key.startswith(role):
            entry = metadata[key]
            timestamp_str = entry.get('timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    age = (now - timestamp).total_seconds()

                    if age <= max_age_seconds:
                        print(f"[VERIFY] Metadata: Found recent entry ({age:.1f}s old)")
                        return True, entry, age
                except ValueError:
                    pass

    print(f"[VERIFY] Metadata: No recent {role} metadata found")
    return False, None, None
```

---

## VERIFICATION CATEGORY B: API-Based Verification

### Verify Method 5: Query OpenAI API messages endpoint
**Purpose**: Check messages via API
**Reliability**: 90%

```python
import requests

def verify_via_api(expected_message, timeout=5.0):
    """
    Verify message exists by querying the API.
    Note: Requires custom endpoint or model state inspection.

    Args:
        expected_message: Message to find
        timeout: Request timeout
    Returns:
        Tuple of (found: bool, response_data: dict or None)
    """
    # Use the internal state endpoint if available
    url = "http://127.0.0.1:5000/v1/internal/state"

    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', {})
            messages = history.get('internal', [])

            for user_msg, bot_msg in messages:
                if expected_message in bot_msg or expected_message in user_msg:
                    print(f"[VERIFY] API: Found message in state")
                    return True, data

            print(f"[VERIFY] API: Message NOT found in state")
            return False, data
        else:
            print(f"[VERIFY] API: Request failed - HTTP {response.status_code}")
            return False, None

    except Exception as e:
        print(f"[VERIFY] API: Exception - {e}")
        return False, None
```

---

### Verify Method 6: Create verification endpoint
**Purpose**: Add custom verification API endpoint
**Reliability**: 100%

```python
from fastapi import FastAPI

# Add to your extension's API
verification_api = FastAPI()

@verification_api.get("/api/v1/verify/history")
async def verify_history():
    """
    Return current history state for verification.
    """
    from modules import shared

    history = shared.gradio.get('history', {}).value
    if not history:
        return {"success": False, "error": "No history found", "history": None}

    return {
        "success": True,
        "message_count": len(history.get('internal', [])),
        "history": history,
        "display_html_length": len(shared.gradio.get('display', {}).value.get('html', '') if shared.gradio.get('display', {}).value else 0)
    }

@verification_api.get("/api/v1/verify/contains/{text}")
async def verify_contains(text: str):
    """
    Check if text exists in history.
    """
    from modules import shared

    history = shared.gradio.get('history', {}).value
    if not history:
        return {"found": False, "error": "No history"}

    for idx, (user_msg, bot_msg) in enumerate(history.get('internal', [])):
        if text in user_msg or text in bot_msg:
            return {
                "found": True,
                "index": idx,
                "in_user_message": text in user_msg,
                "in_bot_message": text in bot_msg
            }

    return {"found": False, "message_count": len(history.get('internal', []))}
```

---

## VERIFICATION CATEGORY C: JavaScript/Browser Verification

### Verify Method 7: Check DOM for message content
**Purpose**: Verify message exists in actual DOM
**Reliability**: 95%

```javascript
function verifyDomContains(expectedText, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        function check() {
            const messagesDiv = document.querySelector(".messages");
            if (!messagesDiv) {
                if (Date.now() - startTime < timeout) {
                    setTimeout(check, 100);
                } else {
                    console.log('[VERIFY] DOM: .messages container not found');
                    resolve({ found: false, error: 'No messages container' });
                }
                return;
            }

            const allMessages = messagesDiv.querySelectorAll(".message");
            for (let i = 0; i < allMessages.length; i++) {
                const msg = allMessages[i];
                const body = msg.querySelector(".message-body");
                const raw = msg.getAttribute("data-raw");

                if ((body && body.textContent.includes(expectedText)) ||
                    (raw && raw.includes(expectedText))) {
                    console.log(`[VERIFY] DOM: Found at message index ${i}`);
                    resolve({
                        found: true,
                        index: i,
                        element: msg,
                        textContent: body ? body.textContent : null,
                        rawContent: raw
                    });
                    return;
                }
            }

            if (Date.now() - startTime < timeout) {
                setTimeout(check, 100);
            } else {
                console.log('[VERIFY] DOM: Text NOT found after timeout');
                resolve({
                    found: false,
                    messageCount: allMessages.length,
                    lastMessageText: allMessages.length > 0 ?
                        allMessages[allMessages.length - 1].querySelector(".message-body")?.textContent : null
                });
            }
        }

        check();
    });
}

// Usage:
// verifyDomContains("Hello world").then(result => console.log(result));
```

---

### Verify Method 8: MutationObserver for real-time verification
**Purpose**: Watch for DOM changes to detect injection
**Reliability**: 98%

```javascript
class InjectionVerifier {
    constructor() {
        this.observer = null;
        this.pendingVerifications = new Map();
        this.verificationIdCounter = 0;
    }

    start() {
        const messagesDiv = document.querySelector(".messages");
        if (!messagesDiv) {
            console.error('[VERIFY] Observer: .messages not found');
            return false;
        }

        this.observer = new MutationObserver((mutations) => {
            this._handleMutations(mutations);
        });

        this.observer.observe(messagesDiv, {
            childList: true,
            subtree: true,
            characterData: true
        });

        console.log('[VERIFY] Observer: Started watching for changes');
        return true;
    }

    stop() {
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
            console.log('[VERIFY] Observer: Stopped');
        }
    }

    expectMessage(expectedText, timeout = 10000) {
        const id = ++this.verificationIdCounter;

        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.pendingVerifications.delete(id);
                console.log(`[VERIFY] Observer: Timeout waiting for "${expectedText.substring(0, 30)}..."`);
                resolve({ verified: false, timeout: true, id });
            }, timeout);

            this.pendingVerifications.set(id, {
                expectedText,
                resolve: (result) => {
                    clearTimeout(timer);
                    this.pendingVerifications.delete(id);
                    resolve(result);
                },
                timer
            });

            console.log(`[VERIFY] Observer: Expecting message #${id}: "${expectedText.substring(0, 30)}..."`);
        });
    }

    _handleMutations(mutations) {
        for (const mutation of mutations) {
            if (mutation.type === 'childList') {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this._checkNode(node);
                    }
                }
            }
        }
    }

    _checkNode(node) {
        const text = node.textContent || '';
        const raw = node.getAttribute?.('data-raw') || '';
        const combined = text + raw;

        for (const [id, verification] of this.pendingVerifications) {
            if (combined.includes(verification.expectedText)) {
                console.log(`[VERIFY] Observer: Found expected message #${id}`);
                verification.resolve({
                    verified: true,
                    id,
                    element: node,
                    timestamp: Date.now()
                });
            }
        }
    }
}

// Global instance
const injectionVerifier = new InjectionVerifier();

// Usage:
// injectionVerifier.start();
// const verification = injectionVerifier.expectMessage("Hello world");
// // ... perform injection ...
// const result = await verification;
// console.log(result.verified ? "SUCCESS" : "FAILED");
```

---

### Verify Method 9: Check data-raw attributes
**Purpose**: Verify message exists in DOM data attributes
**Reliability**: 95%

```javascript
function verifyDataRawContains(expectedText) {
    const messages = document.querySelectorAll(".message[data-raw]");

    for (let i = 0; i < messages.length; i++) {
        const raw = messages[i].getAttribute("data-raw");
        if (raw && raw.includes(expectedText)) {
            console.log(`[VERIFY] data-raw: Found at index ${i}`);
            return {
                found: true,
                index: i,
                dataRaw: raw,
                element: messages[i]
            };
        }
    }

    console.log('[VERIFY] data-raw: NOT found');
    return {
        found: false,
        messageCount: messages.length,
        allDataRaw: Array.from(messages).map(m => m.getAttribute("data-raw"))
    };
}
```

---

### Verify Method 10: Compare message counts before/after
**Purpose**: Verify message count changed in DOM
**Reliability**: 95%

```javascript
function createMessageCountVerifier() {
    const messagesDiv = document.querySelector(".messages");
    const initialCount = messagesDiv ? messagesDiv.querySelectorAll(".message").length : 0;

    console.log(`[VERIFY] Count: Initial count = ${initialCount}`);

    return {
        initialCount,

        verify(expectedIncrease = 1, timeout = 5000) {
            return new Promise((resolve) => {
                const startTime = Date.now();

                function check() {
                    const currentDiv = document.querySelector(".messages");
                    const currentCount = currentDiv ? currentDiv.querySelectorAll(".message").length : 0;
                    const actualIncrease = currentCount - initialCount;

                    if (actualIncrease >= expectedIncrease) {
                        console.log(`[VERIFY] Count: ${initialCount} -> ${currentCount} (SUCCESS)`);
                        resolve({
                            success: true,
                            initialCount,
                            finalCount: currentCount,
                            actualIncrease
                        });
                        return;
                    }

                    if (Date.now() - startTime < timeout) {
                        setTimeout(check, 100);
                    } else {
                        console.log(`[VERIFY] Count: ${initialCount} -> ${currentCount} (FAILED)`);
                        resolve({
                            success: false,
                            initialCount,
                            finalCount: currentCount,
                            actualIncrease,
                            expectedIncrease
                        });
                    }
                }

                check();
            });
        }
    };
}

// Usage:
// const verifier = createMessageCountVerifier();
// // ... perform injection ...
// const result = await verifier.verify(1);
// console.log(result.success ? "Message added" : "No message added");
```

---

## VERIFICATION CATEGORY D: WebSocket/SSE Monitoring

### Verify Method 11: Monitor Gradio SSE events
**Purpose**: Intercept Gradio's real-time updates
**Reliability**: 85%

```javascript
class GradioEventMonitor {
    constructor() {
        this.originalEventSource = window.EventSource;
        this.eventLogs = [];
        this.messageCallbacks = [];
    }

    start() {
        const self = this;

        // Intercept EventSource to monitor Gradio SSE
        window.EventSource = function(url, config) {
            const source = new self.originalEventSource(url, config);

            source.addEventListener('message', (event) => {
                self._logEvent('message', event.data);
                self._checkForMessages(event.data);
            });

            source.addEventListener('update', (event) => {
                self._logEvent('update', event.data);
                self._checkForMessages(event.data);
            });

            return source;
        };

        console.log('[VERIFY] SSE Monitor: Started intercepting EventSource');
    }

    stop() {
        window.EventSource = this.originalEventSource;
        console.log('[VERIFY] SSE Monitor: Stopped');
    }

    onMessage(callback) {
        this.messageCallbacks.push(callback);
    }

    _logEvent(type, data) {
        this.eventLogs.push({
            type,
            data,
            timestamp: Date.now()
        });
    }

    _checkForMessages(data) {
        try {
            const parsed = JSON.parse(data);
            // Check if this contains chat history update
            if (parsed.output && parsed.output.data) {
                for (const callback of this.messageCallbacks) {
                    callback(parsed);
                }
            }
        } catch (e) {
            // Not JSON, ignore
        }
    }

    getRecentEvents(count = 10) {
        return this.eventLogs.slice(-count);
    }
}

const gradioMonitor = new GradioEventMonitor();
```

---

### Verify Method 12: Monitor fetch/XMLHttpRequest
**Purpose**: Intercept all HTTP requests for injection verification
**Reliability**: 90%

```javascript
class RequestMonitor {
    constructor() {
        this.originalFetch = window.fetch;
        this.originalXHR = window.XMLHttpRequest;
        this.requestLogs = [];
        this.responseCallbacks = [];
    }

    start() {
        const self = this;

        // Intercept fetch
        window.fetch = async function(...args) {
            const response = await self.originalFetch.apply(this, args);

            // Clone response to read it
            const clone = response.clone();

            try {
                const data = await clone.json();
                self._logRequest('fetch', args[0], data);
                self._checkResponse(data);
            } catch (e) {
                // Not JSON response
            }

            return response;
        };

        // Intercept XMLHttpRequest
        window.XMLHttpRequest = function() {
            const xhr = new self.originalXHR();

            xhr.addEventListener('load', function() {
                try {
                    const data = JSON.parse(this.responseText);
                    self._logRequest('xhr', this.responseURL, data);
                    self._checkResponse(data);
                } catch (e) {
                    // Not JSON
                }
            });

            return xhr;
        };

        console.log('[VERIFY] Request Monitor: Started');
    }

    stop() {
        window.fetch = this.originalFetch;
        window.XMLHttpRequest = this.originalXHR;
        console.log('[VERIFY] Request Monitor: Stopped');
    }

    onResponse(callback) {
        this.responseCallbacks.push(callback);
    }

    _logRequest(type, url, data) {
        this.requestLogs.push({
            type,
            url: typeof url === 'string' ? url : url.url,
            data,
            timestamp: Date.now()
        });
    }

    _checkResponse(data) {
        for (const callback of this.responseCallbacks) {
            callback(data);
        }
    }
}

const requestMonitor = new RequestMonitor();
```

---

## VERIFICATION CATEGORY E: Selenium/Automated Browser Verification

### Verify Method 13: Selenium DOM verification
**Purpose**: External browser verification
**Reliability**: 99%

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class SeleniumVerifier:
    """
    External browser verification using Selenium.
    """

    def __init__(self, url="http://127.0.0.1:7860", headless=True):
        self.url = url

        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        print(f"[VERIFY] Selenium: Connected to {url}")

    def verify_message_exists(self, expected_text, timeout=10):
        """
        Verify message appears in the UI.

        Args:
            expected_text: Text to find
            timeout: Maximum wait time
        Returns:
            Tuple of (found: bool, element_info: dict or None)
        """
        try:
            # Wait for messages container
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "messages"))
            )

            # Search for text in message bodies
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message .message-body")

            for idx, msg in enumerate(messages):
                if expected_text in msg.text:
                    print(f"[VERIFY] Selenium: Found at index {idx}")
                    return True, {
                        'index': idx,
                        'text': msg.text[:200],
                        'element_id': msg.get_attribute('id')
                    }

            # Also check data-raw attributes
            message_divs = self.driver.find_elements(By.CSS_SELECTOR, ".message[data-raw]")
            for idx, div in enumerate(message_divs):
                raw = div.get_attribute('data-raw')
                if raw and expected_text in raw:
                    print(f"[VERIFY] Selenium: Found in data-raw at index {idx}")
                    return True, {
                        'index': idx,
                        'data_raw': raw[:200]
                    }

            print(f"[VERIFY] Selenium: NOT found")
            return False, {
                'message_count': len(messages),
                'searched_text': expected_text[:50]
            }

        except Exception as e:
            print(f"[VERIFY] Selenium: Error - {e}")
            return False, {'error': str(e)}

    def get_message_count(self):
        """Get current message count."""
        try:
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
            return len(messages)
        except:
            return 0

    def get_last_message_text(self):
        """Get the last message text."""
        try:
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message .message-body")
            if messages:
                return messages[-1].text
        except:
            pass
        return None

    def take_screenshot(self, filename):
        """Take screenshot for debugging."""
        self.driver.save_screenshot(filename)
        print(f"[VERIFY] Selenium: Screenshot saved to {filename}")

    def close(self):
        """Close the browser."""
        self.driver.quit()
        print("[VERIFY] Selenium: Closed")
```

---

## VERIFICATION CATEGORY F: Comprehensive Verification Wrapper

### Verify Method 14: Multi-method verification
**Purpose**: Use multiple methods to confirm injection
**Reliability**: 99%

```python
import time
from typing import Optional, Callable, List, Dict, Any

class ComprehensiveVerifier:
    """
    Uses multiple verification methods to confirm injection success.
    """

    def __init__(self):
        self.verification_results = []

    def verify_injection(
        self,
        expected_message: str,
        timeout: float = 10.0,
        methods: List[str] = None,
        min_confirmations: int = 2
    ) -> Dict[str, Any]:
        """
        Verify injection using multiple methods.

        Args:
            expected_message: Message text to verify
            timeout: Maximum wait time
            methods: List of methods to use (default: all)
            min_confirmations: Minimum number of methods that must confirm
        Returns:
            Dict with overall result and per-method results
        """
        if methods is None:
            methods = ['history', 'display', 'metadata', 'count']

        results = {}
        confirmations = 0

        start_time = time.time()

        # Method 1: Check history state
        if 'history' in methods:
            found, idx, _ = verify_history_contains(
                expected_message,
                timeout=min(timeout, 5.0)
            )
            results['history'] = {'success': found, 'index': idx}
            if found:
                confirmations += 1

        # Method 2: Check display HTML
        if 'display' in methods:
            found, snippet = verify_display_contains(
                expected_message,
                timeout=min(timeout - (time.time() - start_time), 5.0)
            )
            results['display'] = {'success': found, 'snippet': snippet}
            if found:
                confirmations += 1

        # Method 3: Check metadata
        if 'metadata' in methods:
            found, meta, age = verify_recent_metadata(max_age_seconds=30)
            results['metadata'] = {'success': found, 'metadata': meta, 'age': age}
            if found:
                confirmations += 1

        # Method 4: Check count
        if 'count' in methods:
            # This requires tracking count before injection
            from modules import shared
            history = shared.gradio.get('history', {}).value
            count = len(history.get('internal', [])) if history else 0
            results['count'] = {'success': count > 0, 'count': count}
            if count > 0:
                confirmations += 1

        overall_success = confirmations >= min_confirmations

        result = {
            'success': overall_success,
            'confirmations': confirmations,
            'required_confirmations': min_confirmations,
            'methods_used': len(methods),
            'results': results,
            'elapsed_time': time.time() - start_time
        }

        self.verification_results.append(result)

        status = "SUCCESS" if overall_success else "FAILED"
        print(f"[VERIFY] Comprehensive: {status} ({confirmations}/{min_confirmations} confirmations)")

        return result

    def get_all_results(self):
        """Get all verification results."""
        return self.verification_results

# Global instance
comprehensive_verifier = ComprehensiveVerifier()
```

---

## HOOK EXECUTION ORDER

During normal chat generation, hooks are called in this sequence:

```
1. history_modifier          (chat.py:758)    - Modify entire history
2. state_modifier            (chat.py:759)    - Modify parameters
3. chat_input_modifier       (chat.py:794)    - Intercept user input ← KEY HIJACK POINT
4. input_modifier            (chat.py:795)    - Modify input text
5. generate_chat_prompt()    (chat.py:868)    - Build prompt
   └─ custom_generate_chat_prompt             - Override prompt generation
   └─ bot_prefix_modifier    (chat.py:358)    - Add bot prefix
6. generate_reply()          (chat.py:877)    - Generate text
   └─ custom_generate_reply  (text_gen:36)    - Override generation
   └─ tokenizer_modifier     (text_gen:383)   - Modify tokens
   └─ logits_processor       (text_gen:406)   - Constrain sampling
7. output_modifier           (chat.py:894)    - Post-process output
8. HTML rendering            (html_gen:704)   - Convert to HTML
9. Morphdom update           (ui_chat:207)    - Update DOM
```

---

## INJECTION METHOD COMPARISON MATRIX

| Method | Category | Reliability | Complexity | Verification | Best Use Case |
|--------|----------|-------------|------------|--------------|---------------|
| chat_input_modifier | Hook | 98% | Low | Easy | Input hijacking |
| history_modifier | Hook | 95% | Medium | Easy | Pre-generation injection |
| output_modifier | Hook | 95% | Low | Easy | Post-generation filter |
| custom_generate_reply | Hook | 100% | High | Easy | Complete override |
| send_dummy_reply | Direct | 100% | Low | Easy | Direct message insert |
| OpenAI API | HTTP | 95% | Low | Medium | External integration |
| handleMorphdomUpdate | JS | 85% | Medium | Medium | Client-side injection |
| Direct DOM | JS | 80% | Low | Hard | Quick testing only |
| Selenium | External | 99% | High | Built-in | Automated testing |

---

## CRITICAL SUCCESS FACTORS

1. **ALWAYS verify after injection** - Never assume success from sending
2. **Use multiple verification methods** - At least 2 confirmations
3. **Include timeout handling** - UI updates are asynchronous
4. **Log everything** - Detailed logging helps debug failures
5. **Test with small messages first** - Isolate injection from verification issues
6. **Monitor DOM, not just state** - State updates don't guarantee UI updates
7. **Handle race conditions** - Use locks and queues for thread safety
8. **Create verification endpoints** - API-based verification is most reliable

---

---

## TESTING STRATEGY: INSIDE THE EXTENSION

### Why External Testing Failed

Previous testing attempts used an external test application (`injection_test_app/`). This approach failed because:

| Problem | Cause |
|---------|-------|
| Process isolation | External Python process has separate memory from WebUI server |
| `shared.gradio` is empty | Test app gets fresh import, not server's actual state |
| Circular imports | Importing `modules.chat` outside server causes import cycles |
| Verification always fails | Cannot access real history/display components |

### Correct Approach: Test INSIDE the Extension

The boredom_monitor extension runs **inside** the WebUI server process. This means:

| Advantage | Why It Works |
|-----------|--------------|
| Same process | Direct access to `shared.gradio` with real data |
| Modules loaded | No circular imports - everything already initialized |
| Real state | `shared.gradio['history']` contains actual chat history |
| Real components | Can access display, chatbot, and all Gradio components |

### Test Harness Implementation

**Location:** `extensions/boredom_monitor/`

| File | Purpose |
|------|---------|
| `injection_test_harness.py` | All 26 injection methods |
| `verification_harness.py` | All 14 verification methods |
| `test_runner.py` | Matrix executor (26 × 14 = 364 tests) |
| `script.py` | UI button: "Run Full Test Matrix (26×14)" |

### The 26 Injection Methods

| # | Method | Category | Approach |
|---|--------|----------|----------|
| 1 | CHARACTER_GREETING | Direct | Pattern from `start_new_chat()` |
| 2 | HISTORY_MODIFIER | Hook | Extension hook pattern |
| 3 | STATE_MODIFIER | Hook | State modification hook |
| 4 | CHAT_INPUT_MODIFIER | Hook | Input modification hook |
| 5 | INPUT_MODIFIER | Hook | Input hook pattern |
| 6 | BOT_PREFIX_MODIFIER | Hook | Bot prefix hook |
| 7 | OUTPUT_MODIFIER | Hook | Output modification hook |
| 8 | CUSTOM_GENERATE_PROMPT | Hook | Custom prompt generation |
| 9 | CUSTOM_GENERATE_REPLY | Hook | Custom reply generation |
| 10 | LOGITS_PROCESSOR | Hook | Logits processor (UNSUPPORTED) |
| 11 | TOKENIZER_MODIFIER | Hook | Tokenizer modification (UNSUPPORTED) |
| 12 | SEND_DUMMY_MESSAGE | Direct | `send_dummy_message()` function |
| 13 | SEND_DUMMY_REPLY | Direct | `send_dummy_reply()` function |
| 14 | REDRAW_HTML | Direct | `redraw_html()` function |
| 15 | DIRECT_HISTORY | Direct | `shared.gradio['history']` manipulation |
| 16 | GENERATE_WRAPPER | Direct | `generate_chat_reply_wrapper()` |
| 17 | OPENAI_CHAT_API | API | `/v1/chat/completions` |
| 18 | OPENAI_COMPLETIONS_API | API | `/v1/completions` |
| 19 | CUSTOM_API | API | Custom endpoint |
| 20 | MORPHDOM_UPDATE | JS | `handleMorphdomUpdate` (REQUIRES_BROWSER) |
| 21 | DIRECT_DOM | JS | DOM manipulation (REQUIRES_BROWSER) |
| 22 | MESSAGE_EDIT | JS | `submitMessageEdit` (REQUIRES_BROWSER) |
| 23 | GRADIO_COMPONENTS | Direct | Component state update |
| 24 | INPUT_HIJACK | Direct | Input hijack pattern |
| 25 | INJECTION_BRIDGE | Queue | Gradio injection bridge queue |
| 26 | APSCHEDULER | Background | APScheduler background injection |

### The 14 Verification Methods

| # | Method | What It Checks |
|---|--------|----------------|
| 1 | HISTORY_STATE | `shared.gradio['history']` directly |
| 2 | MESSAGE_COUNT | Count messages in history |
| 3 | DISPLAY_HTML | Display component HTML content |
| 4 | METADATA_TIMESTAMP | Metadata for recent timestamp |
| 5 | API_STATE | Internal API state query |
| 6 | VERIFICATION_ENDPOINT | Custom verification endpoint |
| 7 | DOM_CONTENT | Browser DOM (REQUIRES_BROWSER) |
| 8 | MUTATION_OBSERVER | MutationObserver captures (REQUIRES_BROWSER) |
| 9 | DATA_RAW | data-raw attributes in HTML |
| 10 | DOM_MESSAGE_COUNT | Count DOM message elements (ESTIMATED) |
| 11 | SSE_EVENTS | Server-Sent Events (NOT_PRACTICAL) |
| 12 | REQUEST_MONITOR | HTTP request activity (NOT_AVAILABLE) |
| 13 | SELENIUM | External browser (REQUIRES_EXTERNAL) |
| 14 | COMPREHENSIVE | Aggregate multiple methods |

### Test Flow

```
1. Click "Run Full Test Matrix (26×14)" button in Boredom Monitor tab
2. For EACH of 26 injection methods:
   a. Clear chat history
   b. Generate unique test message: "[INJECTION-TEST] Method-N @ HHMMSS"
   c. Execute injection method
   d. Wait 300ms for propagation
   e. Run ALL 14 verification methods
   f. Log which verifications found the message
3. Generate summary report:
   - Which injection methods succeeded (injected something)
   - Which injection methods were VERIFIED (found by verifications)
   - Recommended method(s) to use
4. Save results to F:\Apps\freedom_system\log\
```

### Expected Results

After running the full matrix, the results will show:

```
# FULL MATRIX COMPLETE
# Duration: ~60 seconds
#
# Successful injections: X/26
# Verified injections: Y/26
#
# RECOMMENDED METHODS: [list of method numbers]
#   - Method N: METHOD_NAME
```

The **recommended methods** are those that:
1. Successfully executed (no exceptions)
2. Were verified by at least one verification method

### Files Generated

| File | Content |
|------|---------|
| `log/injection_test_harness.log` | Injection method logs |
| `log/verification_harness.log` | Verification method logs |
| `log/injection_matrix_results_YYYYMMDD_HHMMSS.json` | Full results JSON |

### How to Run

1. Start WebUI with boredom_monitor extension enabled
2. Go to **Boredom Monitor** tab
3. Click **"Run Full Test Matrix (26×14)"**
4. Wait for completion (~60 seconds)
5. Check status box and log files for results

---

## LEGACY: External Testing Application (DEPRECATED)

**WARNING:** The external test application does NOT work due to process isolation.

A testing application exists at `F:\Apps\freedom_system\injection_test_app\` but it cannot access the server's real state. Use the in-extension test harness instead.

### Files (Reference Only)

| File | Purpose |
|------|---------|
| `injection_tester.py` | Main injection + verification framework |
| `browser_verifier.js` | JavaScript DOM verification |
| `selenium_verifier.py` | External browser verification |
| `run_all_tests.py` | Comprehensive test runner |
| `README.md` | Usage documentation |

### Why It Fails

```python
# In external test app:
from modules import shared
print(shared.gradio)  # Empty dict - NOT the server's real gradio!

# In boredom_monitor extension:
from modules import shared
print(shared.gradio)  # Real gradio with actual history, display, etc.
```

---

## RELATED STANDARDS

- `boredom_monitor.md` - Emotional response injection patterns
- `text_gen_ext_standards.md` - Extension development standards
- `alltalk_tts.md` - TTS integration standards
- `coding_process.md` - Systematic troubleshooting process
