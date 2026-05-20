import sys
import os
import requests
import subprocess
import traceback

GITHUB_USER = "TonyStar7"
GITHUB_REPO = "OW-rank-calculator-V2.0"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
DOWNLOAD_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download/OW_app.exe"

def get_curr_version():
    if getattr(sys, 'frozen', False):
        try:
            version_file = os.path.join(sys._MEIPASS, "version.txt")
            if os.path.exists(version_file):
                with open(version_file, "r") as f:
                    return f.read().strip()
        except Exception:
            pass
    
    # Development Mode
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return subprocess.check_output(
            ["git", "describe", "--tags", "--always"], 
            cwd=project_root, 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return "v0.0.0-dev"
    
def check_for_update():
    try:
        latest = requests.get(GITHUB_API, timeout=5).json()["tag_name"]
        if latest == get_curr_version():
            print("Just no update available")
            return False
        
        new_exe = sys.executable + ".new"

        response = requests.get(DOWNLOAD_URL)
        if response.status_code != 200:
            return False

        with open(new_exe, "wb") as f:
            f.write(response.content)

        if os.path.getsize(new_exe) < 10000000:
            os.remove(new_exe)
            return False

        bat = os.path.join(os.path.dirname(sys.executable), "update.bat")
        with open(bat, "w") as f:
            f.write(f'''@echo off
timeout /t 2 /nobreak
move /y "{new_exe}" "{sys.executable}"
if errorlevel 1 (
    echo Move failed, retrying...
    timeout /t 2 /nobreak
    move /y "{new_exe}" "{sys.executable}"
)
timeout /t 1 /nobreak
start "" "{sys.executable}"
del "%~f0"
''')

        subprocess.Popen(bat, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit()
    except Exception:
        print("No update or error")
        return False
