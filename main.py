import aiohttp
import asyncio
from bs4 import BeautifulSoup



INDEX_URL='https://nhentai.net/language/chinese/?page={page}'

# 添加模拟浏览器的请求头，避免被识别为爬虫
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/"  # 模拟从搜索引擎跳转
}
Total_Page=5216
# 爬取每一页含有的网页图片，返回每个本子的链接
async def fetch(page,semaphore):
    try:
        async with aiohttp.ClientSession(headers=headers) as session:  # 传入请求头
            async with session.get(page) as resp:
                re=BeautifulSoup(await resp.text(), 'html.parser')
                covers=re.find_all(class_='cover')
                return [cover.get('href') for cover in covers]
    except Exception as e:
        print(f"错误：{e}")
async def main():
    task=[]
    semaphore = asyncio.Semaphore(10)
    for i in range(1,Total_Page+1):
        url=INDEX_URL.format(page=i)
        task.append(asyncio.create_task(fetch(url, semaphore)))
    results=await asyncio.gather(*task, return_exceptions=True)

if __name__ == '__main__':
    asyncio.run(main())
