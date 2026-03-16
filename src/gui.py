import customtkinter as ctk
from PIL import Image, ImageTk
import os


font_size = 16
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PAR_DIR = os.path.dirname(FILE_DIR)
IMG_DIR = os.path.join(PAR_DIR, "assets")

CROSS_IMG_PATH = os.path.join(IMG_DIR, "red_cross.png")
TANK_IMG = os.path.join(IMG_DIR, "Tank_icon.png")
DPS_IMG = os.path.join(IMG_DIR, "Damage_icon.png")
SUPPORT_IMG = os.path.join(IMG_DIR, "Support_icon.png")
OPEN_QUEUE_IMG = os.path.join(IMG_DIR, "Open_Queue_icon.png")



class Left_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)  # entry expands
        self.grid_columnconfigure(1, weight=0)  # button stays compact

        entry = ctk.CTkEntry(
            self,
            placeholder_text="Enter battletag",
            font=ctk.CTkFont(size=font_size)
        )
        entry.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ew")

        button = ctk.CTkButton(
            self, 
            text="Add player", 
            fg_color="#116113", 
            hover_color="#1B8F1B",
            font=ctk.CTkFont(size=font_size)
        )
        button.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="w")

class Right_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        button = ctk.CTkButton(self,
                                text="Refresh",
                                fg_color="#1a498a",
                                hover_color="#225bab",
                                font=ctk.CTkFont(size=font_size)
                                )
        button.grid(row=0, column=2, padx=20, pady=20, sticky="n")

class Scrollable_Frame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

class Player_list_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        categories = ["Delete", "Tag", "Username", "Tank", "Dps", "Support", "OQ", "Owner", "Date Added"]
        for i in range(len(categories)):
            if i == 0:
                self.grid_columnconfigure(i, weight=0)
            elif categories[i] in ["Tank", "Dps", "Support", "OQ"]:
                self.grid_columnconfigure(i, weight=1)
                img_paths = {"Tank": TANK_IMG, 
                            "Dps": DPS_IMG, 
                            "Support": SUPPORT_IMG, 
                            "OQ": OPEN_QUEUE_IMG}
                Button = ctk.CTkButton(self,
                                        text=categories[i],
                                        image=ImageTk.PhotoImage(Image.open(img_paths[categories[i]]).resize((20, 20))),
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        )
                Button.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            else:
                self.grid_columnconfigure(i, weight=1)
                Button = ctk.CTkButton(self, text=categories[i], font=ctk.CTkFont(size=14, weight="bold"))
                Button.grid(row=0, column=i, padx=10, pady=10, sticky="w")

class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Top row: controls (add/refresh)
        self.grid_rowconfigure(0, weight=1)
        # Bottom row: main content (scrollable list)
        self.grid_rowconfigure(1, weight=0)

        # Column layout: side panels smaller, middle expands
        self.grid_columnconfigure(0, weight=1)  # left-side add section
        self.grid_columnconfigure(1, weight=10)  # middle scrollable content
        self.grid_columnconfigure(2, weight=1)  # right-side refresh section

        self.add_section = Left_Frame(self)
        self.add_section.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.list_frame = Scrollable_Frame(self)
        self.list_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.player_list = Player_list_Frame(self.list_frame)
        self.player_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.refresh_section = Right_Frame(self)
        self.refresh_section.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        self._set_appearance_mode("dark")
        self.title("Overwatch rank calculator 2.0")
        self.geometry("1920x1080")


