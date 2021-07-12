# pip3 install cachelib

# import libarys
from cachelib import SimpleCache
from linebot.models import *

# import custom packages
from database import db_session


cache = SimpleCache() # it is like a dict {id:<dict>}
#print(dir(cache))
#print(cache.get_many())

class Cart(object):
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id

    def bucket(self):
        return cache.get(key=self.user_id) # return a dict or None

    def add(self, datetime, product='', num='0'):
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
        #print(self.bucket())
    
    def reset(self):
        cache.set(key=self.user_id, value={})

    def display(self):
        total = 0
        product_box_comp = []

        #for product