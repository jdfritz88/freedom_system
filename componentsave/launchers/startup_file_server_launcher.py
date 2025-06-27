import os
import http.server
import socketserver
import threading
import sys

# ========== CONFIGURATION ==========
PORT = 8753
ROOT_DIRECTORIES = ["C:/", "F:/"]
LOG_FILE = "F:/Apps/freedom_system/log/startup/FileServer_StartupLog.txt"
CORS_ENABLED = True

# ========== FILE SERVER HANDLER ==========
class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if CORS_ENABLED:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

# ========== FILE SERVER THREAD ==========
def start_file_server():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as log:
        for root in ROOT_DIRECTORIES:
            try:
                os.chdir(root)
                handler = CORSRequestHandler
                with socketserver.TCPServer(("", PORT), handler) as httpd:
                    log.write(f"[INFO] Serving {root} at http://127.0.0.1:{PORT}\n")
                    log.flush()
                    httpd.serve_forever()
            except Exception as e:
                log.write(f"[ERROR] Could not serve {root}: {e}\n")
                log.flush()

# ========== AUTOSAVE THREAD ==========
def start_autosave():
    import subprocess
    import datetime
    from win10toast import ToastNotifier

    log_path = "F:/Apps/freedom_system/autosave_log.txt"
    toaster = ToastNotifier()

    def log(msg):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a") as f:
            f.write(f"[{timestamp}] {msg}\n")
            f.flush()

    def notify(title, text):
        try:
            threading.Thread(target=toaster.show_toast, args=(title, text), kwargs={"duration": 3}).start()
        except Exception as e:
            log(f"❌ Notify failed: {e}")

    try:
        os.chdir("F:/Apps/freedom_system")
        log("Starting autosave process.")

        # Git Add
        result = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
        log("git add output:")
        log(result.stdout.strip())
        log(result.stderr.strip())
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
        log("Staged all changes.")

        # Git Commit
        commit_message = f"[Autosave] {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        log(f"Committed with message: {commit_message}")

        # Git Push
        subprocess.run(["git", "push"], check=True)
        log("Pushed to GitHub.")

        notify("Autosave Complete", "Your files have been saved and pushed to GitHub.")

    except subprocess.CalledProcessError as e:
        log(f"❌ Git command failed: {e}")
        notify("Autosave Error", str(e))
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        notify("Autosave Error", str(e))

# ========== MAIN ==========
if __name__ == "__main__":
    threading.Thread(target=start_file_server, daemon=True).start()
    threading.Thread(target=start_autosave, daemon=True).start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        sys.exit(0)
