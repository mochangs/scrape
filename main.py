import aiofiles
import aiohttp
import telegram
from bs4 import BeautifulSoup
from pygoogletranslation import Translator
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import  traceback
from telegram.request import HTTPXRequest
# https://ailivewallpapers.com/
request = HTTPXRequest(connection_pool_size=200)
translator = Translator()
bot_token = '5872836710:AAGLxglNUtceXHEDdK8K5PMRclgqUujOTow'
channel_id=-1002684579414
bot = Bot(token=bot_token,request=request)
# 异步http请求
async def fetch(session,url):
    async with session.get(url) as response:
        return await response.text()
# 爬取页面
async def getPage(session,page_num):
    url = f'https://ailivewallpapers.com/page/{page_num}/'
    print(url)
    html =await fetch(session,url)
    soup = BeautifulSoup(html, 'html.parser')
    # 许多页面
    task=[]
    pageVideo = soup.find_all(class_='elementor-post__thumbnail__link')
    if pageVideo:
        print(f'第{page_num}页共有{len(pageVideo)}个视频')
        for i in range(len(pageVideo)):
            enterUrl = pageVideo[i].get('href')

            enterUrl1=enterUrl.split('/')[-2]
            print(enterUrl1)

            if enterUrl1 not in file_content:
                mobile=enterUrl.split('-')[-3]

                if mobile!='mobile':

                    # await bot.send_video(chat_id=channel_id,video='https://ailivewallpapers.com/file/darth-vader-leadership-star-wars-live-wallpaper.mp4')
                    task.append(getVideo(session,enterUrl))
                else:
                    async with aiofiles.open('video.txt', 'a', encoding='utf-8') as f:
                        await f.write(enterUrl + '\n')
    await asyncio.gather(*task)
async def getVideo(session,enterUrl):

    html = await fetch(session,enterUrl)
    soup = BeautifulSoup(html, 'html.parser')
    alw_download=soup.find(class_='alw-download')
    source= soup.find('source')

    href = alw_download.get('href')
    categorys=soup.find(class_='elementor-post-info__terms-list').find_all(class_='elementor-post-info__terms-list-item')
    categorysText=[]
    for category in categorys:
        if category.get_text() not in tag_content:
            k.write(category.get_text()+'\n')
            tag_content.add(category.get_text())
        if category.get_text().strip()=='Anime':
            translated_text = '动漫'
            categorysText.append(f'#{translated_text}')
        elif category.get_text().strip()!='Ai':
            try:
                translated_text = translator.translate(category.get_text().strip(), src="en", dest="zh-cn").text
                categorysText.append(f'#{translated_text}')
            except:
                translated_text=category.get_text().strip()

        else:
            categorysText.append('#AI')

    tags=soup.find('div',class_='elementor-element elementor-element-da35136 e-con-full e-flex e-con e-child')
    texts=tags.find_all(class_='elementor-post-info__terms-list-item')
    for text in texts:
        if text.get_text not in tag_content:
            k.write(text.get_text() + '\n')
            tag_content.add(text.get_text())
        try:

            translated_text= translator.translate(text.get_text().strip(), src="en", dest="zh-cn").text
            categorysText.append(f'#{translated_text}')
        except:
            categorysText.append(f'#{text.get_text().strip()}')

    caption=' '.join(categorysText)
    size_div = soup.find( class_='elementor-icon-list-item elementor-repeater-item-4e61e47')

    if size_div:
        size_element = size_div.find(class_='elementor-post-info__terms-list-item')
        size = size_element.get_text().strip() if size_element else None
    else:
        size = None  # 如果找不到，赋值为 None
    other_text = soup.find(class_='elementor-heading-title elementor-size-default')

    if other_text:
        other_text = other_text.get_text().strip()

        other_text=other_text.split(' ')[:-2]
        other_text=' '.join(other_text)
        try:
            other_text = translator.translate(other_text, src="en", dest="zh-cn").text
        except:
            other_text=other_text
        caption = f'[{other_text}]({enterUrl})\n{caption} '
    if source:
        src=source.get('src')


        await sendVideo(src,href,caption,size)
        async with aiofiles.open('video.txt', 'a', encoding='utf-8') as f:
            await f.write(enterUrl + '\n')
async def sendVideo(src, href, caption, size):
    button = InlineKeyboardButton(text=f'下载(文件大小:{size})', url=href)
    keyboard = [[button]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        print(f'本次发送视频连接：{src}')
        await bot.send_video(
            chat_id=channel_id,
            video=src,
            reply_markup=reply_markup,

            parse_mode='Markdown',
            pool_timeout=300,
            connect_timeout=300,
            write_timeout=300
        )
    except telegram.error.TimedOut as err:
        print(f"Timed out error: {err}")


with open('video.txt','a+', encoding='utf-8') as f:
    f.seek(0)
    file_content = f.read()
    if 'asuka-rainy-road-live-wallpaper' in file_content:
        print('存在')
    else:
        print('nonono')
    with open ('videoTag.txt','a+', encoding='utf-8',errors='ignore') as k:
        k.seek(0)
        tag_content = set(k.read().splitlines())
        async def main():
            connector = aiohttp.TCPConnector(limit=150,ssl=False)
            async with aiohttp.ClientSession(connector=connector,timeout=aiohttp.ClientTimeout(total=300)) as session:
                # tasks = [getPage(session, page) for page in range(1, 601)]
                # await asyncio.gather(*tasks)
                for page in range(1000, 0, -1):
                    try:
                        await getPage(session, page)
                    except Exception as e:
                        print(f'出错类型: {type(e).__name__}')
                        print(f'出错信息: {str(e)}')
                        traceback.print_exc()



        asyncio.run(main())
