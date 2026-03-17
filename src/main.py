from async_tkinter_loop import async_mainloop
from scrap import *
from gui import App


if __name__ == "__main__":
    try:
        app = App()
        async_mainloop(app)
    except Exception as e:
        print(f"ERROR: {e}")