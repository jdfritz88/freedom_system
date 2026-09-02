"""
Freedom System - Resource Monitor
Thin always-on-top widget with three thermometer bars: GPU, CPU, RAM.
Minimizes to a system-tray icon (Windows 11 has no in-taskbar meters).
Launched by the media-stack launcher; closing the launcher closes this.

Stdlib Tkinter for the widget. psutil for CPU/RAM, nvidia-ml-py for GPU.
pystray + pillow for the tray icon.
"""
import json
import os
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont

import psutil

try:
    import pynvml
    pynvml.nvmlInit()
    _NVML = pynvml.nvmlDeviceGetHandleByIndex(0)
except Exception as e:  # pragma: no cover - depends on host GPU/driver
    pynvml = None
    _NVML = None
    print(f"[MONITOR] GPU readout unavailable: {e}")

from PIL import Image, ImageDraw
import pystray

# ---------------------------------------------------------------------------
LOG_DIR = "F:/Apps/freedom_system/REPO_koboldccp_sst_tts_media/logs"
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monitor_state.json")
LOG_FILE = os.path.join(LOG_DIR, "resource_monitor.log")
REFRESH_MS = 500          # widget redraw cadence (~2 Hz)

BG = "#12141a"
FG = "#e6e6e6"
DIM = "#7a8290"
TRACK = "#242833"
GREEN = "#3fb950"
AMBER = "#d29922"
RED = "#f85149"


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
    print("[MONITOR]", msg)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
    except OSError:
        pass


def colour_for(pct):
    if pct >= 90:
        return RED
    if pct >= 70:
        return AMBER
    return GREEN


# ---------------------------------------------------------------------------
class Sampler:
    """Reads GPU / CPU / RAM. Cheap; called from the Tk loop."""

    def __init__(self):
        self.gpu_mode = load_state().get("gpu_mode", "vram")  # "vram" | "load"
        psutil.cpu_percent(interval=None)  # prime the first delta

    def read(self):
        cpu = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        ram_pct = vm.percent
        ram_txt = f"{vm.used / 1e9:.1f}/{vm.total / 1e9:.0f}G"

        gpu_pct, gpu_txt, gpu_label = 0.0, "n/a", "GPU"
        if _NVML is not None:
            try:
                if self.gpu_mode == "load":
                    gpu_pct = float(pynvml.nvmlDeviceGetUtilizationRates(_NVML).gpu)
                    gpu_txt = f"{gpu_pct:.0f}%"
                    gpu_label = "GPU\u00b7ld"
                else:
                    mem = pynvml.nvmlDeviceGetMemoryInfo(_NVML)
                    gpu_pct = 100.0 * mem.used / mem.total
                    gpu_txt = f"{mem.used / 1e9:.1f}/{mem.total / 1e9:.0f}G"
                    gpu_label = "GPU\u00b7vram"
            except Exception as e:  # pragma: no cover
                gpu_txt = "err"
                log(f"GPU read error: {e}")

        return {
            "GPU": (gpu_pct, gpu_txt, gpu_label),
            "CPU": (cpu, f"{cpu:.0f}%", "CPU"),
            "RAM": (ram_pct, ram_txt, "RAM"),
        }

    def toggle_gpu_mode(self):
        self.gpu_mode = "load" if self.gpu_mode == "vram" else "vram"
        st = load_state()
        st["gpu_mode"] = self.gpu_mode
        save_state(st)


# ---------------------------------------------------------------------------
class Bar:
    """One vertical thermometer inside the widget canvas."""

    W = 48
    PAD = 8

    def __init__(self, canvas, x):
        self.c = canvas
        self.x = x
        self.track = canvas.create_rectangle(0, 0, 0, 0, fill=TRACK, width=0)
        self.fill = canvas.create_rectangle(0, 0, 0, 0, fill=GREEN, width=0)
        self.pct_txt = canvas.create_text(0, 0, fill=FG, text="", font=("Segoe UI", 9, "bold"))
        self.val_txt = canvas.create_text(0, 0, fill=DIM, text="", font=("Segoe UI", 7))
        self.lbl_txt = canvas.create_text(0, 0, fill=DIM, text="", font=("Segoe UI", 7))

    def draw(self, top, height, pct, value_text, label):
        x0, x1 = self.x + self.PAD, self.x + self.W - self.PAD
        bar_top, bar_bot = top + 16, top + height - 24
        span = bar_bot - bar_top
        filled = span * max(0.0, min(100.0, pct)) / 100.0
        self.c.coords(self.track, x0, bar_top, x1, bar_bot)
        self.c.coords(self.fill, x0, bar_bot - filled, x1, bar_bot)
        self.c.itemconfig(self.fill, fill=colour_for(pct))
        cx = (x0 + x1) / 2
        self.c.coords(self.pct_txt, cx, top + 8)
        self.c.itemconfig(self.pct_txt, text=f"{pct:.0f}%")
        self.c.coords(self.lbl_txt, cx, bar_bot + 8)
        self.c.itemconfig(self.lbl_txt, text=label)
        self.c.coords(self.val_txt, cx, bar_bot + 17)
        self.c.itemconfig(self.val_txt, text=value_text)


class Widget:
    def __init__(self, root, sampler, on_quit):
        self.root = root
        self.sampler = sampler
        self.on_quit = on_quit
        self.hidden = False

        w = Bar.W * 3
        h = 168
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        try:
            root.attributes("-alpha", 0.95)
        except tk.TclError:
            pass
        st = load_state()
        x = st.get("x", root.winfo_screenwidth() - w - 24)
        y = st.get("y", 80)
        root.geometry(f"{w}x{h}+{x}+{y}")
        root.configure(bg=BG)

        self.canvas = tk.Canvas(root, width=w, height=h, bg=BG, highlightthickness=1,
                                highlightbackground="#2b2f3a")
        self.canvas.pack(fill="both", expand=True)
        self.bars = [Bar(self.canvas, i * Bar.W) for i in range(3)]
        self._w, self._h = w, h

        for seq in ("<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"):
            self.canvas.bind(seq, self._drag)
        self.canvas.bind("<Button-3>", self._menu)
        self.canvas.bind("<Double-Button-1>", lambda e: self.sampler.toggle_gpu_mode())
        self._drag_off = (0, 0)

        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="GPU: VRAM / Load", command=self.sampler.toggle_gpu_mode)
        self.menu.add_command(label="Hide to tray", command=self.hide)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.on_quit)

        self.tick()

    # -- dragging ----------------------------------------------------------
    def _drag(self, e):
        if e.type == tk.EventType.ButtonPress:
            self._drag_off = (e.x, e.y)
        elif e.type == tk.EventType.Motion:
            nx = self.root.winfo_pointerx() - self._drag_off[0]
            ny = self.root.winfo_pointery() - self._drag_off[1]
            self.root.geometry(f"+{nx}+{ny}")
        else:  # release
            st = load_state()
            st["x"] = self.root.winfo_x()
            st["y"] = self.root.winfo_y()
            save_state(st)

    def _menu(self, e):
        self.menu.tk_popup(e.x_root, e.y_root)

    # -- visibility ------------------------------------------------------
    def hide(self):
        self.hidden = True
        self.root.withdraw()

    def show(self):
        self.hidden = False
        self.root.deiconify()
        self.root.attributes("-topmost", True)

    # -- redraw loop ----------------------------------------------------
    def tick(self):
        data = self.sampler.read()
        self.latest = data
        for bar, key in zip(self.bars, ("GPU", "CPU", "RAM")):
            pct, val, lbl = data[key]
            bar.draw(0, self._h, pct, val, lbl)
        self.root.after(REFRESH_MS, self.tick)


# ---------------------------------------------------------------------------
class Tray:
    """Single tray icon rendering all three bars (Win11 has no taskbar meters)."""

    SIZE = 64

    def __init__(self, widget, on_quit):
        self.widget = widget
        self.on_quit = on_quit
        self.icon = pystray.Icon(
            "freedom_resource_monitor",
            self._render({"GPU": (0, "", ""), "CPU": (0, "", ""), "RAM": (0, "", "")}),
            "Resource Monitor",
            menu=pystray.Menu(
                pystray.MenuItem("Show / hide widget", self._toggle, default=True),
                pystray.MenuItem("GPU: VRAM / Load", lambda: self.widget.sampler.toggle_gpu_mode()),
                pystray.MenuItem("Quit", lambda: self.on_quit()),
            ),
        )
        self._stop = False

    def _toggle(self):
        if self.widget.hidden:
            self.widget.show()
        else:
            self.widget.hide()

    def _render(self, data):
        img = Image.new("RGBA", (self.SIZE, self.SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cols = 3
        gap = 4
        bw = (self.SIZE - gap * (cols + 1)) // cols
        for i, key in enumerate(("GPU", "CPU", "RAM")):
            pct = max(0.0, min(100.0, data[key][0]))
            x0 = gap + i * (bw + gap)
            x1 = x0 + bw
            d.rectangle([x0, 4, x1, self.SIZE - 4], fill=(40, 44, 55, 255))
            fh = (self.SIZE - 8) * pct / 100.0
            col = colour_for(pct)
            rgb = tuple(int(col[j:j + 2], 16) for j in (1, 3, 5)) + (255,)
            d.rectangle([x0, self.SIZE - 4 - fh, x1, self.SIZE - 4], fill=rgb)
        return img

    def refresh_loop(self):
        while not self._stop:
            try:
                data = getattr(self.widget, "latest", None)
                if data:
                    self.icon.icon = self._render(data)
                    g, c, r = (data[k][0] for k in ("GPU", "CPU", "RAM"))
                    self.icon.title = f"GPU {g:.0f}%  CPU {c:.0f}%  RAM {r:.0f}%"
            except Exception:
                pass
            time.sleep(1.0)

    def run(self):
        threading.Thread(target=self.refresh_loop, daemon=True).start()
        self.icon.run()

    def stop(self):
        self._stop = True
        try:
            self.icon.stop()
        except Exception:
            pass


# ---------------------------------------------------------------------------
def main():
    log("Resource monitor starting")
    root = tk.Tk()
    root.title("Resource Monitor")
    sampler = Sampler()

    state = {"tray": None}

    def quit_all():
        log("Resource monitor exiting")
        if state["tray"]:
            state["tray"].stop()
        try:
            root.destroy()
        except tk.TclError:
            pass
        os._exit(0)

    widget = Widget(root, sampler, quit_all)
    root.protocol("WM_DELETE_WINDOW", widget.hide)

    if "--no-tray" not in sys.argv:
        tray = Tray(widget, quit_all)
        state["tray"] = tray
        threading.Thread(target=tray.run, daemon=True).start()

    root.mainloop()


if __name__ == "__main__":
    main()
