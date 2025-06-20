# This script sets your Git identity globally.
# You only need to run it once on this machine.

import subprocess

subprocess.run(["git", "config", "--global", "user.name", "Jacob Esperanto"], check=True)
subprocess.run(["git", "config", "--global", "user.email", "jdfritz88@gmail.com"], check=True)

print("✅ Git global identity is now set to Jacob Esperanto <jdfritz88@gmail.com>")
