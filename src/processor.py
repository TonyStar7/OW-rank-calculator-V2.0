import scrap as scraper
import player_list as data
import connect_database as db

async def add_player(battletag):    
    player_data = await scraper.scrap_roles(battletag)
    if player_data is not None:
        print("adding player to database...")
        added = db.add_player(player_data)
        if added:
            data.data_list.append(player_data)
            data.tmp_list.append(player_data)
            print(data.data_list)
            print(data.tmp_list)
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
