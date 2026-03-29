from .processor import refresh_players, load_players
import asyncio

async def backend_service():
    print("Starting backend service...")
    load_players()
    print("Loaded players to list")
    while True:
        await refresh_players()
        print("Backend service refreshed.")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(backend_service())