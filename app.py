from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('Mey9WSMEsYoM9tPsG7cwWoF3VJQBgo7c0doI70rNl/XSMqqeVcU/KZxvtdE2JRyqSYOhXTQTSDl2ekWrEb2FbnRPAHEkwQLPdLgTmBZLKwUoIG6yw+ZS+7QUCq2aply5HI1Youl9VCt1SRqeOen44gdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ad324cad12249807470d71979e3f12b8')


@app.route("/callback", methods=['POST'])
def callback():
    #print(f"this is request.headers: {request.headers}")

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    #print(f"this is request.body: {body}")
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #print(f"this is event: {event}")
    msg_text = str(event.message.text).lower()
    msg_reply = None

    if msg_text in ['i am ready to order', 'add', '加入購物車']:
        msg_reply = TextSendMessage(text='list products')
    
    elif msg_text in ['my cart', 'cart', '我的購物車']:
        msg_reply = TextSendMessage(text='cart')

    if msg_reply is None: 
        msg_reply = [
            TextSendMessage(text='''若要將商品加入購物車，請傳送訊息: 加入購物車\n若要顯示您的購物車，請傳送訊息: 我的購物車'''),
            TextSendMessage(text='''If you would like to add the product to the cart, please type: "add" or "i am ready to order"'''),
            TextSendMessage(text='''If you would like to see the products in your cart, please type: "my cart" or "cart"''')
        ]

    line_bot_api.reply_message(
        event.reply_token,
        msg_reply)


if __name__ == "__main__":
    app.run()
