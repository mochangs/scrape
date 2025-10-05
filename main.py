import asyncio
import logging
import os.path
import time
import re
from http.client import responses
from os import makedirs
from os.path import  exists
from pygoogletranslation import Translator
import aiohttp

from telethon import TelegramClient
import requests
import undetected_chromedriver as uc
from pyquery import PyQuery as pq
from urllib.parse import urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from html_telegraph_poster import TelegraphPoster
import io
import zipfile

from telegram import Bot
token='7168200642:AAGB0oVdKkAZ-Qztqech5PxEEdojstw0P30'
bot=Bot(token=token)
translator = Translator()
# f翻译
# driver_path=r'C:\Users\30936\appdata\roaming\undetected_chromedriver\undetected_chromedriver.exe'
with open ('sentManga','a+',encoding='utf-8') as f:
    f.seek(0)
    sent_manga=set(f.read().splitlines())
logging.basicConfig(level=logging.INFO,format='%(asctime)s -- %(levelname)s:--%(message)s')
LOGIN_URL='https://nhentai.net/login/?next=/'
api_id = 28746712
api_hash = 'fadb4020f4ec9c4c420412f5e220f301'
channel_id=-1002989732424
phone_number = '13604744078'
NAME='3093665409@qq.com'
PASSWORD='lierqi20030428..'
INDEX_URL='https://nhentai.net/language/chinese/?page={page}'
Total_Page=5216
options = uc.ChromeOptions()
options.add_argument('--headless=new')
browser = uc.Chrome(options=options)
browser.minimize_window()
wait =WebDriverWait(browser,300)
def scrape_page(url,condition,locator):
    logging.info('正在爬取，%s',url)
    try:


        browser.get(url)
        # 添加页面状态检查
        logging.info('页面标题: %s', browser.title)
        logging.info('当前URL: %s', browser.current_url)

        # 检查是否有重定向或错误页面
        if 'error' in browser.current_url.lower() or 'block' in browser.current_url.lower():
            logging.error('可能被重定向到错误页面: %s', browser.current_url)
            return False

        wait.until(condition(locator))

    except TimeoutError as e:
        logging.error('错误发生，爬取%s',url,exc_info=True)
def scrape_index(page):
    url=INDEX_URL.format(page=page)
    scrape_page(url,condition=EC.visibility_of_all_elements_located,locator=(By.CLASS_NAME,'cover'))
def parse_index():
    elements=browser.find_elements(By.CLASS_NAME,'cover')
    for element in elements:
        href =element.get_attribute('href')
        yield href
def scrape_detail(url):
    scrape_page(url,condition=EC.visibility_of_all_elements_located,locator=(By.CLASS_NAME,'nobold'))
async def parse_detail(detail_url,client:TelegramClient):

    count=browser.find_elements(By.CLASS_NAME,'nobold')[1].text
    math=re.search(r'\d+',count)
    number=int(math.group())
    if number>666:
        logging.info(
            '该漫画 收藏大于666，开始下载: %s, 收藏数: %d',
            detail_url, number
        )
        manga_id=browser.current_url.split('/')[-2]
        imgurls=list(scrape_img())
        tags = getTags()
        thead = tags.split('\n')[1]
        artical_url=generate_telegraph_url(thead, imgurls)

        # client发送图片没有评论，故适用bot发送图片，适用client发送评论
        # 构造标签

        try :
            cover_sent=await bot.send_photo(chat_id=channel_id,photo=imgurls[0],caption=tags,parse_mode='Markdown',pool_timeout=30,
                                        connect_timeout=30,write_timeout=30)
        except:
            cover_sent=await  bot.send_message(chat_id=channel_id,text='封面不可见')
        await client.send_message(channel_id,message=artical_url,comment_to=cover_sent.message_id
                                  ,)
        with open('sentManga', 'a', encoding='utf-8') as f1:
            f1.write(manga_id + '\n')

        # try:
        #     file= await download(imgurls)
        #
        #     await client.send_file(channel_id,file=file,comment_to=cover_sent.message_id,force_document=True)
        # except:
        #     await  client.send_message(channel_id,message='下载文件失败')

origin_href='https://i.nhentai.net/galleries/{gallery_id}/{page_number}.{extension}'
def scrape_img():
    try:
        html=browser.page_source
        doc=pq(html)
        thumb=doc('.thumb-container .lazyload')
        for item in thumb.items():
            src=item.attr('data-src')
            # // t1.nhentai.net / galleries /3512439/2t.webp.webp
            gallery_id = re.search(r'/galleries/(\d+)/', src).group(1)
            page_number=re.search(r'/(\d+)t.',src).group(1)

            extension = src.split('.')[-1]

            src=origin_href.format(gallery_id=gallery_id,page_number=page_number,extension=extension)

            yield src
    except Exception as e:
        logging.info('下载错误，%s',str(e))
RESULT_DIR = 'Manga'
exists(RESULT_DIR) or makedirs(RESULT_DIR)
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }


async def fetch_image(session, url, max_retries=3, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, headers=headers, timeout=20) as response:
                if response.status == 200:
                    content = await response.read()
                    filename = url.split('/')[-1]
                    file_size = len(content)
                    logging.info(f'下载成功: {url}, 文件大小: {file_size} 字节')

                    if file_size < 100:
                        logging.warning(f'文件大小异常小: {file_size} 字节，可能是错误页面')
                        try:
                            content_text = content.decode('utf-8', errors='ignore')
                            if "error" in content_text.lower() or "not found" in content_text.lower():
                                logging.error(f'下载的内容包含错误信息: {content_text[:200]}...')
                                return None
                        except:
                            pass

                    return filename, content
                else:
                    error_content = await response.text()
                    logging.error(f'下载失败: {url}, 状态码: {response.status}, 响应内容: {error_content[:200]}...')

        except asyncio.TimeoutError:
            logging.error(f'下载超时: {url}（第 {attempt} 次）')
        except aiohttp.ClientError as e:
            logging.error(f'客户端错误: {url}（第 {attempt} 次），类型: {type(e).__name__}，信息: {str(e)}')
        except Exception as e:
            logging.error(f'未知错误: {url}（第 {attempt} 次），类型: {type(e).__name__}，信息: {str(e)}')
            import traceback
            logging.error(f'完整堆栈跟踪: {traceback.format_exc()}')

        if attempt < max_retries:
            logging.info(f'等待 {delay} 秒后重试（第 {attempt + 1} 次）: {url}')
            await asyncio.sleep(delay)

    logging.error(f'下载失败（已重试 {max_retries} 次）: {url}')
    return None


async def download(urls):


    zip_buffer=io.BytesIO()
    async with aiohttp.ClientSession(proxy='http://127.0.0.1:10808',trust_env=True) as session:
        task=[fetch_image(session,url) for url in urls]
        results= await asyncio.gather(*task)
        with zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED) as zip_file:
            for result in results:
                if result:
                    filename,content=result
                    zip_file.writestr(filename,content)
        zip_buffer.seek(0)
        zip_buffer.name = browser.current_url.split('/')[-2] + '.zip'
        return zip_buffer
    # with zipfile.ZipFile(zip_buffer,'w',zipfile.ZIP_DEFLATED) as zip_file:
    #     for url in urls:
    #         try:
    #             response=requests.get(url,timeout=20)
    #             if response.status_code==200:
    #                 filename=url.split('/')[-1]
    #                 zip_file.writestr(filename,response.content)
    #             else:
    #                 logging.info('下载失败：%s',url)
    #         except Exception as e:
    #             logging.info('下载异常：%s',str(e))

def generate_telegraph_url(thead,image_url):
    # 创建Telegraph文章的函数
    def create_telegraph_article(image_urls, title, author, short_name='Author'):
        try:
            # 初始化TelegraphPoster
            t_poster = TelegraphPoster(use_api=True)
            # 创建API令牌，现在提供了必需的short_name参数
            t_poster.create_api_token(author_name=author, short_name=short_name)

            image_html_tags = ''.join([f'<img src="{url}"/>' for url in image_urls])
            html_content = image_html_tags
            response = t_poster.post(
                title=title,
                author=author,
                text=html_content,
                author_url='https://t.me/scrapefromnhentai'
            )
            # 从响应中获取文章URL
            article_url = response.get('url')
            if article_url:

                return article_url
            else:
                print("Telegraph文章创建失败，未获取到URL。响应信息:", response)
                return None
        except Exception as e:
            print(f"创建Telegraph文章过程中发生错误: {str(e)}")
            return None
    my_image_urls = image_url


    return create_telegraph_article(
        image_urls=my_image_urls,
        title=thead,
        author='Nhentai',  # 设置作者名
        short_name='li'  # 设置作者的简短名称标识
    )
# def login():
#     browser.get(LOGIN_URL)
#     logging.info('人机验证 ing')
#     input('完成验证后，按回车继续')
#     time.sleep(1)
#     browser.find_element(By.NAME,'username_or_email').send_keys(NAME)
#     time.sleep(1)
#     browser.find_element(By.NAME,'password').send_keys(PASSWORD)
#     time.sleep(1)
#     browser.find_element(By.TAG_NAME,'button').click()
async def main():
    try:
        proxy = ('http', '127.0.0.1', 10808)
        client = TelegramClient('session_name', api_id, api_hash, proxy=proxy)
        # login()
        async with client:
            await client.start(phone=phone_number)
            for page in range(1,Total_Page+1):
                scrape_index(page)
                detail_urls=parse_index()

                for detail_url in list(detail_urls):
                    if detail_url.split('/')[-2] in sent_manga:
                        logging.info('该漫画已存在，跳过 %s',detail_url)
                        continue
                    scrape_detail(detail_url)
                    await asyncio.sleep(5)
                    await parse_detail(detail_url,client)
                await asyncio.sleep(5)

    finally:
        browser.close()

def getTags():
    tag_blocks = browser.find_elements(By.CSS_SELECTOR, '.tag-container')
    results = []
    titles = browser.find_elements(By.CLASS_NAME, 'title')

    for title in titles:
        spans = title.find_elements(By.TAG_NAME, 'span')
        tag_texts = [span.text.strip() for span in spans if span.text.strip()]
        if tag_texts:
            results.append(' '.join(tag_texts))

    gallery_id=browser.current_url.split('/')[-2]
    results.append(f'#{gallery_id}')
    for block in tag_blocks:
        try:
            heads = block.text.split('\n')[0].strip()  # 获取标题
            tags = block.find_elements(By.CSS_SELECTOR, '.tag .name')

            tag_texts = []
            for tag in tags:
                raw = tag.text.strip()
                if not raw:
                    continue

                try:
                    if heads!='Languages:':
                        translated = translator.translate(raw, src='en', dest='zh-cn').text
                        tag_texts.append(f"#{translated}")
                    else:
                        tag_texts.append(tag)
                except Exception as e:
                    logging.warning(f"翻译失败: {raw} → 使用原文")
                    tag_texts.append(f"#{raw}")

            if tag_texts:
                line = f'{heads} {" ".join(tag_texts)}'
                results.append(line)
        except Exception as e:
            logging.warning(f'标签解析失败: {str(e)}')

    return '\n'.join(results)


error_count = 0



if __name__=='__main__':
            asyncio.run(main())
error_count = 0
MAX_ERRORS = 10  # 可选：达到最大错误次数后退出

while True:
    try:
        asyncio.run(main())
        error_count = 0  # 如果运行成功，重置错误计数
    except Exception as e:
        error_count += 1
        logging.error(f'运行出错，第 {error_count} 次: {str(e)}')

        # 可选：写入错误日志文件
        with open('error_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(f'第 {error_count} 次错误: {str(e)}\n')

        # 可选：达到最大错误次数后退出
        if error_count >= MAX_ERRORS:
            logging.critical('错误次数过多，终止程序')
            break

        # 等待一段时间再重试
        time.sleep(5)
