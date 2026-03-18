from tkinter import messagebox

import customtkinter as ctk
from PIL import Image
import os
import processor as process
from async_tkinter_loop import async_handler
import player_list as data
import connect_database as db
import re


font_size = 16
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
PAR_DIR = os.path.dirname(FILE_DIR)
IMG_DIR = os.path.join(PAR_DIR, "assets")

CROSS_IMG_PATH = os.path.join(IMG_DIR, "red_cross.png")
TANK_IMG = os.path.join(IMG_DIR, "Tank_icon.png")
DPS_IMG = os.path.join(IMG_DIR, "Damage_icon.png")
SUPPORT_IMG = os.path.join(IMG_DIR, "Support_icon.png")
OPEN_QUEUE_IMG = os.path.join(IMG_DIR, "Open_Queue_icon.png")

BRONZE_IMG = os.path.join(IMG_DIR, "Bronze_icon.png")
SILVER_IMG = os.path.join(IMG_DIR, "Silver_icon.png")    
GOLD_IMG = os.path.join(IMG_DIR, "Gold_icon.png")
PLATINUM_IMG = os.path.join(IMG_DIR, "Platinum_icon.png")
DIAMOND_IMG = os.path.join(IMG_DIR, "Diamond_icon.png")
MASTER_IMG = os.path.join(IMG_DIR, "Master_icon.png")
GRANDMASTER_IMG = os.path.join(IMG_DIR, "Grandmaster_icon.png")


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

        self.add_button = ctk.CTkButton(
            self, 
            text="Add player", 
            fg_color="#116113", 
            hover_color="#1B8F1B",
            font=ctk.CTkFont(size=font_size, weight="bold"),
            command=async_handler(self.on_add_click)
        )
        self.add_button.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="w")

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=font_size - 2, weight="bold"))
        self.status_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="w")

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
            self.add_button.configure(state="disabled", text="Searching...")
            
            success = await process.add_player(battletag)

            if success:
                self.master.player_list.update_table()
                self.status_label.configure(text="Player added", text_color="#116113")
                self.after(3000, lambda: self.status_label.configure(text=""))
            else:
                self.status_label.configure(text="Player not found", text_color="red")
                
            
            self.add_button.configure(state="normal", text="Add player")
            self.battletag_var.set(self.default_text)
            self.add_entry.configure(text_color="#9c9c9c")
            self.focus()


class Right_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.refresh_button = ctk.CTkButton(self,
                                text="Refresh",
                                fg_color="#1a498a",
                                hover_color="#225bab",
                                font=ctk.CTkFont(size=font_size, weight="bold"),
                                command=async_handler(self.on_refresh_click)
                                )
        self.refresh_button.grid(row=0, column=2, padx=20, pady=20, sticky="n")

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=font_size - 2, weight="bold"))
        self.status_label.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="w")

    async def on_refresh_click(self):
        self.refresh_button.configure(state="disabled", text="Refreshing...")
        success = await process.refresh_players()
        if success:
            self.master.player_list.update_table()
            self.status_label.configure(text="Players refreshed", text_color="#20c11a")
            self.after(3000, lambda: self.status_label.configure(text=""))
        else:
            self.status_label.configure(text="Players not refreshed", text_color="red")
        self.refresh_button.configure(state="normal", text="Refresh")

class Scrollable_Frame(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

class Player_list_Frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.categories = ["Delete", "Tag", "Username", "Tank", "Dps", "Support", "OQ", "Owner", "Date Refreshed"]
        self.tank_idx = self.categories.index("Tank")
        self.damage_idx = self.categories.index("Dps")
        self.support_idx = self.categories.index("Support")
        self.open_queue_idx = self.categories.index("OQ")
        self.widget_height = 60
        
        for i in range(len(self.categories)): #Categories row
            if self.categories[i] == "Delete": #delete button column
                self.grid_rowconfigure(i, weight=1)
                self.grid_columnconfigure(i, weight=0)

            elif self.categories[i] == "Tag": #tag column
                self.grid_columnconfigure(i, weight=0)
                tag_label = ctk.CTkLabel(self, text=self.categories[i], font=ctk.CTkFont(size=font_size, weight="bold"))
                tag_label.grid(row=0, column=i, padx=5, pady=5)

            elif self.categories[i] in ["Tank", "Dps", "Support", "OQ"]: #categories columns with icons
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
                
                category_button.grid(row=0, column=i, padx=5, pady=5)
            elif self.categories[i] == "Date Added":
                self.grid_columnconfigure(i, weight=1)
                date_button = ctk.CTkButton(self,
                                            text=self.categories[i], 
                                            font=ctk.CTkFont(size=font_size, weight="bold")
                                            )
                date_button.grid(row=0, column=i, padx=5, pady=5)
            else:
                self.grid_columnconfigure(i, weight=1)
                Button = ctk.CTkButton(self, text=self.categories[i], font=ctk.CTkFont(size=font_size, weight="bold"))
                Button.grid(row=0, column=i, padx=5, pady=5)
        

    def update_table(self): #redraw table, updates table with data_list
        bg_color = "#2b2b2b"
        alt_bgcolor = "#363636"
        # Clear existing player rows (except header)
        self.remove_player_rows()

        # Draw rows from the data list
        for i, player_dict in enumerate(data.data_list):
            row_idx = i + 1
            if row_idx % 2 == 0:
                row_color = alt_bgcolor
            else:
                row_color = bg_color

            # Delete Button (col 0)
            self.create_delete_button(row_idx, player_dict, row_color)

            # Data Labels
            fields = ["tag", "username", "tank", "damage", "support", "open_queue", "owner", "date_added"]
            role_fields = ["tank", "damage", "support", "open_queue"]

            for col_idx, field in enumerate(fields, start=1):
                val = player_dict.get(field, "")
                #if role columns, make btn
                if field in role_fields:
                    self.create_rank_button(row_idx, col_idx, val, row_color)
                elif field == "date_added":
                    self.create_datebutton(row_idx, col_idx, val, row_color, player_dict)
                else:
                    #if not role column, make label
                    self.create_label(row_idx, col_idx, val, row_color)
        return True        

    def handle_delete(self, tag):
        confirm_pop = messagebox.askquestion(title="Delete account?", message="Are you sure you want to delete this account?")
        print(confirm_pop)
        if confirm_pop == "yes":
            process.delete_player(tag)
            self.update_table()

    def remove_player_rows(self):
        for child in self.winfo_children():
            if int(child.grid_info()["row"]) > 0:
                child.destroy()

    def create_delete_button(self, row_idx, player_dict, row_color):
        del_btn = ctk.CTkButton(
                self, text="", 
                image=ctk.CTkImage(light_image=Image.open(CROSS_IMG_PATH), size=(20, 20)),
                width=30, fg_color=row_color, hover_color="red",
                command=lambda t=player_dict["tag"]: self.handle_delete(t),
                height=self.widget_height,
                corner_radius=0
            )
        del_btn.grid(row=row_idx, column=0, padx=0, pady=0, sticky="nsew")

    def create_rank_button(self, row_idx, col_idx, rank_text, row_color):
        game_ranks = {
            "Silver": SILVER_IMG,
            "Gold": GOLD_IMG,
            "Platinum": PLATINUM_IMG,
            "Diamond": DIAMOND_IMG,
            "Master": MASTER_IMG,
            "Grandmaster": GRANDMASTER_IMG,
        }
        display_text = str(rank_text).replace("N/A", "").strip() #Unranked case
        if display_text != "Unranked":
            rank = re.findall("[a-zA-Z]+", display_text)[0]
            division = re.findall("[0-9]+", display_text)
        else:
            rank = "Unranked"

        found_key = None
        for key in game_ranks:
            if key == rank:
                found_key = key
                break

        if found_key:
            with Image.open(game_ranks[found_key]) as img:
                orig_w, orig_h = img.size
            
            target_width = 35
            aspect_ratio = orig_h / orig_w
            calculated_height = int(target_width * aspect_ratio)

            if calculated_height > 30: # 30 is a safe max height for a 50px row
                calculated_height = 30
                target_width = int(calculated_height * (orig_w / orig_h))

            img_path = game_ranks[found_key]

            rank_btn = ctk.CTkButton(self, 
                                text=division,
                                image=ctk.CTkImage(light_image=Image.open(img_path), dark_image=Image.open(img_path), size=(target_width, calculated_height)),
                                font=ctk.CTkFont(size=font_size, weight="bold"), 
                                fg_color=row_color, 
                                corner_radius=0, 
                                height=self.widget_height
                                )
            rank_btn.grid(row=row_idx, column=col_idx, padx=0, pady=0, sticky="nsew")
        else:
            unranked_label = ctk.CTkLabel(self, 
                                text=display_text,
                                font=ctk.CTkFont(size=14, weight="bold"), 
                                fg_color=row_color, 
                                corner_radius=0, 
                                height=self.widget_height
                                )
            unranked_label.grid(row=row_idx, column=col_idx, padx=0, pady=0, sticky="nsew")

    def create_label(self, row_idx, col_idx, text, row_color):
        lbl = ctk.CTkLabel(self, text=str(text), font=ctk.CTkFont(size=14, weight="bold"), fg_color=row_color, corner_radius=0, height=self.widget_height)
        lbl.grid(row=row_idx, column=col_idx, padx=0, pady=0, sticky="nsew")

    def create_datebutton(self, row_idx, col_idx, date_text, row_color, player_dict):
        btn = ctk.CTkButton(self, 
                            text=str(date_text), 
                            font=ctk.CTkFont(size=14, weight="bold"), 
                            fg_color=row_color, 
                            corner_radius=0, 
                            height=self.widget_height,
                            command= async_handler(lambda p=player_dict: self.refresh_single_row(p)))
        btn.grid(row=row_idx, column=col_idx, padx=0, pady=0, sticky="nsew")

    async def refresh_single_row(self, player_dict):
    # Pass the specific player dictionary to the function
        success = await process.refresh_players(player=player_dict)
        if success:
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
        self.grid_columnconfigure(1, weight=20)  # middle scrollable content
        self.grid_columnconfigure(2, weight=1)  # right-side refresh section

        self.add_section = Left_Frame(self)
        self.add_section.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.list_frame = Scrollable_Frame(self)
        self.list_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        self.player_list = Player_list_Frame(self.list_frame)
        self.player_list.grid(row=0, column=0, padx=5, pady=10, sticky="nsew") #setting up categories in player frame

        self.refresh_section = Right_Frame(self)
        self.refresh_section.grid(row=0, column=2, padx=10, pady=20, sticky="nsew")

        self._set_appearance_mode("dark")
        self.title("Overwatch rank calculator 2.0")
        self.geometry("1920x1080")

        self.player_list.update_table()

            
        self.deiconify()     # Un-minimize the window if it starts minimized


