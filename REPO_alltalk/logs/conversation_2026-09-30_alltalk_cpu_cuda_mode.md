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

---

## 6. Later the same day: is there a smaller voice-cloning model, and the environment break

**Research (sources checked, not memory):** AllTalk (local copy and GitHub `alltalkbeta`) has
the same engines: XTTS, F5-TTS, Parler, Piper, VITS, plus RVC. Only XTTS and F5-TTS clone a
voice. Official file sizes: XTTS v2 2.0.3 ~2.09 GB; F5-TTS v1 Base 1.35 GB; E2-TTS 1.33 GB. A
~400 MB quantized F5-TTS exists but runs on Macs only (MLX).

**F5-TTS model download goes to the repo:** patches point AllTalk's F5-TTS download button and
loader at `REPO_alltalk/models/f5tts` (`_fa.F5_MODELS`); `models/` is git-ignored. Downloaded
through AllTalk's own page: `f5tts_v1a` (model file 1,348,435,761 bytes, same as Hugging Face);
nothing went into the app folder.

**Freya for F5-TTS:** F5-TTS needs a short clip plus its exact words; `Freya.wav` is 204 s, and
AllTalk would cut the audio to ~12 s but keep the full transcript. User chose a separate clip:
`user_voice_files/Freya_F5.wav` (10.0 s, 145.9-155.9 s of Freya.wav, cut at pauses) and
`Freya_F5.reference.txt`, transcribed with Whisper small.en; re-transcribing the clip gave the
same words. `Freya.wav` untouched.

**What broke:** the first time AllTalk loaded F5-TTS, its engine ran its own
`pip install vocos` and `pip install git+https://github.com/SWivid/F5-TTS.git` (F5-TTS 1.1.22).
That replaced 66 packages in AllTalk's environment, including PyTorch 2.2.1+cu121 -> 2.14.1+cpu,
Gradio 4.44.1 -> 6.29, FastAPI 0.112.2 -> 0.142.2, Transformers -> 5.18. AllTalk then failed to
start for every engine (`'FastAPI' object has no attribute 'route'`, then
`Could not import module 'GPT2PreTrainedModel'`).

**Also found:** AllTalk's `/api/enginereload` is broken in stock AllTalk
(`'AlltalkTTSEnginesConfigModel' object has no attribute 'save'`) - not fixed (parked).

**Repair (user chose: research, then one pass; only AllTalk's own Python/conda, by full path):**
- PyTorch 2.2.1 cu121 / torchaudio 2.2.1 / torchvision 0.17.1 reinstalled by conda with the exact
  builds in `conda-meta` (as AllTalk's `atsetup.bat` installs them).
- F5-TTS 1.1.7: the newest release whose requirements accept Gradio 4.44.1 (PyPI records:
  1.1.8+ need Gradio 5/6). Its defaults match the F5TTS_v1_Base config AllTalk loads.
- Transformers 4.46.1: `parler-tts 0.2.2` pins exactly that; it also fits XTTS (coqui-tts
  0.24.3 needs >=4.43) and PyTorch 2.2. protobuf < 5 (descript-audiotools).
- Removed packages that arrived with the broken install and nothing requires: hf-gradio,
  torch-einops-utils, eight opentelemetry packages.
- Files: `logs/repair_alltalk_env_2026-09-30.bat`, `.log`, `repair_alltalk_constraints_2026-09-30.txt`.
  `pip check` afterwards: only "deepspeed requires pynvml" (the `pynvml` module is installed,
  from nvidia-ml-py, Feb 2026 - a name-only complaint).
- Patch: the F5-TTS engine's automatic `pip install` is blocked; a missing package now stops
  with a message pointing at the constraints file.

## 7. XTTS vs F5-TTS, Freya, graphics card (2026-09-30, RTX 4080 Laptop)

Memory = total graphics card memory minus the reading with AllTalk off (796-808 MiB, steady).
Each line run 3 times; make time is the median-ish range of the runs.

| | XTTS v2 (Freya.wav) | F5-TTS v1 (Freya_F5.wav) |
|---|---|---|
| Graphics card memory, loaded and idle | 1,987-2,005 MiB | 1,513 MiB |
| Peak while speaking | 2,855-2,877 MiB | 1,597 MiB |
| Short line (19 words): time to make / audio length | 1.6-3.8 s / 6.5-8.2 s | 2.8-4.5 s / 10.7 s |
| Long line (61 words) | 3.5-4.1 s / 18-21 s | 7.5 s / 32.1 s |
| Words correct (Whisper small.en vs the text) | 100% | 100% |
| Streaming (voice mode's first choice) | yes | no (AllTalk marks it not capable) |

F5-TTS uses ~0.5 GB less idle and ~1.3 GB less at peak. It speaks ~60% slower: it copies the
pace of its reference clip, and the Freya clip is slow, emotional speech. How close each sounds
to Freya needs the user's ears: `outputs/compare_XTTS_Freya.wav`, `outputs/compare_F5-TTS_Freya_F5.wav`.
Startup lines name the model correctly for both (user check): `Loading XTTS model xttsv2_2.0.3 on cuda`
and `Model/Engine : f5tts - f5tts_v1a loading into cuda`.

**Not tested:** F5-TTS on the main processor; F5-TTS while ComfyUI is generating; Parler/Piper/VITS
engines (their models are not downloaded). AllTalk was left stopped, set to XTTS (as found).
