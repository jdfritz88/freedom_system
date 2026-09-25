"""Oobabooga loader for the AllTalk add-on.

Oobabooga loads this file as the `alltalk_tts` extension (it lives in
REPO_oobabooga/user_data, which the oobabooga launcher passes as --user-data-dir).
It loads the real add-on - REPO_alltalk/oobabooga_extension/script.py - as if it sat
in AllTalk's own folder (app_cabinet/alltalk_tts), with the REPO_alltalk layer active
so AllTalk's code, settings, voices, outputs and logs come from REPO_alltalk.

The environment variables set here are inherited by the AllTalk server the add-on
starts, so that process gets the same REPO_alltalk layer (via _boot/sitecustomize.py).
"""
import os
import sys

_APP = r"F:\Apps\freedom_system\app_cabinet\alltalk_tts"
_REPO = r"F:\Apps\freedom_system\REPO_alltalk"
_BOOT = os.path.join(_REPO, "_boot")

os.environ["FREEDOM_ALLTALK_APP"] = _APP
os.environ["FREEDOM_ALLTALK_REPO"] = _REPO
if _BOOT not in os.environ.get("PYTHONPATH", "").split(os.pathsep):
    os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (_BOOT, os.environ.get("PYTHONPATH")) if p)
if _BOOT not in sys.path:
    sys.path.insert(0, _BOOT)

import freedom_alltalk as _freedom_alltalk  # noqa: E402

_freedom_alltalk.boot_host()

__file__ = os.path.join(_APP, "script.py")
with open(os.path.join(_REPO, "oobabooga_extension", "script.py"), "r", encoding="utf-8") as _f:
    _code = compile(_f.read(), __file__, "exec")
exec(_code, globals())
