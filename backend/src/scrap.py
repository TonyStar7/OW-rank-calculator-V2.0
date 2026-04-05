import re
from bs4 import BeautifulSoup
from .api import *
from datetime import datetime

BASE_URL = "https://overwatch.blizzard.com/en-us/career/"
roles_block_class = "mouseKeyboard-view Profile-playerSummary--rankWrapper is-active"
indiv_role_class = "Profile-playerSummary--roleWrapper"
rank_class = "Profile-playerSummary--rank"
role_icon_class = "Profile-playerSummary--role"



async def scrap_player_page(battletag): # returns the page of the player
    formatted_battletag = battletag.replace("#", "-")
    page_text = await get_player_data(formatted_battletag)
    if not page_text:
        print("error getting player data")
        return None
    page = BeautifulSoup(page_text, "html.parser")
    return page

def scrap_role_block(page): # returns the block with all 3 roles
    if page is None:
        return None
    return page.find("div", class_=roles_block_class)

def list_role_block(page): # returns the 3 roles as list
    roles_block = scrap_role_block(page)
    if roles_block is None:
        return []
    return roles_block.find_all("div", class_=indiv_role_class) or []

def scrap_role_icon(role): # returns the role icon for curr role
    if role is None:
        return None
    role_icon_div = role.find("div", class_=role_icon_class)
    if role_icon_div is None:
        return None
    return role_icon_div.find("img")

def scrap_img_rank(role): # returns the rank img for curr role
    if role is None:
        return []
    return role.find_all("img", class_=rank_class) or []

def reg_search_role(role_icon_img): # searches role string
    if role_icon_img is None:
        return "Unranked"
    m = re.search(r"role/(\w+)", str(role_icon_img))
    if not m:
        return "Unranked"
    role = m.group(1)
    if role == "offense":
        return "dps"
    return role

def reg_search_rank(imgs_rank): # searches rank string
    if len(imgs_rank) < 2:
        return "Unranked", "N/A"
    rank_match = re.search(r"Rank_(\w+)Tier", str(imgs_rank[0]))
    div_match = re.search(r"TierDivision_(\w+)", str(imgs_rank[1]))
    rank = rank_match.group(1) if rank_match else "Unranked"
    rank_div = div_match.group(1) if div_match else "N/A"
    return rank, rank_div

def add_time():
    now = datetime.now()
    date_refreshed = now.strftime("%d/%m/%Y %H:%M")
    print(date_refreshed)
    return date_refreshed

def split_battletag(battletag):
    try:
        tag = '#' + battletag.split('#')[1]
        username = battletag.split('#')[0]
        return tag, username
    except IndexError:
        return None

async def scrap_roles(battletag):
    date_refreshed = add_time()
    tag, username = split_battletag(battletag)
    page = await scrap_player_page(battletag)

    tank = damage = support = open_queue = "Unranked"
    tank_division = damage_division = support_division = open_queue_division = "N/A"

    indiv_roles = list_role_block(page)
    if not indiv_roles:
        print("Warning: no roles found on page, saving all defaults")
        player_data = {
        "tag": tag,
        "username": username,
        "tank": "Unranked",
        "tank_division": 'N/A',
        "damage": "Unranked",
        "damage_division": 'N/A',
        "support": "Unranked",
        "support_division": 'N/A',
        "open_queue": "Unranked",
        "open_queue_division": 'N/A',
        "tank_diff": 'same',
        "damage_diff": 'same',
        "support_diff": 'same',
        "open_queue_diff": 'same',
        "owner": "N/A",
        "date_refreshed": date_refreshed
        }
        return player_data
    else:
        for curr_role in indiv_roles:
            role_icon_img = scrap_role_icon(curr_role)
            imgs_rank = scrap_img_rank(curr_role)

            role = reg_search_role(role_icon_img)
            rank, rank_div = reg_search_rank(imgs_rank)

            if role == "tank":
                tank, tank_division = rank, rank_div
            elif role == "dps":
                damage, damage_division = rank, rank_div
            elif role == "support":
                support, support_division = rank, rank_div
            elif role == "open":
                open_queue, open_queue_division = rank, rank_div

    player_data = {
        "tag": tag,
        "username": username,
        "tank": tank,
        "tank_division": tank_division,
        "damage": damage,
        "damage_division": damage_division,
        "support": support,
        "support_division": support_division,
        "open_queue": open_queue,
        "open_queue_division": open_queue_division,
        "tank_diff": 'same',
        "damage_diff": 'same',
        "support_diff": 'same',
        "open_queue_diff": 'same',
        "owner": "N/A",
        "date_refreshed": date_refreshed,
    }

    return player_data
