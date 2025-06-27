import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# face_training_launcher.py
# GUI prompt before A1111 startup
# Handles resume or new face training session

import tkinter as tk
from componentsave.tkinter import filedialog
import subprocess
import os
import threading

DEFAULT_PATH = "F:/Apps/FaceTrainer"
DEFAULT_WEIGHTS = "F:/Apps/freedom_system/weights/freedom_face.safetensors"
LAUNCHER_SCRIPT = os.path.join(DEFAULT_PATH, "FaceTrainingRoutine.py")

class FaceTrainerPrompt:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FaceTrainer Launcher")
        self.root.geometry("400x160")

        self.label = tk.Label(self.root, text="Do you want to start a face training session?")
        self.label.pack(pady=10)

        self.resume_button = tk.Button(self.root, text="Resume", command=self.resume_session)
        self.new_button = tk.Button(self.root, text="New", command=self.new_session)
        self.skip_button = tk.Button(self.root, text="Skip", command=self.skip)

        self.resume_button.pack()
        self.new_button.pack()
        self.skip_button.pack(pady=10)

        self.timer = self.root.after(5000, self.auto_skip)
        self.root.mainloop()

    def resume_session(self):
        folder = DEFAULT_PATH
        self.run_face_trainer(folder, resume=True)

    def new_session(self):
        folder = filedialog.askdirectory(initialdir="F:/", title="Select New Face Training Folder")
        if folder:
            self.run_face_trainer(folder, resume=False)

    def skip(self):
        self.root.destroy()

    def auto_skip(self):
        print("[FaceTrainer] No input. Skipping after 5 seconds...")
        self.root.destroy()

    def run_face_trainer(self, folder, resume):
        args = ["python", LAUNCHER_SCRIPT, folder]
        if resume:
            args.append("--resume")
        threading.Thread(target=lambda: subprocess.run(args)).start()
        self.root.destroy()

if __name__ == "__main__":
    FaceTrainerPrompt()
