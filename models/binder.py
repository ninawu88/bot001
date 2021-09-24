from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from database import Base # should be executed at the root package

class Binders(Base):
    __tablename__ = 'binders'
    
    id = Column(Integer, primary_key=True)
    plate = Column(String)
    created_time = Column(DateTime, default=func.now())
    user_id = Column("user_id", ForeignKey("users.id")) # Foreignkey(table_name.column_name)

