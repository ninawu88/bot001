# pip3 install flask, requests
# pip3 install flask
# pip3 install requests
# pip3 install line-bot-sdk
# pip3 install SQLAlchemy==1.4.20
# pip3 install SQLAlchemy-Utils

# import library 
import types
from flask import Flask, request, abort

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *
from urllib.parse import quote

# import custom module
import config
import utils
from database import db_session
from models.users import Users
from models.products import Products
from models.cart import Cart


app = Flask(__name__)

# add new method to the scoped session instance 
db_session.get_or_create_user = types.MethodType(utils.get_or_create_user, db_session)
db_session.init_products = types.MethodType(utils.init_products, db_session)
""" print(dir(db_session))
print(dir(db_session())) """

# an “on request end” event
# automatically remove database sessions at the end of the request 
# or when the application shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


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
        config.handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@config.handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        #print(f"this is event: {event}")
        user_id = event.source.user_id
        db_session.get_or_create_user(user_id=user_id)
        cart = Cart(user_id=user_id)
        
        msg_text = str(event.message.text).lower()
        msg_reply = None
        if msg_text in ['i am ready to order', 'add', '加入購物車']:
            msg_reply = Products.list_all() # call class method
        elif msg_text in ['my cart', 'cart', '我的購物車']:
            msg_reply = TextSendMessage(text='cart')
        elif "i'd like to order" in msg_text:
            product_name = msg_text.split('\n')[0]
            reserve_time = msg_text.split('\n')[1]
            num_item = msg_text.split('\n')[-1]
            #print(product_name, num_item)
            product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
            if product and num_item and num_item != '0' and num_item.isdigit():
                cart.add(product=product_name, num=num_item, time=reserve_time)
                items = f"Reserving:\n"
                for i in [f"    {value['amount']} {key} at {value['datetime']}\n" for key, value in cart.bucket().items()]:
                    items = items+i

                add_revise_confirm_template = ConfirmTemplate(
                    text=f'{items}Anything else?',
                    actions=[
                        MessageAction(label='Add/Revise', text='add'),
                        MessageAction(label="That's it", text="that's it")
                    ])
                msg_reply = TemplateSendMessage(alt_text='anything else?', template=add_revise_confirm_template)
            else:
                reselect_confirm_template = ConfirmTemplate(
                    text=f"Sorry, we don't have {product_name} or you forgot to enter a right amount.",
                    actions=[
                        MessageAction(label='Add/Revise', text='add'),
                        MessageAction(label="That's it", text="that's it")
                    ])
                msg_reply = TemplateSendMessage(alt_text='anything else?', template=reselect_confirm_template)
        if msg_reply is None: 
            msg_reply = [
                TextSendMessage(text='''若要將商品加入購物車，請傳送訊息: 加入購物車\n若要顯示您的購物車，請傳送訊息: 我的購物車'''),
                TextSendMessage(text='''If you would like to add the product to the cart, please type: "add" or "i am ready to order"'''),
                TextSendMessage(text='''If you would like to see the products in your cart, please type: "my cart" or "cart"''')
            ]
        config.line_bot_api.reply_message(
            event.reply_token,
            msg_reply)

    except LineBotApiError as e:
        print(f'err: {e}')


@config.handler.add(PostbackEvent)
def handle_postback(event):
    #print(event)
    datatime_confirm_template = ConfirmTemplate(
                    text=f"Reserving:\n    {event.postback.data}\n    {event.postback.params['datetime']}",
                    actions=[
                        URIAction(
                            label= 'Enter Amount', 
                            uri=f"https://line.me/R/oaMessage/{config.Bot_ID}/?" + quote(f"{event.postback.data}\n{event.postback.params['datetime']}\nI'd like to order:\n(Pls type in number)\n")
                        ),
                        MessageAction(label="Select Again", text="add")
                    ])
    msg_reply = TemplateSendMessage(alt_text='Reserving the time', template=datatime_confirm_template)
    config.line_bot_api.reply_message(
            event.reply_token,
            msg_reply)


@config.handler.add(FollowEvent)
def handle_follow(event):
    db_session.get_or_create_user(event.source.user_id)

    config.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='welcome to linebot!'))


@config.handler.add(UnfollowEvent)
def handle_unfollow():
    pass
    #print('Unfollow event')


if __name__ == "__main__":
    db_session.init_products()
    app.run() # one web request is a thread 