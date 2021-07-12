# import library
from sqlalchemy import Column, Integer, String
from linebot.models import FlexSendMessage, CarouselContainer
from database import Base, db_session # should be executed at the root package

# custom package
import config
from models.cart import Cart
from msg.json_msg import product_bubble


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
    def product_carousel(cls, cart, datetime='Pls Select Date/Time'):
        products = db_session.query(cls).all()

        bubbles = []
        for product in products:
            bubble = product_bubble(product=product, datetime=datetime).gen_product_bubble()
            bubbles.append(bubble)
            #print(bubble)
        
        msg = FlexSendMessage(alt_text='IE125 product carousel', contents=CarouselContainer(contents=bubbles))
        return msg


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