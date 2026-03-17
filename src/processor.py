import scrap as scraper
import player_list as p_list
import connect_database as db


async def add_player(battletag):    
    player_data = await scraper.scrap_roles(battletag)
    if player_data is not None:
        print("adding player to database...")
        added = db.add_player(player_data)
        if added:
            print("player successfully added to database!")
            p_list.data_list.append(player_data)
            p_list.tmp_list.append(player_data)
            print(p_list.data_list)
            print(p_list.tmp_list)
            print(f"Player {battletag} added successfully.")
        else:
            print("player not added (probably duplicate tag)")
        return True
    print(f"Failed to retrieve data for {battletag}.")
    return False


async def refresh_players():
    battletags = [] #list of btags to refresh
    if p_list.data_list:
        print(p_list.data_list)
        print(len(p_list.data_list))
        for player in p_list.data_list:
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

