from async_tkinter_loop import async_mainloop


from frontend.gui import App

if __name__ == "__main__":
    app = App()
    async_mainloop(app)
