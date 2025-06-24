import os
import shutil
import subprocess

REPO = "C:/Users/dohze/PycharmProjects/Betting/Delta"
FILE = "PrizePicks_Arena_AllLeagues.xlsx"
BACKUP = os.path.join(REPO, "backup_" + FILE)

os.chdir(REPO)

# Backup current Excel file
if os.path.exists(FILE):
    shutil.copy2(FILE, BACKUP)
    print(f"✅ Backup created: {BACKUP}")

# Reset repo to remote
print("🧹 Resetting repo to match GitHub...")
subprocess.run(["git", "fetch", "origin"])
subprocess.run(["git", "reset", "--hard", "origin/main"])

# Restore file and push again
print("🔁 Restoring updated Excel file and pushing...")
shutil.copy2(BACKUP, FILE)
subprocess.run(["git", "add", FILE])
subprocess.run(["git", "commit", "-m", "📈 Restore updated PrizePicks file after reset"])
subprocess.run(["git", "push"])
