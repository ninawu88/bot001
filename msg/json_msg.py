# import library
from linebot.models import *
from urllib.parse import quote

# custom package
import config


class product_bubble():
    def __init__(self, product, datetime):
        self.product = product
        self.datetime = datetime

    def gen_product_bubble(self):
        uri_action = URIAction(
                    label='Enter Amount', 
                    uri=f"https://line.me/R/oaMessage/{config.Bot_ID}/?" + 
                        quote(f"Product:\n{self.product.name}\nDatetime:\n{self.datetime}\nI'd like to order:\n(Pls type in number)\n")
                        )   
        datetimepicker = DatetimePickerAction(
                            label="Date and Time",
                            data='DatetimePickerAction:cart_datetime',
                            mode='datetime',
                            #initial=,
                            #max=,
                            #min=
                            )
        return BubbleContainer(
            hero=ImageComponent(
                size="full",
                aspect_ratio="20:13",
                aspect_mode="cover",
                url=self.product.image_url
            ),
            body=BoxComponent(
                layout="vertical",
                spacing="sm",
                contents=[
                    TextComponent(
                        text=self.product.name,
                        wrap=True,
                        weight="bold",
                        size="xl"),
                    BoxComponent(
                        layout="baseline",
                        contents=[
                            TextComponent(
                                text=f"NT${self.product.price}",
                                wrap=True,
                                weight='bold',
                                size= "xl",
                                flex=0
                            )
                        ]
                    ),
                    TextComponent(
                        margin='md',
                        text=f"{self.product.desc or ''} @ {self.datetime}",
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