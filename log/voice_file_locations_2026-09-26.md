# Voice file locations — 2026-09-26

Where every voice `.wav` file lives after the oobabooga + AllTalk update of 2026-09-24/25
(see `conversation_2026-09-24_ooba_alltalk_update.md`), and why there are extra copies.

## How this was searched

- Scope: all of `F:\Apps`, skipping `.git`, `node_modules`, `site-packages`, `venv`, `env`,
  `installer_files`, `alltalk_environment`.
- Rule 1: every folder holding `.wav` files whose path mentions "voice" or "speaker".
- Rule 2: every folder holding the user's own voices by file name
  (Freya, Peach, Succubus, yandere, Dinner, Doggy, Game, Massage).
- Limit: a voice `.wav` in a folder whose name doesn't mention "voice"/"speaker" and isn't one of
  the named voices would not be found.
- An earlier search that only matched folders literally named `voices` missed #2
  (`voice_profiles`).

## The 8 folders

| # | Folder | .wav | Size | Whose | Notes |
|---|---|---|---|---|---|
| 1 | `F:\Apps\freedom_system\REPO_alltalk\voices` | 8 | 1.1 GB | **User** | **The working copy AllTalk uses.** Dinner, Doggy, Freya, Game, Massage, Peach, Succubus, yandere (+ 11 `.mp4` source videos). **Not in git** (user decision 2026-09-25, `REPO_alltalk\.gitignore`). The only copy of Dinner, Doggy, Game, Massage, Peach, Virgin, Workout and the two Xvideos `.mp4`. |
| 2 | `F:\Apps\freedom_system\REPO_avatarAI\backend\voice_profiles` | 4 | 18 MB | avatarAI project | Four `.wav` named by ID (e.g. `74596d4a-....wav`). Not tracked by that repo's git. Not part of this update. |
| 3 | `F:\Apps\freedom_system\REPO_oobabooga\user_data\extensions\coqui_tts_api\voices` | 5 | 1.8 MB | User's add-on | The old `coqui_tts_api` oobabooga add-on: arnold, cn-taco-ddc-gpu, female_01, female_02, sample_1. |
| 4 | `F:\Apps\freedom_system\app_cabinet\alltalk_tts\voices` | 19 | 8.9 MB | AllTalk (stock) | The developer's voices: Arnold, Clint Eastwood (2), David Attenborough, James Earl Jones, Morgan Freeman, Sophie Anderson, female_01–07, male_01–05. AllTalk lists these together with #1. |
| 5 | `F:\Apps\freedom_system\app_cabinet\text-generation-webui\extensions\coqui_tts\voices` | 3 | 1.7 MB | oobabooga (stock) | arnold, female_01, female_02 — ships with oobabooga's own coqui_tts extension. |
| 6 | `F:\Apps\freedom_system_BACKUP_ooba_v3.12\extensions_moved_out_2026-09-25\alltalk_tts\voices` | 21 | 460 MB | Backup | Old stock AllTalk voices + **identical copies** of Freya.wav, Succubus.wav/.mp4, yandere.wav/.mp4. |
| 7 | `F:\Apps\freedom_system_BACKUP_ooba_v3.12\extensions_moved_out_2026-09-25\coqui_tts_api\voices` | 5 | 1.8 MB | Backup | Identical copy of #3. |
| 8 | `F:\Apps\YuE\jacob-YuE-UI\tmp\8cbf1878f05e2e8f608fb814cf6c34f54d450c94c00485ff1d410b3a34d274ef` | 1 | 18 MB | YuE app | YuE's own temp copy of Freya.wav — **identical** to #1. |

## Why #6 and #7 exist

No program copies voice files — not the launchers, update checks, watcher or REPO_alltalk layer.
The backup folders exist because of one manual move during the update (plan step 7), which moved
the old second AllTalk copy and the old add-ons out of oobabooga's folder instead of deleting them:

```powershell
Move-Item -LiteralPath "$X\alltalk_tts" -Destination "$B\alltalk_tts"      # also boredom_monitor, coqui_tts_api
# X = F:\Apps\freedom_system\app_cabinet\text-generation-webui\extensions
# B = F:\Apps\freedom_system_BACKUP_ooba_v3.12\extensions_moved_out_2026-09-25
```

That old AllTalk copy carried its own `voices\` folder, so its Freya, Succubus and yandere are now
duplicates of the ones in #1.

## Copies of the user's own voices

| Voice | Copies on disk | Where |
|---|---|---|
| Freya.wav | 3 | #1, #6, #8 (all identical) |
| Succubus.wav / .mp4 | 2 | #1, #6 |
| yandere.wav / .mp4 | 2 | #1, #6 |
| Dinner, Doggy, Game, Massage, Peach (.wav + .mp4), Virgin.mp4, Workout.mp4, 2 Xvideos .mp4 | 1 | #1 only |

## In git

- Voice files are kept out of git (user decision, question 31). They were in the first backup
  commit of branch `ooba-alltalk-update`; that branch was rewritten on 2026-09-26 to remove them
  (two were over GitHub's 100 MB limit: yandere.wav 202.6 MB, Succubus.wav 128.3 MB) and pushed.
- The local-only branch `backup/ooba-alltalk-update-before-voice-removal` (not pushed) still
  holds 45 voice files from the old copy, including Freya, Succubus and yandere `.wav`.

## Corrections made in the conversation

- `REPO_alltalk\voices` is 1.1 GB, not "about 0.5 GB" as first stated.
