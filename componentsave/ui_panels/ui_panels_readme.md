# 🧩 UI Panels Module Overview

This folder contains all logic for the Freedom System's **user interface controls**, including real-time emotion display, toggle switches, and override inputs. All modules are optimized for:

- ✅ **Low CPU usage** (throttled background threads)
- ✅ **Minimal RAM footprint** (no memory-heavy loops)
- ✅ **Battery efficiency** (1–1.5 sec sleep cycles)
- ✅ **Thread-safe interaction** (via locks)

## 📁 Modules Included

| File                       | Purpose                                   |
|----------------------------|-------------------------------------------|
| `ui_layout_core.py`        | Defines UI zone layout modes (`wide`, etc.) |
| `ui_master_orb.py`         | Displays dominant + blended emotions      |
| `ui_dropdown_emotions.py`  | Lists all active emotions with scores     |
| `ui_toggle_controls.py`    | On/off toggles (legend, preview, etc.)    |
| `ui_override_controls.py`  | Manually set or clear emotional overrides |
| `ui_status_area.py`        | Shows live system status (e.g. running)   |

---

## 🧠 Best Practices

- All update threads are `daemon=True` to avoid hanging on exit.
- `threading.Lock()` ensures safe shared-state access.
- Modules return cached values for instant GUI rendering.
- None of these modules poll faster than 1/sec.

---

You can call any module's `init_*()` function to start tracking, and `get_*()` to retrieve live UI-safe output.

---

_Last updated: 2025-06-21_

**Freedom System UI is now fully modular and laptop-optimized.**
