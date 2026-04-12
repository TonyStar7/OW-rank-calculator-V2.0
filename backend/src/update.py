import sys
import os
import requests

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.append(PROJECT_ROOT)

CURRENT_VERSION = "1.0.0"
GIT_VERSION_URL = "https://github.com/TonyStar7/OW-rank-calculator-V2.0/blob/main/version.txt"

def is_exe():
    IS_EXE = getattr(sys, 'frozen', False)
    return IS_EXE

def update_check():
    git_page = requests.get(GIT_VERSION_URL)
    print(git_page.status_code)
    if git_page.status_code == 200:
        git_version = git_page.text.strip()
        print(f"git version: {git_version}")
        if git_version != CURRENT_VERSION:
            return True
        
update_check()
