from async_tkinter_loop import async_mainloop
import sys 
import os


from frontend.gui import App
from update import check_for_update

if __name__ == "__main__":
    if getattr(sys,'frozen', False): # DO NOT REMOVE THIS LINE AT ALL COST OR IT WILL OVERRIDE YOUR PYTHON.EXE 
        check_for_update()
    app = App()
    async_mainloop(app)
