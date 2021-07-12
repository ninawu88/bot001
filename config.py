# pip3 install python-dotenv

import os
from dotenv import load_dotenv
from linebot import (
    LineBotApi, WebhookHandler
)


load_dotenv()
Bot_ID = os.environ.get('Bot_ID')
Channel_access_token = os.environ.get('Channel_access_token')
Channel_secret =  os.environ.get('Channel_secret')

line_bot_api = LineBotApi(Channel_access_token)
handler = WebhookHandler(Channel_secret)
#print(os.environ.get('Channel_access_token'))

db_path = 'sqlite:///' + f'{os.path.dirname(__file__)}/linebot.db'