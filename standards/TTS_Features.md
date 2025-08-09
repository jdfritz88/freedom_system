 TTS Features in the Freedom Project (Confirmed)
🎤 1. GPU-Only TTS Execution
You specified no CPU fallback for TTS
All models (e.g., XTTS, RVC) must run strictly on GPU
Config enforced during launcher and batch setup

🧠 2. Emotion State Locking During Speech
Voice output must respect the active emotion state
No emotion shifts mid-line
State is frozen at speech trigger time and released on completion

🔁 3. API Speech System
Implemented a API system to handle TTS input
Prevents overlapping audio, ensures proper timing
Queue integrated with emotional control logic

⏱️ 4. Throttled Trigger Timing
Delays between speech triggers are controlled
Prevents spamming TTS engine, especially during fast message cycles
Part of the lag-reduction strategy for Coqui-style models

⚙️ 5. Launch Integration
TTS launches via a bat
Voice system is one of the core services launched in sequence
All logs routed to F:\Apps\freedom_system\log\ no subfolder

🛑 6. Toggles for TTS GUI
TTS audio in web UI (Coqui or Bark) includes:
✅ “Activate TTS” checkbox
✅ “Autoplay” checkbox (adds autoplay to <audio> tag)
Toggled via Gradio interface

🔍 7. Emotion-Aware Voice Control
Voice tone aligns with top 2 emotion states
Positive emotions always outweigh negative ones when intensity is equal
Affects tone, pacing, and vocal quality

🎯 8. Backdoor Access
Assistant (me) has backdoor access to modify TTS configuration or inject voices
Always subject to your manual enable/disable switch

🧪 09. Voice Trainer Voice Interop
Voice emotion states will sync with facial motion and expression
Requires final hook-up of Voice Trainer’s emotion input line

🧰 10. Model Validation and Auto-Repair (Planned)
If TTS fails, the system can:
Auto-check verify_module_import.py
Rebuild the speech environment
Fallback to recovery mode and notify you

🔗 11. AllTalk TTS Integration Standards
For complex TTS integrations (like AllTalk with text-generation-webui):
- Follow subprocess management and detection protocols
- Implement smart connection detection with retry logic
- Use proper port conflict resolution (7851/7852)
- Maintain comprehensive operation logging
- Preserve CUDA support and all existing features

**Reference**: See `AllTalk_TTS_Integration_Standards.md` for detailed integration patterns and troubleshooting practices.

