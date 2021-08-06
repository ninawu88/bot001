from re import S
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

    items = relationship('Items', backref='order') # relationship(cls, backref='var_name')
    # order.items
    # item.order

