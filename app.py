# import library 
import requests
from flask import url_for, render_template, redirect
from flask import Flask, request, abort, render_template, redirect, url_for
from flask_restful import Api, Resource, reqparse
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *
from linepay import LinePayApi

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, inspect
from sqlalchemy.orm import relationship

from flask_marshmallow import Marshmallow

from urllib.parse import quote, parse_qsl
import uuid
from cachelib import SimpleCache
from datetime import datetime
def strptime(time):
    if 't' in time:
        return datetime.strptime(time[2:], '%y-%m-%dt%H:%M')
    else:
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
def strf_datetime(dt):
    date_args = [u for i in dt.split(',') for u in i.split(' ') if all([u != cond for cond in ['','PM','AM']])]
    #config.logger.debug(date_args)
    time_args = date_args[-1].split(':')
    #config.logger.debug(time_args)
    return str(datetime(
                year=int(date_args[2]), month=int(datetime.strptime(date_args[0], "%b").month), day=int(date_args[1]), 
                hour=int(time_args[0]), minute=int(time_args[1]), second=int(time_args[2]))
                )

# import custom module
import config
from database import db_session, Base, engine

app = Flask(__name__)

##======================DB==================================
# add new method to the scoped session instance 
@app.before_first_request
def init_tables():
    result = init_db()
    if result:
        db_session.add_all(product_lst) # a way to insert many query
        db_session.add_all(scooter_lst)
        db_session.commit()

def init_db():
    if inspect(engine).has_table('products'):
        return False
    else:    
        Base.metadata.create_all(bind=engine)
        return True

def get_or_create_user(user_id):
    user = Users.query.filter_by(id=user_id).first()
    #print(f'{user} in db')
    
    if not user:
        profile = config.line_bot_api.get_profile(user_id)
        # insert entries into the database
        user = Users(id=user_id, nick_name=profile.display_name, image_url=profile.picture_url)
        db_session.add(user) # insert query
        db_session.commit()
        #print(f"Add {user} to db")
    return user

class Users(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    nick_name = Column(String)
    image_url = Column(String(length=256))
    created_time = Column(DateTime, default=datetime.now())
    
    def __repr__(self):
        return f'<User {self.nick_name!r}>'

class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    desc = Column(String)
    image_url = Column(String(length=256))
    
    # print an instance
    def __repr__(self):
        return f'<Products {self.name!r}>'

    @classmethod
    def product_carousel(cls, datetime='Pls Select Date/Time'):
        products = cls.query.all()

        bubbles = []
        for product in products:
            uri_action = URIAction(
                    label='Enter Amount', 
                    uri=f"https://line.me/R/oaMessage/{config.Bot_ID}/?" + 
                        quote(f"Product:\n{product.name}\nDatetime:\n{datetime}\nI'd like to order:\n(Pls type in number)\n")
                        )   
            datetimepicker = DatetimePickerAction(
                            label="Date and Time",
                            data='DatetimePickerAction:cart_datetime',
                            mode='datetime',
                            #initial=,
                            #max=,
                            #min=
                            )
            bubble = BubbleContainer(
                hero=ImageComponent(
                    size="full",
                    aspect_ratio="20:13",
                    aspect_mode="cover",
                    url=product.image_url
                ),
                body=BoxComponent(
                    layout="vertical",
                    spacing="sm",
                    contents=[
                        TextComponent(
                            text=product.name,
                            wrap=True,
                            weight="bold",
                            size="xl"),
                        BoxComponent(
                            layout="baseline",
                            contents=[
                                TextComponent(
                                    text=f"NT${product.price}",
                                    wrap=True,
                                    weight='bold',
                                    size= "xl",
                                    flex=0
                                )
                            ]
                        ),
                        TextComponent(
                            margin='md',
                            text=f"{product.desc or ''} @ {datetime}",
                            wrap=True,
                            size='xs',
                            color='#aaaaaa'
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout="vertical",
                    spacing="sm",
                    contents=[
                        ButtonComponent(
                            style="primary",
                            color='#1DB446',
                            action=uri_action
                        ),
                        ButtonComponent(
                            style="primary",
                            color='#1DB446',
                            action=datetimepicker
                        ),
                    ]
                )
            )
            bubbles.append(bubble)
        
        return FlexSendMessage(alt_text='IE125 product carousel', contents=CarouselContainer(contents=bubbles))

product_lst = [Products(name='IE125_carstuff', 
                        image_url='https://img.carstuff.com.tw/images/stories/2019/Steven/12/9/emoving/1%20(2).jpg',
                        price=600,
                        desc='一天600元'),
               Products(name='IE125_emoving', 
                        image_url='https://www.e-moving.com.tw//emwspublished/N0003/LV220210527120042.png',
                        price=700,
                        desc='一天700元'),
               Products(name='IE125_蝦皮', 
                        image_url='https://cf.shopee.tw/file/abe4ffc8ac38151920239074e2f6da1a',
                        price=800,
                        desc='一天800元')]

class Scooters(Base):
    __tablename__ = 'scooters'
    id = Column(Integer, primary_key=True)
    license_plate = Column(String)
    modem_id = Column(String)
    status = Column(Integer) # 0:idle, 1:used, ...
    plan = Column(String)
    location = Column(String)
    
    def __repr__(self):
        return f'<Products {self.name!r}>'

scooter_lst = [Scooters(license_plate='EPA0276', 
                        modem_id='357364080996860',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0277', 
                        modem_id='357364080584757',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0278', 
                        modem_id='357364081020470',
                        status=0,
                        plan='rent',
                        location='澎湖'),
                Scooters(license_plate='EPA0279', 
                        modem_id='357364081020397',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0280', 
                        modem_id='357364081020124',
                        status=0,
                        plan='rent',
                        location='澎湖'),
                Scooters(license_plate='EPA0281', 
                        modem_id='357364080997793',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0282', 
                        modem_id='357364080609265',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0283', 
                        modem_id='357364080609174',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0285', 
                        modem_id='357364081002379',
                        status=0,
                        plan='rent',
                        location='澎湖'),
                Scooters(license_plate='EPA0286', 
                        modem_id='357364081006461',
                        status=0,
                        plan='rent',
                        location='竹北'),
            ]   

class Orders(Base):
    __tablename__= 'orders'

    id = Column(String, primary_key=True)
    amount = Column(Float)
    tx_id = Column(Integer)
    is_pay = Column(Boolean, default=False)
    created_time = Column(DateTime, default=datetime.now())

    user_id = Column(String, ForeignKey("users.id")) # Foreignkey(table_name.column_name)

    def display_receipt(self):
        item_box_components = []
        for item in self.items:
            item_box_components.append(BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text=f'{item.quantity} x {item.product_name}',
                                size='sm',
                                color='#555555',
                                flex=0),
                    TextComponent(text=f'NT${item.quantity * item.product_price}',
                                size='sm',
                                color='#111111',
                                align='end')
                                ]
            )
            )
        
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='RECEIPT',
                                weight='bold',
                                color='#1DB446',
                                size='sm'),
                    TextComponent(text='Fun2Go',
                                weight='bold',
                                size='xxl',
                                margin='md'),
                    TextComponent(text='Linebot Store',
                                size='xs',
                                color='#aaaaaa',
                                wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=item_box_components
                    ),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(
                                        text='TOTAL',
                                        size='sm',
                                        color='#555555',
                                        flex=0),
                                    TextComponent(
                                        text=f'NT${self.amount}',
                                        size='sm',
                                        color='#111111',
                                        align='end')    
                                ]
                            )
                        ]
                    )
                ]
            )
        )

        return FlexSendMessage(alt_text='receipt', contents=bubble)

class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    reserved_datetime=Column(DateTime)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String)
    product_price = Column(Integer)
    quantity = Column(Integer)
    created_time = Column(DateTime, default=datetime.now())
    order_id = Column(String, ForeignKey("orders.id"))

class Binders(Base):
    __tablename__ = 'binders'
    id = Column(Integer, primary_key=True)
    plate = Column(String)
    created_time = Column(DateTime, default=datetime.now())
    user_id = Column(String, ForeignKey("users.id")) # Foreignkey(table_name.column_name)

class Modem_750(Base):
    __tablename__ = 'modem_750'
    index = Column(Integer, primary_key=True)
    id = Column(Integer)
    transactionId = Column(String)
    messageEncoding = Column(String)
    messageType = Column(String)
    modemId = Column(String, ForeignKey("scooters.modem_id"))
    messageId = Column(String)
    dataLength = Column(String)
    gpsTime = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    direction = Column(Float)
    odometer = Column(Integer)
    hdop = Column(Float)
    satellites = Column(Integer)
    ioStatus = Column(String)
    reserved = Column(String)
    mainPowerVoltage = Column(Float)
    backupBatteryVoltage = Column(Float)
    rtcTime = Column(DateTime)
    posTime = Column(DateTime)
    csq = Column(String)
    mcuMotorRpm = Column(Integer)
    obdSpeed = Column(Integer)
    bmsBatterySoc = Column(Integer)
    mtrOdoData = Column(String)
    keyStatus = Column(String)
    chargingStatus = Column(String)

class Modem_275(Base):
    __tablename__ = 'modem_275'
    index = Column(Integer, primary_key=True)
    id = Column(Integer)
    transactionId = Column(String)
    messageEncoding = Column(String)
    messageType = Column(String)
    modemId = Column(String, ForeignKey("scooters.modem_id"))
    messageId = Column(String)
    dataLength = Column(String)
    gpsTime = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    speed = Column(Float)
    direction = Column(Float)
    odometer = Column(Integer)
    hdop = Column(Float)
    satellites = Column(Integer)
    ioStatus = Column(String)
    reserved = Column(String)
    mainPowerVoltage = Column(Float)
    backupBatteryVoltage = Column(Float)
    rtcTime = Column(DateTime)
    posTime = Column(DateTime)
    deviceImei = Column(String)
    simCardIccid = Column(String)
    simCardImsi =  Column(String)
    deviceModelName = Column(String)
    deviceFwVersion = Column(String)
    deviceHwVersion = Column(String)

Users.orders = relationship('Orders', backref='user') # relationship(cls_name, backref='var_name')
    # user.orders
    # order.user, for backref
Users.binders = relationship('Binders', backref='user') 
Orders.items = relationship('Items', backref='order') 
    # order.items
    # item.order, for backref
Scooters.modem_750 = relationship('Modem_750', backref='scooter')
Scooters.modem_275 = relationship('Modem_275', backref='scooter')
##======================Marshmallow==================================
mars = Marshmallow(app)
class ModemSchema_750(mars.SQLAlchemyAutoSchema):
    class Meta:
        model = Modem_750
        include_fk = True

class ModemSchema_275(mars.SQLAlchemyAutoSchema):
    class Meta:
        model = Modem_275
        include_fk = True
##======================Cache==================================
cache = SimpleCache(threshold=500, default_timeout=0) # it is like a dict {id:<dict>}

class Cart(object):
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id

    def bucket(self):
        return cache.get(key=self.user_id) # return a dict or None

    def add(self, datetime, product, num):
        bucket = cache.get(key=self.user_id)
        #print(bucket)
        if bucket == None:
            cache.add(key=self.user_id, value={datetime:{product:int(num)}}) # equal to cache.set()
        elif datetime in bucket.keys():
            bucket[datetime].update({product:int(num)}) # dict.update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating
        else:
            bucket.update({datetime:{product:int(num)}}) # dict.update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating

    def reset(self):
        cache.set(key=self.user_id, value={})

    def reserve(self):
        bubbles = []
        print(self.bucket())

        for datetime, value in self.bucket().items():
            reserve_box_comp = []
            for product_name, num in value.items():
                product = Products.query.filter(Products.name.ilike(product_name)).first()
                reserve_box_comp.append(BoxComponent(
                        layout='horizontal',
                        spacing='sm',
                        contents=[
                            TextComponent(text=f"{product.name}", size='sm', color='#555555', flex=0, align='start'),
                            TextComponent(text=f"{num}", size='sm', color='#111111', align='end')
                        ]
                    )
                )
                
            bubble = BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        TextComponent(
                            text=f"Reserving at {datetime}",
                            weight='bold',
                            size='xl',
                            wrap=True,
                            contents=[]
                        ),
                        SeparatorComponent(),
                        BoxComponent(
                            layout='vertical',
                            margin='xxl',
                            spacing='sm',
                            contents=reserve_box_comp
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        ButtonComponent(
                            style='primary',
                            action=PostbackAction(
                                label="Add/Revise",
                                text="Processing...Add/Revise",
                                data=f"PostbackAction:cart_datetime={datetime}"
                            )
                        ),
                        ButtonComponent(
                            action=MessageAction(
                                label="That's it", 
                                text="that's it"
                            )
                        )
                    ]
                )
            )
            bubbles.append(bubble)
        
        return FlexSendMessage(alt_text='IE125 reserve carousel', contents=CarouselContainer(contents=bubbles))

    def display(self):
        total = 0
        product_box_comp = []

        for datetime, value in self.bucket().items():
            #print(datetime, value)
            product_box_comp.append(BoxComponent(
                    layout='vertical',
                    contents=[TextComponent(text=f"{datetime}",
                                        size='sm', color='#555555', flex=0, weight="bold", align="end"),
                            SeparatorComponent(margin='sm')
                                ]
                )
                )
            for product_name, num in value.items():
                product = Products.query.filter(Products.name.ilike(product_name)).first()
                amount = product.price * int(num)
                total += amount

                product_box_comp.append(BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text=f"{num} x {product_name}",
                                        size='sm', color='#555555', flex=0),
                        TextComponent(text=f"NT$ {amount}",
                                        size='sm', color='#111111', align='end')
                    ]
                )
                )
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=f"Here is your order:",
                                        size='md', wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=product_box_comp
                    ),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='Total',
                                                    size='sm', color='#555555', flex=0),
                                    TextComponent(text=f'NT$ {total}',
                                                    size='sm', color='#111111', align='end')
                                ]
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#1DB446',
                        action=PostbackAction(label='Checkout',
                                                display_text='checkout',
                                                data='action=checkout')
                    ),
                    BoxComponent(
                        layout='horizontal',
                        spacing='md',
                        contents=[
                            ButtonComponent(
                                style='primary',
                                color='#aaaaaa',
                                action=MessageAction(label='Empty Cart',
                                                        text='empty cart')
                            ),
                            ButtonComponent(
                                style='primary',
                                color='#aaaaaa',
                                flex=2,
                                action=MessageAction(label='Add',
                                                        text='add')
                            )
                        ]
                    )
                ]
            )
        ) 

        return FlexSendMessage(alt_text='Cart', contents=bubble)

##======================LinePay==================================
linepay_api = LinePayApi(config.LINE_PAY_ID, config.LINE_PAY_SECRET, is_sandbox=True)

class LinePay():
    def __init__(self, currency='TWD'):
        self.confirm_url = url_for('.confirm', _external=True, _scheme='https') #https://rvproxy.fun2go.energy/confirm
        self.cancel_url = url_for('.cancel', _external=True, _scheme='https') #https://rvproxy.fun2go.energy/cancel
        self.channel_id = config.LINE_PAY_ID
        self.secret=config.LINE_PAY_SECRET
        self.currency=currency

    def _headers(self, **kwargs):
        return {**{'Content-Type':'application/json',
                            'X-LINE-ChannelId':self.channel_id,
                            'X-LINE-ChannelSecret':self.secret},
                            **kwargs}

    def pay(self, amount, order_id, packages=[]):
        request_options = {
            "amount": amount,
            "currency": self.currency,
            "orderId": order_id,
            "packages": packages,
            "redirectUrls": {
                "confirmUrl": self.confirm_url,
                "cancelUrl": self.cancel_url
            }
        }

        response = linepay_api.request(request_options) # return a dict, where the key ['info'] also holds a dict
        return self._pay_check_response(response)

    def confirm(self, tx_id, amount):
        response = linepay_api.confirm(
            tx_id,
            amount,
            self.currency
        )
        return self._confirm_check_response(response)

    def _pay_check_response(self, response):
        transaction_id = int(response.get("info", {}).get("transactionId", 0))
        check_result = linepay_api.check_payment_status(transaction_id)
        config.logger.debug(check_result)
        config.logger.debug(response.get("info"))
        if check_result.get("returnCode") == '0000':
            return response.get("info")
        else:
            raise Exception(f'{check_result.get("returnCode")}:{ check_result.get("returnMessage")}')

    def _confirm_check_response(self, response):
        transaction_id = int(response.get("info", {}).get("transactionId", 0))
        check_result = linepay_api.check_payment_status(transaction_id)
        config.logger.debug(check_result)
        config.logger.debug(response.get("info"))
        if check_result.get("returnCode") == '0123':
            return response.get("info")
        else:
            raise Exception(f'{check_result.get("returnCode")}:{ check_result.get("returnMessage")}')

##======================API==================================
yes_post_api = Api(app)
class test(Resource):
    def get(self):
        args = request.args
        return args, 200

    def post(self):
        data = request.get_json() # return as a dict
        
        for i in ['gpsTime', 'rtcTime', 'posTime']:
            if data.get(i):
                data[i] = strf_datetime(data[i])
        
        _msg_id = data.get('messageId')
        _modem_id = data.get('modemId')
        if Scooters.query.filter(Scooters.modem_id.ilike(_modem_id)).first():
            license_plate = Scooters.query.filter(Scooters.modem_id.ilike(_modem_id)).first().license_plate
            
            if _msg_id == '750':
                db_session.add(Modem_750(**ModemSchema_750().load(data)))
                config.logger.info(Modem_750.query.all()[-1].scooter.license_plate)
                #config.logger.info(Modem_750.query.first().scooter.license_plate)
                #config.logger.info(Scooters.query.filter(Scooters.license_plate.ilike(Modem_750.query.first().scooter.license_plate)).first().modem_750)
                #config.logger.info(data)
            elif _msg_id == '275':
                db_session.add(Modem_275(**ModemSchema_275().load(data)))
                config.logger.info(data)
            else:
                _user_id = Binders.query.filter(Binders.plate.ilike(license_plate)).first()
                config.logger.info(_user_id)
                if _msg_id == '180': 
                    config.logger.info('Event Reserve Table')
                    config.logger.info(data)
                elif _msg_id == '177':
                    config.logger.info('Tow Alert')
                    config.logger.info(data)
                elif any([_msg_id == s for s in ('160', '166', '167', '168', '175')]):
                    config.logger.info('Format_extend')
                    config.logger.info(data)
                elif any([_msg_id == s for s in ('809', '810', '500', '501', '402')]):
                    config.logger.info('Format_std')
                    config.logger.info(data)

        else:
            config.logger.warn(f'{_modem_id} does not match any plate number in db')    

        #config.logger.info(Scooters)        
        #config.logger.info(Binders.query.filter(Binders.plate.ilike('epa0277')).first())

        try:
            db_session.commit()
        except:
            db_session.rollback()
        finally:
            db_session.close()
        #config.logger.debug([type(i) for i in data.values()])
        return data, 201

yes_post_api.add_resource(test, '/test')

##======================Temp Var==================================
plates = [
    'epa0277',
    'epa0278',
    'epa0279',
    'epa0280',
    'epa0281',
    'epa0282',
    'epa0283',
    'epa0285',
    'epa0286',
    'epa0276',
    ]
##======================Flask App==================================
# an “on request end” event
# automatically remove database sessions at the end of the request 
# or when the application shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

##======================Route==================================
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
    order = Orders.query.filter_by(tx_id=tx_id).first()

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


##======================Handle msg==================================
@config.handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    #try:
    #print(f"this is event: {event}")
    user_id = event.source.user_id
    user = get_or_create_user(user_id=user_id)
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
        product = Products.query.filter(Products.name.ilike(product_name)).first()
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

    elif (msg_reply is None): 
        msg_reply = [
            #TextSendMessage(text='''若要將商品加入購物車，請傳送訊息: 加入購物車\n若要顯示您的購物車，請傳送訊息: 我的購物車'''),
            TextSendMessage(text='''If you would like to add the product to the cart, please type: "time" or "date"'''),
            TextSendMessage(text='''If you would like to see the products in your cart, please type: "my cart" or "cart"''')
        ]


    if 'status' in msg_text:
        usingmotor = URIAction(
                    label='usingmotor', 
                    uri=f"https://line.me/R/oaMessage/{config.Bot_ID}/?" + 
                        quote(f"usingmotor\nlicensePlate:\n(Pls type in plate number)\n")
                        )

        chargedata = URIAction(
                    label='chargedata', 
                    uri=f"https://line.me/R/oaMessage/{config.Bot_ID}/?" + 
                        quote(f"chargedata\nlicensePlate:\n(Pls type in plate number)\n")
                        )

        msg_reply = TextSendMessage(
                        text='Which status?',
                        quick_reply=QuickReply(items=[
                            QuickReplyButton(action=usingmotor),
                            QuickReplyButton(action=chargedata),
                        ])
                    )   

    elif (any([s in msg_text for s in ('usingmotor', 'chargedata')])) and ('licenseplate' in msg_text):
        yes_api = msg_text.split('\n')[0]
        licensePlate = msg_text.split('\n')[-1]
        config.logger.debug(licensePlate)

        if licensePlate in plates:
            plate_confirm_template = ConfirmTemplate(
                text=f'Process {yes_api} with License Plate:\n{licensePlate}',
                actions=[
                    PostbackAction(
                        label="Confirm",
                        data=f"api={yes_api}&licensePlate={licensePlate}"
                    ),
                    MessageAction(label="Re-Type", text="Status"),
                ])
            msg_reply = TemplateSendMessage(alt_text=f'Process {yes_api} with License Plate: {licensePlate}', template=plate_confirm_template)
        else:
            msg_reply = TextSendMessage(text='The License Plate does not exist, please check again')
    

    if 'my location' in msg_text:
        msg_reply = TextSendMessage(
                        text='Share your location by clicking the button below',
                        quick_reply=QuickReply(items=[QuickReplyButton(
                                                        action=LocationAction(label='mylocation'))
                        ])
                    )

    if 'binder' in msg_text:
        msg_reply = TemplateSendMessage(alt_text='Bind your Line account to a License plate',
                                        template=ButtonsTemplate(text='Bind your Line account to a License plate',
                                                                actions=[URIAction(label='Type plate number', 
                                                                                    uri=f"https://line.me/R/oaMessage/{config.Bot_ID}/?" + 
                                                                                        quote(f"Bind to licensePlate:\n(Pls type in plate number, only characters allowed)\n")
                                                    )
                                                ]
                                            )
                                        )
    elif all([s in msg_text for s in ('bind', 'licenseplate')]): 
        licensePlate = msg_text.split('\n')[-1]
        if licensePlate in plates:
            bind_confirm_template = ConfirmTemplate(
                text=f'Bind with License Plate:\n{licensePlate.upper()}',
                actions=[
                    PostbackAction(
                        label="Confirm",
                        data=f"action=bind&licensePlate={licensePlate}&userId={user_id}"
                    ),
                    MessageAction(label="Re-Type", text="Binder"),
                ])
            msg_reply = TemplateSendMessage(alt_text=f'Bind with License Plate:\n{licensePlate}', template=bind_confirm_template)
        else:
            msg_reply = TextSendMessage(text='The License Plate does not exist, please check again')


    config.line_bot_api.reply_message(
        event.reply_token,
        msg_reply)

    """ except LineBotApiError as e:
        print(f'err: {e}') """


##======================Handle Postback==================================
@config.handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))
    action = data.get('action')
    api = data.get('api')
    config.logger.debug(data)
    
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
                product = Products.query.filter(Products.name.ilike(product_name)).first()
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

    if any([s == api for s in ('usingmotor', 'chargedata')]):
        payload = {}
        for key in data.keys():
            if key != "api":
                payload[key] = data.get(key)
        if payload.get('licensePlate'):
            payload['licensePlate'] = payload.get('licensePlate').upper()
        config.logger.debug(payload)

        resp = requests.post(config.yes_api_base + api, json=payload)      
        config.logger.debug(resp.text)

    if action == 'bind':
        licensePlate = data.get('licensePlate')
        user_id = data.get('userId')
        binder = Binders(plate=licensePlate, user_id=user_id)
        db_session.add(binder)
        db_session.commit()
        config.logger.debug((licensePlate, user_id))


@config.handler.add(FollowEvent)
def handle_follow(event):
    get_or_create_user(event.source.user_id)

    config.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='welcome to linebot!'))


@config.handler.add(UnfollowEvent)
def handle_unfollow(event):
    unfollowing_user = get_or_create_user(event.source.user_id)
    print(f'Unfollow event from {unfollowing_user}')


if __name__ == "__main__":
    init_tables()
    app.run(debug=False) # one web request is a thread 