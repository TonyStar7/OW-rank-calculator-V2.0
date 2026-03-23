from async_tkinter_loop import async_mainloop
from backend.src.scrap import *
from frontend.gui import App


if __name__ == "__main__":
    try:
        app = App()
        async_mainloop(app)
    except Exception as e:
        print(f"ERROR: {e}")