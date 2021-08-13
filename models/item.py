from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey
from sqlalchemy.engine import create_engine
from database import Base

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    reserved_datetime=Column(DateTime)
    product_id = Column(ForeignKey("products.id"))
    product_name = Column(String)
    product_price = Column(Integer)
    quantity = Column(Integer)
    created_time = Column(DateTime, default=func.now())
    order_id = Column("order_id", ForeignKey("orders.id"))

