"""REPO_alltalk runtime layer for stock AllTalk v2.

Loaded by sitecustomize.py in every AllTalk process started through REPO_alltalk.
AllTalk's own folder (app_cabinet/alltalk_tts) is never written to by the code paths
handled here:

- Settings files AllTalk reads/writes by path are served from REPO_alltalk/settings.
- voices/ is a union: stock voices stay in the app folder, user voices live in
  REPO_alltalk/voices. Listings show both; anything written goes to the repo.
- Stock code is patched in memory (patches/alltalk_patches.py) and user-owned
  replacement files are loaded from REPO_alltalk/overrides, both compiled under the
  app file's own path so AllTalk's relative lookups keep working.

Any mismatch between a patch and the stock code stops the process with a message
naming the patch, instead of running AllTalk without the Freedom changes.
"""
import builtins
import io
import os
import sys

APP = os.path.abspath(os.environ["FREEDOM_ALLTALK_APP"])
REPO = os.path.abspath(os.environ["FREEDOM_ALLTALK_REPO"])
SETTINGS = os.path.join(REPO, "settings")
LOGS = os.path.join(REPO, "logs")
OUTPUTS = os.path.join(REPO, "outputs")
TRANSCRIPTIONS = os.path.join(REPO, "transcriptions")
APP_VOICES = os.path.join(APP, "voices")
REPO_VOICES = os.path.join(REPO, "voices")

_nc = os.path.normcase
_APP_NC = _nc(APP) + os.sep
_APP_VOICES_NC = _nc(APP_VOICES)

# Settings files AllTalk opens directly by path (relative to the app folder).
_SETTINGS_FILES = {
    _nc(os.path.join("system", "TGWUI_Extension", "tgwui_remote_config.json")),
    _nc("confignew.json"),
    _nc(os.path.join("system", "tts_engines", "tts_engines.json")),
    _nc(os.path.join("system", "tts_engines", "parler", "parler_voices.json")),
}
_ENGINES_DIR_NC = _nc(os.path.join("system", "tts_engines")) + os.sep


def log(msg):
    print(f"[REPO_alltalk] {msg}", flush=True)


def fatal(msg):
    # Python treats errors raised inside sitecustomize as warnings and carries on,
    # which would run AllTalk without the Freedom changes. Stop instead.
    print(f"[REPO_alltalk] FATAL: {msg}", file=sys.stderr, flush=True)
    os._exit(1)


# --------------------------------------------------------------------------- paths

def _abs(path):
    if isinstance(path, int):
        return None
    try:
        path = os.fspath(path)
    except TypeError:
        return None
    if isinstance(path, bytes):
        return None
    return os.path.abspath(path)


def _app_rel(abs_path):
    """Path relative to the app folder (normcased), or None if outside it."""
    n = _nc(abs_path)
    if n.startswith(_APP_NC):
        return n[len(_APP_NC):]
    return None


def settings_target(abs_path):
    """REPO settings path for an app settings file, else None."""
    rel = _app_rel(abs_path)
    if rel is None:
        return None
    is_model_settings = (rel.startswith(_ENGINES_DIR_NC)
                         and rel.endswith(os.sep + "model_settings.json")
                         and rel.count(os.sep) == 3)
    if rel in _SETTINGS_FILES or is_model_settings:
        target = os.path.join(SETTINGS, abs_path[len(APP) + 1:])
        if not os.path.exists(target):
            # First use of a settings file the repo has no copy of yet: seed it
            # from the stock file (reading the app folder, never writing it).
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with _real_open(abs_path, "rb") as src, _real_open(target, "wb") as dst:
                dst.write(src.read())
            log(f"seeded repo settings from stock: {rel}")
        return target
    return None


def _in_app_voices(abs_path):
    n = _nc(abs_path)
    return n == _APP_VOICES_NC or n.startswith(_APP_VOICES_NC + os.sep)


def _repo_voice_twin(abs_path):
    return REPO_VOICES + abs_path[len(APP_VOICES):]


def voice_path(*parts):
    """Real path of a voice file/folder: the repo copy if it exists, else stock."""
    repo = os.path.join(REPO_VOICES, *parts)
    if _real_exists(repo):
        return repo
    return os.path.join(APP_VOICES, *parts)


# ------------------------------------------------------------- filesystem shims

_real_open = builtins.open
_real_listdir = os.listdir
_real_scandir = os.scandir
_real_stat = os.stat
_real_remove = os.remove
_real_unlink = os.unlink


def _real_exists(p):
    try:
        _real_stat(p)
        return True
    except OSError:
        return False


def _redirect_read(abs_path):
    t = settings_target(abs_path)
    if t:
        return t
    if _in_app_voices(abs_path) and not _real_exists(abs_path):
        twin = _repo_voice_twin(abs_path)
        if _real_exists(twin):
            return twin
    return None


def _redirect_write(abs_path):
    t = settings_target(abs_path)
    if t:
        return t
    if _in_app_voices(abs_path):
        twin = _repo_voice_twin(abs_path)
        os.makedirs(os.path.dirname(twin), exist_ok=True)
        return twin
    return None


def _open(file, mode="r", *args, **kwargs):
    p = _abs(file)
    if p is not None and _nc(p).startswith(_APP_NC):
        writing = any(c in mode for c in "wax+")
        t = _redirect_write(p) if writing else _redirect_read(p)
        if t:
            file = t
    return _real_open(file, mode, *args, **kwargs)


def _listdir(path="."):
    p = _abs(path)
    names = _real_listdir(path)
    if p is not None and _in_app_voices(p):
        twin = _repo_voice_twin(p)
        if _real_exists(twin):
            have = set(names)
            names = names + [n for n in _real_listdir(twin) if n not in have]
    return names


class _UnionScandir:
    def __init__(self, first, second):
        self._its = [first, second]

    def __iter__(self):
        seen = set()
        for it in self._its:
            if it is None:
                continue
            for entry in it:
                if entry.name not in seen:
                    seen.add(entry.name)
                    yield entry

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        for it in self._its:
            if it is not None:
                it.close()


def _scandir(path="."):
    p = _abs(path)
    if p is not None and _in_app_voices(p):
        twin = _repo_voice_twin(p)
        if _real_exists(twin):
            first = _real_scandir(path) if _real_exists(p) else None
            return _UnionScandir(first, _real_scandir(twin))
    return _real_scandir(path)


def _stat(path, *args, **kwargs):
    p = _abs(path)
    if p is not None and _nc(p).startswith(_APP_NC):
        t = settings_target(p)
        if t:
            return _real_stat(t, *args, **kwargs)
        if _in_app_voices(p):
            try:
                return _real_stat(path, *args, **kwargs)
            except FileNotFoundError:
                return _real_stat(_repo_voice_twin(p), *args, **kwargs)
    return _real_stat(path, *args, **kwargs)


def _make_remove(real):
    def remove(path, *args, **kwargs):
        p = _abs(path)
        if p is not None and _in_app_voices(p) and not _real_exists(p):
            path = _repo_voice_twin(p)
        return real(path, *args, **kwargs)
    return remove


def _make_check(test):
    # Python 3.12+ on Windows checks existence with C fast paths that skip os.stat,
    # so exists/isfile/isdir are routed through the voices/settings shim explicitly.
    import stat as _st

    def check(path):
        try:
            return test(_st, _stat(path).st_mode)
        except (OSError, ValueError, TypeError):
            return False
    return check


def install_shims():
    builtins.open = _open
    io.open = _open
    os.listdir = _listdir
    os.scandir = _scandir
    os.stat = _stat
    os.remove = _make_remove(_real_remove)
    os.unlink = _make_remove(_real_unlink)
    os.path.exists = _make_check(lambda st, m: True)
    os.path.lexists = _make_check(lambda st, m: True)
    os.path.isfile = _make_check(lambda st, m: st.S_ISREG(m))
    os.path.isdir = _make_check(lambda st, m: st.S_ISDIR(m))
    # Python 3.13's glob (used by Path.glob) keeps its own references to os.scandir /
    # os.path.lexists, bound when glob is first imported - often before this layer is
    # installed (oobabooga imports it at startup). Point those at the shims too.
    import glob as _glob
    for _cls in ("_StringGlobber",):
        _g = getattr(_glob, _cls, None)
        if _g is not None:
            if "scandir" in vars(_g):
                _g.scandir = staticmethod(_scandir)
            if "lexists" in vars(_g):
                _g.lexists = staticmethod(os.path.lexists)


# ------------------------------------------------ patches, overrides, import hook

def install_code_hooks():
    import importlib.abc
    import importlib.machinery
    import importlib.util

    sys.path.insert(0, os.path.join(REPO, "patches"))
    from alltalk_patches import PATCHES

    overrides_dir = os.path.join(REPO, "overrides")

    def override_for(app_path):
        rel = os.path.relpath(app_path, APP)
        if rel.startswith(".."):
            return None
        cand = os.path.join(overrides_dir, rel)
        return cand if _real_exists(cand) else None

    def code_for(app_path):
        """Source for an app file: the repo override if one exists, else stock
        with this file's patches applied. Compiled under the app path."""
        rel = os.path.relpath(app_path, APP).replace(os.sep, "/")
        override = override_for(app_path)
        src_path = override or app_path
        with _real_open(src_path, "r", encoding="utf-8") as f:
            source = f.read()
        if override:
            log(f"using repo override for {rel}")
        else:
            patches = PATCHES.get(rel, [])
            for i, (find, replace) in enumerate(patches, 1):
                count = source.count(find)
                if count != 1:
                    fatal(f"patch {rel} #{i} expected its target once in stock AllTalk, "
                          f"found it {count} times - AllTalk changed this code; update the patch.")
                source = source.replace(find, replace)
            if patches:
                log(f"applied {len(patches)} patches to {rel}")
        return compile(source, app_path, "exec")

    def handled(app_path):
        rel = os.path.relpath(app_path, APP).replace(os.sep, "/")
        return rel in PATCHES or override_for(app_path) is not None

    class Loader(importlib.machinery.SourceFileLoader):
        def get_code(self, fullname):
            return code_for(self.path)

    class Finder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path, target=None):
            parts = fullname.split(".")
            # Where this module would live in the app folder, for every app root
            # on sys.path (overrides can exist for files the app doesn't have).
            search = path if path is not None else sys.path
            for base in search:
                try:
                    base = os.path.abspath(base)
                except TypeError:
                    continue
                if _app_rel(base + os.sep) is None and _nc(base) != _nc(APP):
                    continue
                name = parts[-1] + ".py"
                app_path = os.path.join(base, name)
                if (_real_exists(app_path) or override_for(app_path)) and handled(app_path):
                    return importlib.util.spec_from_file_location(
                        fullname, app_path, loader=Loader(fullname, app_path))
            return None

    sys.meta_path.insert(0, Finder())
    return code_for, handled


def run_app_file_as_main(code_for, handled):
    """`python <app file>` (as AllTalk's script.py starts tts_server.py, firstrun.py,
    etc.): run it from the app folder, patched."""
    main = sys.argv[0] if sys.argv else ""
    if not main or not main.endswith(".py"):
        return
    main_abs = os.path.abspath(main)
    if _app_rel(main_abs) is None:
        return
    os.chdir(APP)
    if not handled(main_abs):
        return
    import types
    sys.path.insert(0, os.path.dirname(main_abs))
    mod = types.ModuleType("__main__")
    mod.__file__ = main_abs
    mod.__builtins__ = builtins
    sys.modules["__main__"] = mod
    exec(code_for(main_abs), mod.__dict__)
    sys.exit(0)


def add_env_dlls():
    """Make AllTalk's conda DLLs (e.g. nvrtc-builtins) findable without
    `conda activate`, for AllTalk processes started by oobabooga."""
    env = os.path.join(APP, "alltalk_environment", "env")
    if _nc(os.path.abspath(sys.prefix)) != _nc(env):
        return
    dirs = [os.path.join(env, d) for d in ("Library\\bin", "bin", "Scripts", "")]
    os.environ["PATH"] = os.pathsep.join(dirs + [os.environ.get("PATH", "")])
    for d in dirs:
        if os.path.isdir(d):
            try:
                os.add_dll_directory(d)
            except OSError:
                pass


def boot():
    for d in (LOGS, OUTPUTS, REPO_VOICES, TRANSCRIPTIONS):
        os.makedirs(d, exist_ok=True)
    add_env_dlls()
    install_shims()
    code_for, handled = install_code_hooks()
    run_app_file_as_main(code_for, handled)


_host_booted = False


def boot_host():
    """For a host program that loads AllTalk code into its own process (oobabooga's
    AllTalk add-on): same redirects and patches, but no chdir and no takeover of the
    host's own __main__."""
    global _host_booted
    if _host_booted:
        return
    for d in (LOGS, OUTPUTS, REPO_VOICES, TRANSCRIPTIONS):
        os.makedirs(d, exist_ok=True)
    install_shims()
    install_code_hooks()
    _host_booted = True
