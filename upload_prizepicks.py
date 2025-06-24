import os
import subprocess
import datetime
import shutil

# === CONFIG ===
XLSX_FILENAME = "PrizePicks_Arena_AllLeagues.xlsx"
GITHUB_REPO_PATH = "C:/Users/dohze/PycharmProjects/Betting/Delta"
FULL_FILE_PATH = os.path.join(GITHUB_REPO_PATH, XLSX_FILENAME)

# === STEP 1: Confirm Excel file exists
if not os.path.exists(FULL_FILE_PATH):
    raise FileNotFoundError(f"❌ File not found: {FULL_FILE_PATH}")
print(f"✅ Found file: {FULL_FILE_PATH}")

# === STEP 2: Optional backup before push
backup_name = f"backup_{XLSX_FILENAME}"
backup_path = os.path.join(GITHUB_REPO_PATH, backup_name)
shutil.copyfile(FULL_FILE_PATH, backup_path)
print(f"🛡️  Backup created: {backup_path}")

# === STEP 3: Git add/commit/push just the Excel file
os.chdir(GITHUB_REPO_PATH)
subprocess.run(["git", "add", XLSX_FILENAME])

commit_msg = f"📈 Auto-update PrizePicks file ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
subprocess.run(["git", "commit", "-m", commit_msg])
push_result = subprocess.run(["git", "push"])

if push_result.returncode == 0:
    print("🚀 Excel file pushed to GitHub!")
else:
    print("❌ Git push failed.")
