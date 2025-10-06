import aiohttp
import asyncio

PAGE = 'https://nhentai.net/'

# 添加模拟浏览器的请求头，避免被识别为爬虫
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"  # 模拟从搜索引擎跳转
}

async def fetch():
    try:
        async with aiohttp.ClientSession(headers=headers) as session:  # 传入请求头
            async with session.get(PAGE) as resp:
                print(f"状态码：{resp.status}")
                print(await resp.text()[:500])  # 只打印前500字符
    except Exception as e:
        print(f"错误：{e}")

asyncio.run(fetch())
    
