from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base # should be executed at the root package

class Users(Base):
    # class attr
    # create a Table in database
    __tablename__ = 'users'
    #i = 123
    id = Column(String, primary_key=True)
    nick_name = Column(String)
    image_url = Column(String(length=256))
    created_time = Column(DateTime, default=func.now())

    """ # instance attr
    # without init, one could use argument to modify the class attr. ex. Users(id='123')
    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email"""
    
    # print an instance
    def __repr__(self):
        return f'<User {self.nick_name!r}>'


""" print(Users().query.all())
print(Users().query.session)
a = Users()
print(a)
print(a.i, a.id, a.nick_name)
a = Users(i = 345, id=456)
print(a.i, a.id, a.nick_name)
print(a.query.all()) """