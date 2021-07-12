# pip3 install cachelib

# import libarys
from cachelib import SimpleCache
from linebot.models import *

# import custom packages
from database import db_session
from models.products import Products
from msg.json_msg import cart_bubble, reserve_bubble


cache = SimpleCache() # it is like a dict {id:<dict>}
#print(dir(cache))
#print(cache.get_many())

class Cart(object):
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id

    def bucket(self):
        return cache.get(key=self.user_id) # return a dict or None

    def add(self, datetime, product, num):
        bucket = cache.get(key=self.user_id)
        print(bucket)
        print(self.user_id)
        print(datetime, product, num)
        if bucket == None:
            cache.add(key=self.user_id, value={datetime:{product:int(num)}}) # equal to cache.set()
        elif datetime in bucket.keys():
            bucket[datetime].update({product:int(num)}) # dict.update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating
        else:
            bucket.update({datetime:{product:int(num)}}) # dict.update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating
        print(self.bucket())
    
    def reset(self):
        cache.set(key=self.user_id, value={})

    def reserve(self):
        bubbles = []
        print(self.bucket())

        for datetime, value in self.bucket().items():
            reserve_box_comp = []
            for product_name, num in value.items():
                product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()

                reserve_box_comp.append(BoxComponent(
                        layout='horizontal',
                        spacing='sm',
                        contents=[
                            TextComponent(text=f"{product_name}", size='sm', color='#555555', flex=0, align='start'),
                            TextComponent(text=f"{num}", size='sm', color='#111111', align='end')
                        ]
                    )
                )
            #bubble = reserve_bubble(datetime=datetime, box=reserve_box_comp).gen_reserve_bubble()
            bubbles.append(reserve_bubble(datetime=datetime, box=reserve_box_comp).gen_reserve_bubble())
        msg = FlexSendMessage(alt_text='IE125 reserve carousel', contents=CarouselContainer(contents=bubbles))
        #msg = FlexSendMessage(alt_text='Cart', contents=bubble)
        return msg

    def display(self):
        total = 0
        product_box_comp = []
        print(self.bucket())

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
                product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
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
        return cart_bubble(box=product_box_comp, total=total).gen_cart_bubble()