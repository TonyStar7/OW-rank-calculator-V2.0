import aiohttp

BASE_URL = "https://overwatch.blizzard.com/en-us/career/"

def check_request_status(response):
    return response.status == 200

async def get_player_data(battletag):
    player_page = BASE_URL + battletag.replace("#", "-")
    async with aiohttp.ClientSession() as session:
        async with session.get(player_page) as response:
            if not check_request_status(response):
                print(f"error api for {battletag} : {response.status}")
                return None
            text = await response.text()
            print(f"success api for {battletag}")
            return text
    
