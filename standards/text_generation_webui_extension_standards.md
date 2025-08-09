# text-generation-webui Extension & Chat Tab – Combined Standards and Summary

This document merges the Freedom System’s extension coding standards with the functional overview of text-generation-webui’s Chat Tab and Extensions.

---

# Freedom System – text-generation-webui Extension Standards

This document defines the 15 official standards for creating, installing, and managing extensions within the text-generation-webui system, as used in the Freedom System project.

---

## 1. Folder Isolation Standard
Every extension must live entirely inside its own folder. No touching other extensions, no root file placement.

## 2. Environment Usage Standard
All extensions must install and run from the shared `_env` folder. System Python is never used.

## 3. Versions Control Standard
All installable packages must be declared in the shared `versions.json` file. No guesses. No floating versions.

## 4. Version Mapping Standard
If a required package isn’t listed in `versions.json`, the installer must stop and run `build_versions_map.py` automatically.

## 5. Install Enforcement Standard
Installers must install only the versions declared in `versions.json`. No newer or older versions allowed unless approved.

## 6. Unavailable Version Handling Standard
If the correct version is listed but can’t be downloaded, the installer must cancel and explain. No fallback installs.

## 7. Installer Presence Standard
Every extension must include a properly coded `install.py` that follows all standards and uses `_env`.

## 8. Styling File Standard
Each extension must include a `style.css` file—even if it’s minimal—for future UI and emotional styling.

## 9. Script Loader Override Standard
Each extension’s `script.py` must override Python’s default paths to load from its own `_env`. If missing, it must auto-repair.

## 10. Post-Install Verification Standard
Installers must confirm every required module can be imported using `verify_module_import.py`. Failures cancel the install.

## 11. Log Placement Standard
All extension logs must go directly into the root `log` folder—no subfolders allowed.

## 12. Log Format Standard
Every log must include timestamps, component names, action results, and a final `[DONE]` or `[FAIL]`.

## 13. Environment Integrity Standard
No extension is allowed to modify `_env` directly. All changes must go through installer logic only.

## 14. Shared File Protection Standard
Extensions may not edit shared files (like the mapper, import checker, or launchers) unless they inform you and explain risks.

## 15. Manual Removal Standard
Uninstall scripts are not required. Extensions are removed by deleting their folder manually.

## 16. Subprocess Management Standard
Extensions that create subprocesses must follow the AllTalk TTS Integration Standards:
- Always detect existing processes before creating new ones
- Use conditional subprocess creation to prevent duplicates
- Implement proper subprocess communication verification
- Follow established port conflict resolution protocols

## 17. API Integration Standard
Extensions with API components must implement:
- Smart connection detection with retry logic
- Progressive timeout management (1s, 2s, 4s, 8s)
- Graceful error recovery and user-friendly error messages
- Connection health monitoring and automatic reconnection

## 18. External Service Integration Standard
Extensions integrating with external services (like AllTalk TTS) must:
- Verify service availability before attempting connections
- Implement incremental testing protocols for each change
- Preserve all existing features during modifications
- Follow comprehensive logging standards for all operations

## 19. Enhanced Logging Standard (REQUIRED)
All extensions MUST implement enhanced logging from the start of development:

```python
def setup_enhanced_logging(component_name):
    """Setup enhanced logging for any extension - REQUIRED"""
    def log_enhanced(message, level="INFO", function_name="", component=component_name):
        import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = f"[{component}]"
        
        if function_name:
            prefix = f"{prefix} [{function_name}]"
        
        full_message = f"{prefix} [{level}] {message}"
        print(full_message)
        
        # Write to extension-specific log file
        log_file = f"F:/Apps/freedom_system/log/{component_name.lower()}_extension.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {full_message}\n")
        except Exception:
            pass  # Don't fail on logging failures
    
    return log_enhanced

# Usage in extension
log_enhanced = setup_enhanced_logging("EXTENSION_NAME")
```

**Logging Requirements:**
- Log all significant operations (startup, API calls, errors, state changes)
- Include function names in log entries for troubleshooting
- Use consistent log levels: INFO, WARNING, ERROR, SUCCESS, DEBUG
- Write logs to extension-specific files in the root log folder
- Never let logging failures break extension functionality

**Reference**: See `AllTalk_TTS_Integration_Standards.md` and `coding_troubleshoot_process.md` for detailed implementation patterns.


---

# Text‑Generation‑WebUI — Chat Tab & Extensions Summary

_Last updated: 2025-07-30_

---

## 📚 Chat Tab (User Interface & Behavior)

### Conversation Management
- **Switch between conversations** using tabs in the interface.
- **Rename or delete** conversations with built-in controls.
- **Template setting**: Use "start reply with" to add a fixed prefix to every bot reply.

### Chat Modes
- **Chat**: Basic persona interaction, character-driven.
- **Instruct**: Pure instruction-following using training-format prompts.
- **Chat-Instruct**: Mix of chat tone with instruction formatting.

### Token Limit
- Combined total of character info, history, user message, and bot reply cannot exceed **2048 tokens**.
- Excess tokens cause oldest history or character content to be truncated.

---

## 🔌 Official Built-In Extensions

| Extension Name       | Purpose |
|----------------------|---------|
| `openai`             | Emulates OpenAI's API (supports generate/stream endpoints). |
| `multimodal`         | Enables input of both text and images. |
| `google_translate`   | Adds automatic translation for chat inputs and outputs. |
| `silero_tts`         | Adds Silero-based speech playback (TTS). |
| `whisper_stt`        | Enables voice-to-text using Whisper via mic input. |
| `sd_api_pictures`    | Sends prompts to a Stable Diffusion image API and returns image. |
| `character_bias`     | Adds a hidden prefix to every reply for character consistency. |
| `ngrok`              | Creates remote access tunnel via ngrok (useful for headless setups). |
| `perplexity_colors`  | Colors each token by confidence level (green = confident). |

---

## 🧪 Community Extensions (Common)

- `speakLocal`: Adds lightweight TTS using system voices (offline).
- `Chatbot Clinic`: Side-by-side comparison and scoring of bot personalities.
- `code_syntax_highlight`: Enables syntax highlighting in chat code blocks.
- `dynamic_context`: Adjusts how much chat history is passed to the model.
- `LLM_Web_search`: Lets model search the web for real-time answers.
- `hello_outside_world`: Allows bot to read/write to local system files.
- `Deep Reason`: Advanced logic routing based on user input patterns.

---

## ⚙️ Extension Requirements & Installation

### Installing Requirements
Use pip to install each extension’s packages:

```bash
pip install -r extensions/<extension_name>/requirements.txt
```

**Important**: Run this inside the active text-generation-webui Conda or virtual environment.

### Docker/Containerized Setups
- Some forks require you to **merge extension requirements** into the main `requirements.txt` before running update scripts.
- Check the Docker repo or README for specific instructions.

---

## ⚠️ Conflicts & Cautions

### Prompt Formatting
- Instruct mode must use the model’s expected format (like Alpaca, Vicuna, or ChatML).
- Using wrong format = poor response quality.

### Extension Overlap
- Some community forks preload many extensions.
- Conflicts may arise if extensions use same ports, override same callbacks, or log to same files.

### Token Overflow
- Long character definitions, replies, or memory can break the 2048-token limit.
- Symptoms: truncated replies, missing personality, or empty responses.

---

## ✅ Summary

- Use the **chat tab** to switch, rename, and template conversations.
- **Built-in extensions** add core features like API, speech, images, and translation.
- **Community extensions** enhance logic, local control, and visualization.
- Install requirements carefully and monitor for token limits or extension overlaps.

---

---

## 📘 Full Wiki Insert – Chat Tab & Extensions Documentation

This section mirrors the official documentation pages for full context.

### 📖 01 – Chat Tab

Used to have multi-turn conversations with the model.

#### Input Area Buttons

- **Generate**: Sends your message and starts a reply.
- **Stop**: Interrupts reply generation at the next token.
- **Continue**: Continues the model's last response.
- **Regenerate**: Resends your last message to generate a new reply.
- **Remove last reply**: Removes the last input/output pair.
- **Replace last reply**: Replaces the last bot reply with the new input text.
- **Copy last reply**: Sends the bot’s last reply back into the input field.
- **Impersonate**: Generates a message from the user’s perspective.
- **Send dummy message**: Adds a message without generating a bot reply.
- **Send dummy reply**: Adds a fake reply as if generated.
- **Start new chat**: Starts a new chat and triggers any character greetings.
- **Send to default / notebook**: Moves current prompt to another tab.

#### Past Chats
Lets you toggle between old sessions and rename or delete them.

#### “Start reply with”
Sets a prefix for every bot reply.

#### Mode Overview
- **Chat**: For character-based models (uses persona formatting).
- **Instruct**: For models trained on Alpaca/Vicuna-style instruction formatting.
- **Chat-Instruct**: Uses instruction-style with character persona in one prompt.

##### Example Formats:
**Alpaca**:
```
Below is an instruction...

### Instruction:
Hi there!

### Response:
Hello!
```

**Llama 2**:
```
[INST] <<SYS>>
System prompt here
<</SYS>>
User message [/INST] Bot reply
```

#### Chat Style
CSS-driven visual theming. Stored in `/css/chat_style-name.css`.

#### Character Gallery
Built-in extension at `/extensions/gallery`, shows all character avatars.

---

### 📖 07 – Extensions

Extensions live in:
- `text-generation-webui/extensions`
- `text-generation-webui/user_data/extensions`

They load via:
```bash
python server.py --extensions <ext1> <ext2>
```

#### Built-in Extensions Summary

| Name               | Description |
|--------------------|-------------|
| `openai`           | Creates OpenAI-compatible API endpoints |
| `multimodal`       | Adds image + text input |
| `google_translate` | Auto-translates chat |
| `silero_tts`       | Adds audio replies using Silero |
| `whisper_stt`      | Enables mic input via Whisper |
| `sd_api_pictures`  | Requests images via Stable Diffusion |
| `character_bias`   | Adds hidden bias string at start of bot replies |
| `send_pictures`    | Upload images and auto-caption them |
| `gallery`          | Character gallery |
| `superbooga`       | Large context handling with ChromaDB |
| `ngrok`            | Enables remote access using Ngrok tunnel |
| `perplexity_colors`| Token color visualization |

#### Extension Scripting Functions

You can define the following in `script.py`:

- `setup()`: Runs once when extension is imported
- `ui()`: Adds custom Gradio controls
- `custom_css()`, `custom_js()`: Appends UI styling/scripts
- `input_modifier()`, `output_modifier()`
- `chat_input_modifier()`, `bot_prefix_modifier()`
- `state_modifier()`, `history_modifier()`
- `custom_generate_reply()`, `custom_generate_chat_prompt()`
- `tokenizer_modifier()`, `custom_tokenized_length()`

#### Example `params` usage
```python
params = {
    "display_name": "Google Translate",
    "is_tab": True,
    "language string": "jp"
}
```

To override via settings.yaml:
```yaml
google_translate-language string: 'fr'
```

#### Extension Load Priority
- Extensions in `user_data/extensions` override those in `extensions`.

#### Load Order
```bash
python server.py --extensions enthusiasm translate
```
This applies `enthusiasm` first, then `translate`.

---

