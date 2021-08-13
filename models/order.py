from typing import Text
from sqlalchemy import Column, DateTime, String, Integer, func, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from linebot.models import *
from database import Base

class Orders(Base):
    __tablename__= 'orders'

    id = Column(String, primary_key=True)
    amount = Column(Integer)
    tx_id = Column(String)
    is_pay = Column(Boolean, default=False)
    created_time = Column(DateTime, default=func.now())
    user_id = Column("user_id", ForeignKey("users.id")) # Foreignkey(table_name.column_name)

    items = relationship('Items', backref='order') # relationship(cls_name, backref='var_name')
    # order.items
    # item.order, for backref

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
        

