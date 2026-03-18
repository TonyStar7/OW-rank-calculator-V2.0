import scrap as scraper
import player_list as data
import connect_database as db

async def add_player(battletag):    
    player_data = await scraper.scrap_roles(battletag)
    if player_data is not None:
        print("adding player to database...")
        added = db.add_player(player_data)
        if added:
            print("player successfully added to database!")
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


async def refresh_players():
    battletags = [] #list of btags to refresh
    if data.data_list:
        print(data.data_list)
        print(len(data.data_list))
        for player in data.data_list:
            print(f"Putting {player['username'] + str(player['tag'])} in battletags list for refresh...")
            battletags.append((player["username"] + str(player["tag"])))
            print(f"Successfully put {player['username'] + str(player['tag'])} in battletags list for refresh!")

        for battletag in battletags:
            print(f"Refreshing {battletag}...")
            player_data = await scraper.scrap_roles(battletag)
            print("finished refreshing, now updating database...")

            if player_data is not None:
                db.update_player(player_data)
                print(f"Successfully updated {battletag} in database!")
    return True

def delete_player(tag):
    print(f"Deleting player with tag {tag} from database...")
    db.delete_player(tag)
    data.data_list = [player for player in data.data_list if player["tag"] != tag]
    data.tmp_list = data.data_list.copy()
    
    print(f"Successfully deleted player with tag {tag} from database!")
    return True
