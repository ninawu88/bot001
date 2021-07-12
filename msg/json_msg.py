from linebot.models import *

import config

def ie125_product_bubble(product):
    return BubbleContainer(
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
                    text=f"{product.desc or ''}",
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
                    action=DatetimePickerAction(
                        label="Date and Time",
                        data=product.name,
                        mode='datetime',
                        #initial=,
                        #max=,
                        #min=
                    )
                )
            ]
        )
    )