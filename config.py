# pip3 install python-dotenv

import os
import logging
from dotenv import load_dotenv
from linebot import (
    LineBotApi, WebhookHandler
)
from datetime import datetime

load_dotenv()

# linebot msg api 
Bot_ID = os.environ.get('Bot_ID')
Channel_access_token = os.environ.get('Channel_access_token')
Channel_secret =  os.environ.get('Channel_secret')

line_bot_api = LineBotApi(Channel_access_token)
handler = WebhookHandler(Channel_secret)
#print(os.environ.get('Channel_access_token'))

# db
db_path = 'sqlite:///' + f'{os.path.dirname(__file__)}/linebot.db'

# linepay
LINE_PAY_ID = os.environ.get('LINE_PAY_ID')
LINE_PAY_SECRET = os.environ.get('LINE_PAY_SECRET')
#PAY_API_URL = 'https://sandbox-api-pay.line.me/v2/payments/request'
#CONFIRM_API_URL = 'https://sandbox-api-pay.line.me/v2/payments/{}/confirm'
#STORE_IMAGE_URL = 'https://i.imgur.com/HvJQ4qL.png'

# liff
LIFF_LINEPAY = 'https://liff.line.me/1656118882-gGKlpBvr'
LIFF_LINEPAY_REQ = 'https://liff.line.me/1656118882-RWMrlNJO'

# logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
	'[%(levelname)s %(asctime)s %(module)s:%(lineno)d] %(message)s',
	datefmt='%Y%m%d %H:%M:%S')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)


fh = logging.FileHandler(filename=f'linebot_{datetime.today().strftime("%Y-%m-%d")}.log', mode='w')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

logger.addHandler(ch)
logger.addHandler(fh)

# api 
yes_api_base = "http://13.114.106.45:8088/api/"