import scrap as scraper
import player_list as p_list


async def add_player(battletag):    
    player_data = await scraper.scrap_roles(battletag)
    if player_data is not None:
        p_list.data_list.append(player_data)
        p_list.tmp_list.append(player_data)
        print(p_list.data_list)
        print(p_list.tmp_list)
        print(f"Player {battletag} added successfully.")
        return True
    print(f"Failed to retrieve data for {battletag}.")
    return False


