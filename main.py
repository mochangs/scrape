import asyncio
from telegram import Bot
token='7168200642:AAGB0oVdKkAZ-Qztqech5PxEEdojstw0P30'
channel_id=-1002989732424
bot=Bot(token=token)
async def send():
    await bot.send_message(chat_id=channel_id,text='你好',read_timeout=30,write_timeout=30,pool_timeout=30)
asyncio.run(send())
