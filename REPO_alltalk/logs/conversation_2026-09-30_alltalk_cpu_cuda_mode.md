# Conversation log: AllTalk graphics card (CUDA) / main processor (CPU) mode

**Date:** 2026-09-30
**Started from:** `REPO_koboldccp_sst_tts_media` (Claude Code session)
**Code changed in:** `REPO_alltalk` (part of the main `freedom_system` repo)
**Commit:** `fea4fbcd` (main `freedom_system` repo, branch `ooba-alltalk-update`)
**Companion logs:** `REPO_koboldccp_sst_tts_media/logs/conversation_2026-09-30_alltalk_cpu_cuda_mode.md`,
`REPO_claude_code_voice_mode/logs/conversation_2026-09-30_alltalk_cpu_cuda_mode.md`

---

## 1. The problem

**User said:** running AllTalk (Claude's voice mode) while ComfyUI makes an image is too much
for the graphics card; maybe a smaller TTS model is needed. A pasted Mistral conversation
listed smaller models.

**Found on this machine:** RTX 4080 Laptop, 12 GB. AllTalk has the XTTS, F5-TTS, Parler, Piper
and VITS engines installed; only XTTS and VITS models are downloaded. Freya is a cloned voice,
and only XTTS and F5-TTS clone voices, so Piper/VITS would lose Freya.

**User chose:** keep XTTS, run it on the main processor. Not by changing AllTalk itself: add a
main processor mode alongside CUDA mode to the launcher, with a menu to switch back and forth.

## 2. What the user asked for (all confirmed before work started)

- The mode switch lives in `launch_alltalk.bat` itself. The shortcut
  `app_cabinet\AllTalk (with my voices).lnk` is not changed (it already runs that .bat).
- Switching restarts AllTalk; that is fine.
- Every app that runs the .bat shows which mode is on and offers the switch: the shortcut
  window, the KoboldCpp launcher, and the voice mode mic panel.
- On start, the .bat gives 5 seconds to pick a mode; no key = the last saved mode.
- The KoboldCpp launcher shows that same countdown in its own window.

## 3. What was built (this repo)

**`launch_alltalk.bat`**
- 5-second startup menu: `C` graphics card, `P` main processor, `S` start now. A pick is saved.
- Starts AllTalk with `start /b` and stays in the window with a key menu: `C` / `P` switch,
  `R` restart, `Q` stop, `M` show the menu again. The menu is printed once AllTalk is listening.
- Main processor mode sets `CUDA_VISIBLE_DEVICES=-1` for AllTalk only.
- Files every app can use:
  - `settings\device_mode.txt` - the saved mode (`cuda` / `cpu`; missing = cuda). Any app
    switches by writing it; the .bat running AllTalk sees it within ~2 s and restarts.
  - `runtime\running_mode.txt`, `runtime\alltalk.pid` - what is running now.
  - `runtime\request.txt` - other apps write `restart` or `stop`.
- `--choose-mode` shows only the countdown and exits (used by the KoboldCpp launcher).
- `FREEDOM_ALLTALK_HEADLESS=1` (set by the KoboldCpp launcher) skips the countdown and key
  menu when nobody can press keys; switches made elsewhere still work.
- Refuses to start a second copy if port 7851 is already in use.
- File converted to CRLF line endings (batch labels misbehave with LF).

**`patches/alltalk_patches.py`** - XTTS `model_engine.py`: DeepSpeed is off when no graphics
card is visible (DeepSpeed only runs on one). The saved DeepSpeed setting is not touched;
checked afterwards: `model_settings.json` still has `"deepspeed_enabled": true`.

**`_boot/sitecustomize.py`** - `start /b` starts AllTalk with Ctrl+C ignored; turned back on
(`SetConsoleCtrlHandler(None, False)`), so Ctrl+C in the window stops AllTalk as before.

**`.gitignore`** - `runtime/` added.

## 4. Test results (all run on this machine)

| Test | Result |
|---|---|
| Countdown with no keyboard (`< nul`) | falls through to the saved mode at once, no stall |
| Shortcut: P in countdown | saved `cpu`, AllTalk ready in 16 s |
| Main processor mode, graphics card use | neither AllTalk process listed by `nvidia-smi` |
| Main processor mode, DeepSpeed | `/api/currentsettings` shows `false` |
| Freya, 6.7 s of speech, main processor | 14-15 s to make (native and OpenAI endpoints) |
| Same line, graphics card | 2.8-3.2 s; DeepSpeed `true` |
| C key in the shortcut window | switched to CUDA, ready in 19 s; one process on the GPU |
| Mode file written from outside | restarted in the new mode in ~30 s |
| Q key | AllTalk stopped, port free, runtime files removed, window closed |
| Ctrl+C in the shortcut window | AllTalk stopped (same "Terminate batch job" prompt as the old launcher) |

**Not tested:** AllTalk on the main processor while ComfyUI is generating. It uses no graphics
card memory, but it may compete with ComfyUI for the processor.

## 5. Found along the way

- The AllTalk folder watcher (`watcher/alltalk_folder_watcher.py`) keeps running for a while
  after AllTalk stops, by design (it checks every 30 s and stops itself). Also true with the
  old launcher.
- Test audio files written to `outputs/` were deleted. The saved mode was set back to `cuda`
  (there was no saved mode before, which meant cuda).
