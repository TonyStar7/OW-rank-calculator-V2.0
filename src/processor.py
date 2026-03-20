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
                    data.data_list[i] = {
                        "tag": player_data["tag"],
                        "username": player_data["username"],
                        "tank": player_data["tank"] + player_data["tank_division"],
                        "damage": player_data["damage"] + player_data["damage_division"],
                        "support": player_data["support"] + player_data["support_division"],
                        "open_queue": player_data["open_queue"] + player_data["open_queue_division"],
                        "owner": player_data["owner"],
                        "date_refreshed": player_data["date_refreshed"] 
                        }
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
    
def check_rank_category(rank_text):
    curr_idx = get_rank_index(rank_text)
    if curr_idx == -1:
        return "Unranked"
    if curr_idx < 22:
        return "Max Diamond 4"
    if curr_idx >= 22 and curr_idx <= 24:
        return "min D3 max D1"
    return "min Master"

def get_span(rank_text):
    curr_idx = get_rank_index(rank_text)
    if curr_idx <= 24: # Bronze 5 to Diamond 1
        return 5
    if 25 <= curr_idx <= 29: # Master
        return 4
    if 30 <= curr_idx <= 34: # Grandmaster
        return 3
    return 2 # Champion

def can_squad_play(rank1, rank2):
    idx1 = get_rank_index(rank1)
    idx2 = get_rank_index(rank2)
    
    if idx1 == -1 or idx2 == -1:
        return "Unranked"

    distance = abs(idx1 - idx2)
    
    # The rule: The highest player dictates the limit
    highest_rank = rank1 if idx1 > idx2 else rank2
    allowed_span = get_span(highest_rank)
    
    return distance <= allowed_span

print(can_squad_play("Diamond5", "Master5"))