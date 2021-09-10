# pip3 install flask, requests
# pip3 install flask
# pip3 install requests
# pip3 install line-bot-sdk
# pip3 install SQLAlchemy==1.4.20
# pip3 install SQLAlchemy-Utils
# pip3 install alembic
# pip3 install flask-restful

# import library 
import types
from flask import Flask, request, abort, render_template, redirect
from flask_restful import Api, Resource, reqparse
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *
from urllib.parse import quote, parse_qsl
import uuid
from datetime import datetime
def strptime(time):
    if 't' in time:
        return datetime.strptime(time[2:], '%y-%m-%dt%H:%M')
    else:
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    

# import custom module
import config
import utils
from database import db_session
from models.users import Users
from models.products import Products
from models.cart import Cart
from models.order import Orders
from models.item import Items
from models.linepay import LinePay
import resources_cls

app = Flask(__name__)
yes_api = Api(app)
yes_api.add_resource(resources_cls.test, '/test')

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


@app.route("/", methods=['GET', 'POST'])
def index():
    # render the file under /templates
    # request.args for GET 
    # request.form for POST
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        return render_template("greet.html", name=request.form.get('name', 'world'))


# https://rvproxy.fun2go.energy/confirm
@app.route("/confirm")
def confirm():
    config.logger.debug(request.args)
    tx_id = int(request.args.get('transactionId'))
    order = db_session.query(Orders).filter(Orders.tx_id == tx_id).first()

    if order:
        line_pay = LinePay()
        line_pay.confirm(tx_id=int(tx_id), amount=float(order.amount))
        order.is_pay = True
        db_session.commit()

        msg = order.display_receipt()
        config.line_bot_api.push_message(to=order.user_id, messages=msg)

        return '<h1>Your payment is successful. Thx for your purchase.</h1>'


# https://rvproxy.fun2go.energy/cancel
@app.route("/cancel")
def cancel():
        return '<h1>Your payment is failed.</h1>'


@app.route("/liffpay", methods=['GET'])
def liffpay():
    redirect_url = request.args.get('liff.state').split('redirect_url=')[-1]
    return redirect(redirect_url)


@app.route("/liffpay_req", methods=['GET'])
def liffpay_req():
    result = dict(parse_qsl(request.args.get('liff.state')))
    result['paymentAccessToken'] = result.pop('?paymentAccessToken')
    print(result)
    return render_template("linepay_request.html", result=result)


@app.route("/callback", methods=['POST'])
def callback():
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
    #try:
    #print(f"this is event: {event}")
    user_id = event.source.user_id
    user = db_session.get_or_create_user(user_id=user_id)
    cart = Cart(user_id=user_id)
    
    msg_text = str(event.message.text).lower()
    msg_reply = None
    if (msg_text in ['date', 'time', 'datetime']) or ('pls select date/time' in msg_text):
        datetime_confirm_template = ConfirmTemplate(
                text=f'Please Pick a Date/Time',
                actions=[
                    DatetimePickerAction(label="Date and Time",
                                            data='DatetimePickerAction:cart_datetime',
                                            mode='datetime',
                                            #initial=,
                                            #max=,
                                            #min=
                                            ),
                    MessageAction(label="Check Availablility", text="available")
                ])
        msg_reply = TemplateSendMessage(alt_text='Pick Date and Time', template=datetime_confirm_template)
    
    elif msg_text in ['i am ready to order', 'add', '加入購物車']:
        try:
            msg_reply = Products.product_carousel() # call class method
        except AttributeError as e:
            print(e)
            #config.line_bot_api.reply_message(event.reply_token, msg_reply)

    elif msg_text in ['my cart', 'cart', '我的購物車', "that's it"]:
        if cart.bucket():
            msg_reply = cart.display()
        else:
            msg_reply = TextSendMessage(text='Your cart is empty now!')

    elif msg_text == 'empty cart':
        cart.reset()
        msg_reply = TextSendMessage(text='Your cart is empty now!')

    elif "i'd like to order" in msg_text:
        product_name = msg_text.split('\n')[1]
        datetime = msg_text.split('\n')[3]
        num_item = msg_text.split('\n')[-1]
        #print(product_name, num_item)
        product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
        if product and num_item and num_item != '0' and num_item.isdigit():
            # after certain timeout, the cache will be dropped
            if cart.bucket() == None:
                #print('reset cache')
                cart.reset()
            cart.add(datetime=datetime, product=product_name, num=num_item)
            #print(cart.bucket().items())
            msg_reply = cart.reserve()
        else:
            reselect_confirm_template = ConfirmTemplate(
                text=f"Sorry, we don't have {product_name} or you forgot to enter a right amount.",
                actions=[
                    MessageAction(label='Add/Revise', text='add'),
                    MessageAction(label="That's it", text="that's it")
                ])
            msg_reply = TemplateSendMessage(alt_text='anything else?', template=reselect_confirm_template)
        """ except Exception as e:
            print(e) """

    elif 'processing' in msg_text:
        msg_reply = TextSendMessage(text="On the way")

    if (msg_reply is None): 
        msg_reply = [
            #TextSendMessage(text='''若要將商品加入購物車，請傳送訊息: 加入購物車\n若要顯示您的購物車，請傳送訊息: 我的購物車'''),
            TextSendMessage(text='''If you would like to add the product to the cart, please type: "time" or "date"'''),
            TextSendMessage(text='''If you would like to see the products in your cart, please type: "my cart" or "cart"''')
        ]

    config.line_bot_api.reply_message(
        event.reply_token,
        msg_reply)

    """ except LineBotApiError as e:
        print(f'err: {e}') """


@config.handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))
    action = data.get('action')
    
    if action == 'checkout':
        user_id = event.source.user_id
        cart = Cart(user_id=user_id)

        if not cart.bucket():
            msg_reply = TextSendMessage(text='Your cart is empty now.')
            config.line_bot_api.reply_message(
                        event.reply_token,
                        [msg_reply])
            return 'OK'
        
        order_id = str(uuid.uuid4())
        total = 0
        items = []
        packages = []
        package_count = 0
        for time, value in cart.bucket().items():
            #print(strptime(time), type(strptime(time)))
            package = {
                    "id": f"{order_id}-{package_count}",
                    "amount": 0,
                    "name": "Sample package",
                    "products": []
                }
            for product_name, num in value.items():
                product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
                item = Items(product_id=product.id,
                            reserved_datetime=strptime(time),
                            product_name=product.name,
                            product_price=product.price,
                            quantity=int(num),
                            order_id=order_id
                            )
                package_product={
                    "id": f"{product.id}",
                    "name": f"{product.name}",
                    "imageUrl": f"{product.image_url}",
                    "quantity": int(num),
                    "price": product.price
                }
                items.append(item)
                package["products"].append(package_product)
                package["amount"] += product.price * int(num)
                total += product.price * int(num)
            
            packages.append(package)
            package_count += 1

        # empty cart
        cart.reset()
        
        line_pay = LinePay()
        info = line_pay.pay(
                            amount=total,
                            order_id=order_id,
                            packages=packages)
        #print(info)
        pay_web_url = info['paymentUrl']['web']
        #print(pay_web_url)
        tx_id = info['transactionId']
        order = Orders(id=order_id,
                        tx_id=tx_id,
                        is_pay=False,
                        amount=total,
                        user_id=user_id)
        db_session.add(order)
        for item in items:
            db_session.add(item)
        db_session.commit()
        msg_reply = TemplateSendMessage(alt_text='Thx. Pls go ahead to the payment.',
                                        template=ButtonsTemplate(text='Thx. Pls go ahead to the payment.',
                                                                actions=[URIAction(label='Pay NT${}'.format(order.amount), 
                                                                                    uri=f'{config.LIFF_LINEPAY}?redirect_url={pay_web_url}')
                                                                                    ]
                                                                )
                                                                )
        config.line_bot_api.reply_message(event.reply_token, [msg_reply])
        return 'OK'

    if 'cart_datetime' in event.postback.data:
        if 'DatetimePickerAction' in event.postback.data:
            datetime = event.postback.params['datetime'].lower()
        elif 'PostbackAction' in event.postback.data:
            datetime = event.postback.data.lower().split('=')[-1]
    
        try:
            print(f"check {strptime(datetime)}")
            msg_reply = Products.product_carousel(datetime=strptime(datetime))
            config.line_bot_api.reply_message(
                        event.reply_token,
                        msg_reply)
        except AttributeError as e:
            print(e)


@config.handler.add(FollowEvent)
def handle_follow(event):
    db_session.get_or_create_user(event.source.user_id)

    config.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='welcome to linebot!'))


@config.handler.add(UnfollowEvent)
def handle_unfollow(event):
    unfollowing_user = db_session.get_or_create_user(event.source.user_id)
    print(f'Unfollow event from {unfollowing_user}')


if __name__ == "__main__":
    db_session.init_products()
    app.run(debug=True) # one web request is a thread 