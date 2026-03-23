from . import scrap as scraper
from . import player_list as data
from .import connect_database as db

async def add_player(battletag):    
    player_data = await scraper.scrap_roles(battletag)
    if player_data is not None:
        print("adding player to database...")
        added = db.add_player(player_data)
        if added:
            formatted_player = {
                "tag": player_data["tag"],
                "username": player_data["username"],
                "tank": player_data["tank"] + player_data["tank_division"],
                "damage": player_data["damage"] + player_data["damage_division"],
                "support": player_data["support"] + player_data["support_division"],
                "open_queue": player_data["open_queue"] + player_data["open_queue_division"],
                "owner": player_data["owner"],
                "date_refreshed": player_data["date_refreshed"]
            }
            data.data_list.append(formatted_player)
            data.tmp_list.append(formatted_player)
            print(f"Player {battletag} added successfully.")
        else:
            print("player not added (probably duplicate tag)")
        return True
    print(f"Failed to retrieve data for {battletag}.")
    return False


async def refresh_players(player=None):
    to_refresh = [player] if player else data.data_list
    if not to_refresh:
        return False
    for player in to_refresh:
        battletag = f"{player['username']}{player['tag']}"
        player_data = await scraper.scrap_roles(battletag)

        if player_data is not None:
            player_data["owner"] = player["owner"]
            db.update_player(player_data) # updates db
            for i, p in enumerate(data.data_list): # updates data
                if p["tag"] == player_data["tag"]:
                    # Match by tag
                    updated_player = {
                        "tag": player_data["tag"],
                        "username": player_data["username"],
                        "tank": player_data["tank"] + player_data["tank_division"],
                        "damage": player_data["damage"] + player_data["damage_division"],
                        "support": player_data["support"] + player_data["support_division"],
                        "open_queue": player_data["open_queue"] + player_data["open_queue_division"],
                        "owner": p["owner"],
                        "date_refreshed": player_data["date_refreshed"] 
                        }
                    data.tmp_list[i] = data.data_list[i] = updated_player
    return True

def delete_player(tag):
    print(f"Deleting player with tag {tag} from database...")
    db.delete_player(tag)
    data.data_list = [player for player in data.data_list if player["tag"] != tag]
    data.tmp_list = data.data_list.copy()
    
    print(f"Successfully deleted player with tag {tag} from database!")
    return True

Ranks_list = ["Bronze5", "Bronze4", "Bronze3", "Bronze2", "Bronze1", 
                "Silver5", "Silver4", "Silver3", "Silver2", "Silver1", 
                "Gold5", "Gold4", "Gold3", "Gold2", "Gold1", 
                "Platinum5", "Platinum4", "Platinum3", "Platinum2", "Platinum1", 
                "Diamond5", "Diamond4", "Diamond3", "Diamond2", "Diamond1",
                "Master5", "Master4", "Master3", "Master2", "Master1", 
                "Grandmaster5", "Grandmaster4", "Grandmaster3", "Grandmaster2", "Grandmaster1",
                "Champion5", "Champion4", "Champion3", "Champion2", "Champion1"]

def get_rank_index(rank_text):
    if "Unranked" in rank_text:
        return -1
    try:
        return Ranks_list.index(rank_text)
    except ValueError as e:
        print(e)
        return -1
    
def get_span(rank_text):    # Gets the range
    curr_idx = get_rank_index(rank_text)
    if curr_idx <= 19:       # Bronze 5 to Platinum 1
        min_span, max_span = 5, 5
    elif 20 <= curr_idx <= 24: # Diamond
        min_span , max_span = 5, 4
    elif 25 <= curr_idx <= 29: # Master
        min_span, max_span = 4, 3
    elif 30 <= curr_idx <= 34: # Grandmaster
        min_span, max_span = 3, 2
    else:                    # Champion
        min_span, max_span = 2, 2
    return min_span, max_span

def global_range(min_span, max_span, new_idx): # calculates range for the first player added
    minimum = max(0, new_idx - min_span)
    maximum = min(len(Ranks_list) - 1, new_idx + max_span)
    return minimum, maximum


def add_rank(new_player_rank):    
    global global_min_idx, global_max_idx
    new_idx = get_rank_index(new_player_rank)

    if new_idx == -1:
        print("Player cannot be added")
        return False
    
    min_span, max_span = get_span(new_player_rank)
    new_player_min, new_player_max = global_range(min_span, max_span, new_idx)

    if data.selected_accounts:
        if not (global_min_idx <= new_idx <= global_max_idx):
            print("Player cannot be added, not in range")
            return False
        
        global_min_idx = max(global_min_idx, new_player_min)
        global_max_idx = min(global_max_idx, new_player_max)

    else:                       #check if first player
        global_min_idx = new_player_min
        global_max_idx = new_player_max                              #check if between range

    print(f"New player added, new rank range: {Ranks_list[global_min_idx]} to {Ranks_list[global_max_idx]}")
    return True

def can_add_role(role):
    if role == "open_queue":
        return True
    if role == "tank":
        return data.role_list.count("tank") < 1
    else:
        return data.role_list.count(role) < 2
    
def can_add_owner(owner):
    if str(owner).strip().upper() == "N/A":
        return True
    
    clean_owner = str(owner).lower()
    for existing_owner in data.owner_list:
        clean_existing_owner = str(existing_owner).lower()
        if clean_existing_owner == "n/a":
            continue
        if clean_existing_owner in clean_owner or clean_owner in clean_existing_owner:
            return False
    return True

def recalculate_range():
    global global_min_idx, global_max_idx
    global_min_idx = 0
    global_max_idx = len(Ranks_list) - 1
    
    for acc in data.selected_accounts:
        rank = acc["rank"]
        idx = get_rank_index(rank)
        min_span, max_span = get_span(rank)
        new_player_min, new_player_max = global_range(min_span, max_span, idx)
        global_min_idx = max(global_min_idx, new_player_min)
        global_max_idx = min(global_max_idx, new_player_max)

def handle_add_squad(username, owner, role, rank):
    global global_min_idx, global_max_idx
    existing_acc = next((acc for acc in data.selected_accounts if acc["username"] == username and acc["role"] == role), None)

    # Removing account
    if existing_acc:
        data.selected_accounts.remove(existing_acc)
        if owner in data.owner_list: data.owner_list.remove(owner)
        if role in data.role_list: data.role_list.remove(role)
        
        if not data.selected_accounts:
            global_min_idx = 0
            global_max_idx = len(Ranks_list) - 1
            print("Squad empty, resetting rank range")
        else:
            recalculate_range()
        print(f"Removed {username} {role} {rank} from the squad")
        print(data.owner_list)
        print(data.role_list)
        return True
    
    # Check if can add account
    if not can_add_owner(owner):
        print(f"Owner {owner} already exists in the squad")
        return False
    
    if not can_add_role(role):
        print(f"Too many {role} in the squad")
        return False
    
    # Adding account
    if add_rank(rank):
        data.owner_list.append(owner)
        data.role_list.append(role)

        data.selected_accounts.append({
            "username": username, 
            "owner": owner, 
            "role": role, 
            "rank": rank
        })
        print(f"Successfully added {username} {role} {rank} to the squad")
        print(data.role_list)
        print(data.owner_list)
        return True
    return False

def sort_by_role(role):
    def get_sort_value(player):
        val = player.get(role)

        if role in ["tank", "damage", "support", "open_queue"]:
            return get_rank_index(str(val))
        
        text_val = str(val or "").strip().lower()
        if text_val == "n/a" or text_val == "":
            return "zzzzzzzzzzz"
        return text_val
    
    is_rank_col = role in ["tank", "damage", "support", "open_queue"]
    data.tmp_list.sort(key=get_sort_value, reverse=is_rank_col)


def test():
    while len(data.selected_accounts) < 5:
        rank = input("Rank?\n")
        add_squad(rank)
        print(data.selected_accounts)

