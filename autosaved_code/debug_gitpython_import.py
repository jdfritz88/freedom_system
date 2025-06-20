# debug_gitpython_import.py
import sys
import subprocess
import importlib.util

print("Python executable:", sys.executable)
print("Python version:", sys.version)

try:
    spec = importlib.util.find_spec("git")
    print("GitPython module found:", spec is not None)
except Exception as e:
    print("Error while checking GitPython module:", e)

print("\nInstalled packages:")
try:
    subprocess.run([sys.executable, "-m", "pip", "list"], check=True)
except subprocess.CalledProcessError as e:
    print("Error running pip list:", e)
except Exception as ex:
    print("Unexpected error:", ex)
