import customtkinter as ctk
from PIL import Image
import os
import processor as process
from async_tkinter_loop import async_handler
import player_list as data
import connect_database as db


font_size = 17
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
        
        self.default_text = "Enter BattleTag"
        self.battletag_var = ctk.StringVar(value=self.default_text)
        self.add_entry = ctk.CTkEntry(
            self,
            textvariable=self.battletag_var,
            font=ctk.CTkFont(size=font_size),
            fg_color="transparent",
            text_color="#9c9c9c"
        )
        self.add_entry.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ew")

        self.button = ctk.CTkButton(
            self, 
            text="Add player", 
            fg_color="#116113", 
            hover_color="#1B8F1B",
            font=ctk.CTkFont(size=font_size, weight="bold"),
            command=async_handler(self.on_add_click)
        )
        self.button.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="w")

        self.bind("<Button-1>", self.drop_focus)
        self.add_entry.bind("<FocusIn>", self.handle_focus_in)
        self.add_entry.bind("<FocusOut>", self.handle_focus_out)

    def drop_focus(self, event):
        # When you click the background, this gives focus to the frame
        # which forces the entry to "FocusOut"
        self.focus()

    def handle_focus_in(self, event):
        if self.battletag_var.get() == self.default_text:
            self.battletag_var.set("")
            self.add_entry.configure(text_color="white")

    def handle_focus_out(self, event):
        if self.battletag_var.get().strip() == "": # strip() handles spaces
            self.battletag_var.set(self.default_text)
            self.add_entry.configure(text_color="#9c9c9c")

    async def on_add_click(self):
        battletag = self.add_entry.get()
        if battletag != self.default_text and battletag.strip():
            self.button.configure(state="disabled", text="Searching...")
            
            success = await process.add_player(battletag)

            if success:
                self.master.player_list.update_table()
            
            self.button.configure(state="normal", text="Add player")
            self.battletag_var.set(self.default_text)


class Right_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.button = ctk.CTkButton(self,
                                text="Refresh",
                                fg_color="#1a498a",
                                hover_color="#225bab",
                                font=ctk.CTkFont(size=font_size, weight="bold"),
                                command=async_handler(self.on_refresh_click)
                                )
        self.button.grid(row=0, column=2, padx=20, pady=20, sticky="n")

    async def on_refresh_click(self):
        self.button.configure(state="disabled", text="Refreshing...")
        success = await process.refresh_players()
        if success:
            self.master.player_list.update_table() 
        self.button.configure(state="normal", text="Refresh")

class Scrollable_Frame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

class Player_list_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.categories = ["Delete", "Tag", "Username", "Tank", "Dps", "Support", "OQ", "Owner", "Date Added"]
        self.tank_idx = self.categories.index("Tank")
        self.damage_idx = self.categories.index("Dps")
        self.support_idx = self.categories.index("Support")
        self.open_queue_idx = self.categories.index("OQ")
        
        for i in range(len(self.categories)): #Categories row
            if i == 0:
                self.grid_rowconfigure(i, weight=1)
                self.grid_columnconfigure(i, weight=0)
            elif self.categories[i] in ["Tank", "Dps", "Support", "OQ"]:
                self.grid_columnconfigure(i, weight=1)
                img_paths = {"Tank": TANK_IMG,
                            "Dps": DPS_IMG,
                            "Support": SUPPORT_IMG,
                            "OQ": OPEN_QUEUE_IMG}
                
                category_button = ctk.CTkButton(self,
                                        text=self.categories[i],
                                        image=ctk.CTkImage(light_image=Image.open(img_paths[self.categories[i]]),
                                                            dark_image=Image.open(img_paths[self.categories[i]]),
                                                            size=(20, 20)),
                                        font=ctk.CTkFont(size=font_size, weight="bold"),
                                        )
                
                category_button.grid(row=0, column=i, padx=5, pady=5, sticky="w")
            else:
                self.grid_columnconfigure(i, weight=1)
                Button = ctk.CTkButton(self, text=self.categories[i], font=ctk.CTkFont(size=font_size, weight="bold"))
                Button.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        

    def update_table(self):
    # Clear existing player rows (except header)
        for child in self.winfo_children():
            if int(child.grid_info()["row"]) > 0:
                child.destroy()

        # Draw rows from the data list
        for i, player_dict in enumerate(data.data_list):
            row_idx = i + 1
            
            # Delete Button
            del_btn = ctk.CTkButton(
                self, text="", 
                image=ctk.CTkImage(light_image=Image.open(CROSS_IMG_PATH), size=(20, 20)),
                width=30, fg_color="transparent", hover_color="red",
                command=lambda t=player_dict["tag"]: self.handle_delete(t)
            )
            del_btn.grid(row=row_idx, column=0, padx=10, pady=5)

            # Data Labels
            fields = ["tag", "username", "tank", "damage", "support", "open_queue", "owner", "date_added"]
            for col_idx, field in enumerate(fields, start=1):
                val = player_dict.get(field, "")
                lbl = ctk.CTkLabel(self, text=str(val), font=ctk.CTkFont(size=14, weight="bold"))
                lbl.grid(row=row_idx, column=col_idx, padx=5, pady=15, sticky="w")
    
    def handle_delete(self, tag):
        process.delete_player(tag)
        self.update_table()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        db_players = db.get_all_players()
        data.data_list.clear()
        data.tmp_list.clear()
        for player in db_players:
            player_data = {
                "tag": player[1],
                "username": player[2],
                "tank": player[3] + player[4],
                "damage": player[5] + player[6],
                "support": player[7] + player[8],
                "open_queue": player[9] + player[10],
                "owner": player[11],
                "date_added": player[12]
            }
            print(f"Adding player {player[0]}{player[1]} from db to dl")
            data.data_list.append(player_data)
            data.tmp_list.append(player_data)

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
        self.player_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") #setting up categories in player frame

        self.refresh_section = Right_Frame(self)
        self.refresh_section.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        self._set_appearance_mode("dark")
        self.title("Overwatch rank calculator 2.0")
        self.geometry("1920x1080")

        self.player_list.update_table()
        print(data.data_list)

            
        self.deiconify()     # Un-minimize the window if it starts minimized


