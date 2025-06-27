import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import tkinter as tk
from componentsave.queue import Queue

class DashboardUpdateQueue:
    def __init__(self, app):
        self.queue = Queue()
        self.app = app
        self.poll()

    def push(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def poll(self):
        while not self.queue.empty():
            func, args, kwargs = self.queue.get()
            func(*args, **kwargs)
        self.app.after(50, self.poll)
