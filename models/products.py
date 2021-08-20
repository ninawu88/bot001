# import library
from sqlalchemy import Column, Integer, String
from linebot.models import *
from database import Base, db_session # should be executed at the root package
from urllib.parse import quote

# custom package
import config

class Products(Base):
    # class attr
    # create a Table in database
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
        products = db_session.query(cls).all()

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