import scrap as scraper
import player_list as data
import connect_database as db
import re

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
                        "owner": player_data["owner"],
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

def add_squad(new_player_rank):
    global global_min_idx, global_max_idx

    new_idx = get_rank_index(new_player_rank)
    if new_idx == -1:
        print("Player cannot be added")
        return False
    
    min_span, max_span = get_span(new_player_rank)
    new_player_min, new_player_max = global_range(min_span, max_span, new_idx)

    if data.selected_accounts and not global_min_idx <= new_idx <= global_max_idx:
        print("Player cannot be added, not in range")
        return False

    if not data.selected_accounts:       #check if first player
        global_min_idx = new_player_min
        global_max_idx = new_player_max
    else:                                #check if between range
        global_min_idx = max(global_min_idx, new_player_min)
        global_max_idx = min(global_max_idx, new_player_max)

    data.selected_accounts.append(new_player_rank)
    print(f"New player added, new rank range: {Ranks_list[global_min_idx]} to {Ranks_list[global_max_idx]}")
    return True


def sort_by_role(role):
    data.tmp_list.sort(key=lambda player: get_rank_index(str(player[role])), reverse=True)



def test():
    while len(data.selected_accounts) < 5:
        rank = input("Rank?\n")
        add_squad(rank)
        print(data.selected_accounts)

