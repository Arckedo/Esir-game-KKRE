import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_game()

    def start_game(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, "main.py"])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"--- Changement détecté dans {event.src_path}. Relancement... ---")
            self.start_game()


if __name__ == "__main__":
    handler = ReloadHandler()
    observer = Observer()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
