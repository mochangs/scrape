import aiohttp
import asyncio
PAGE='https://nhentai.net/'
async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get(PAGE) as resp:
            print(resp.status)
            print(await resp.text())
asyncio.run(fetch())
