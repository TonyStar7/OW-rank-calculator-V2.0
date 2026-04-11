from async_tkinter_loop import async_mainloop
import sys 
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.append(PROJECT_ROOT)

from frontend.gui import App

if __name__ == "__main__":
    app = App()
    async_mainloop(app)



    