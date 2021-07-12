# import library
from linebot.models import *
from urllib.parse import quote

# custom package
import config


class reserve_bubble():
    def __init__(self, datetime, box):
        self.datetime = datetime
        self.box = box

    def gen_reserve_bubble(self):
        bubble = BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        TextComponent(
                            text=f"Reserving at {self.datetime}",
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
                            contents=self.box
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
                                text="Add/Revise",
                                data=f"PostbackAction:cart_datetime={self.datetime}"
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
        return bubble


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


class cart_bubble():
    def __init__(self, box, total):
        self.box = box
        self.total = total
    
    def gen_cart_bubble(self):
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
                        contents=self.box
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
                                    TextComponent(text=f'NT$ {self.total}',
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

        msg = FlexSendMessage(alt_text='Cart', contents=bubble)
        return msg