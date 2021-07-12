# pip3 install cachelib

from cachelib import SimpleCache

cache = SimpleCache() # it is like a dict {id:<dict>}
#print(dir(cache))
#print(cache.get_many())

class Cart(object):
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id

    def bucket(self):
        return cache.get(key=self.user_id) # return a dict or None

    def add(self, product, time, num):
        bucket = cache.get(key=self.user_id)
        if bucket == None:
            cache.add(key=self.user_id, value={product:{'amount':int(num),'datetime':time}}) # equal to cache.set()
        else:
            bucket.update({product:{'amount':int(num),'datetime':time}}) # dict,update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating
            #print(f"this is {bucket}")
    
    def reset(self):
        cache.set(key=self.user_id, value={})

""" cart = Cart(0)
print(cart.bucket())
cart.add('coffee', '2')
cart.add('tea', '2')
print(cart.bucket())
 """