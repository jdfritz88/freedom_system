"""Loaded automatically by every Python process AllTalk starts, because the
REPO_alltalk launcher puts this folder on PYTHONPATH (child processes inherit it).

It tells stock AllTalk to use REPO_alltalk, the way ComfyUI is launched with
--base-directory. See freedom_alltalk.py for what that covers.
"""
import os

if os.environ.get("FREEDOM_ALLTALK_APP") and os.environ.get("FREEDOM_ALLTALK_REPO"):
    try:
        import freedom_alltalk
    except BaseException as e:  # noqa: BLE001 - never run AllTalk unpatched
        import sys
        print(f"[REPO_alltalk] FATAL: could not load the REPO_alltalk layer: {e!r}",
              file=sys.stderr, flush=True)
        os._exit(1)
    try:
        freedom_alltalk.boot()
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        freedom_alltalk.fatal(f"REPO_alltalk layer failed: {e!r}")
