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
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    version_file = os.path.join(base_path, "version.txt")
    with open(version_file, "r") as f:
        return f.read().strip()
    
def check_for_update():
    try:
        latest = requests.get(GITHUB_API, timeout=5).json()["tag_name"]
        if latest == get_curr_version():
            print("Just no update")
            return False
        
        new_exe = sys.executable + ".new"
        with open(new_exe, "wb") as f:
            f.write(requests.get(DOWNLOAD_URL).content)
        bat = os.path.join(os.path.dirname(sys.executable), "update.bat")

        with open(bat, "w") as f:
            f.write(f'@echo off\ntimeout /t 2 /nobreak\nmove /y "{new_exe}" "{sys.executable}"\nstart "" "{sys.executable}"\ndel "%~f0"')

        subprocess.Popen(bat, shell=True)
        sys.exit()
    except Exception:
        print("No update or error")
        return False
