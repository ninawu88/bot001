# in a venv
# pip3 install SQLAlchemy==1.4.20
# pip3 install SQLAlchemy-Utils

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import config


# connection to resource
engine = create_engine(
    config.db_path, 
    convert_unicode=True # for string convertion
    )
#print(engine)

# func sessionmaker() is to make a session
# func scoped_session() is to register the session for becoming a global session
## which is to handle threads linking to multi web requests 
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# db_session is a registry holding a Session for all who ask for it 
# After calling registry, the session is then instantiated by sessionmaker 
# and be placed in a thread local storage
""" print(db_session)
print(db_session())
print(db_session.query_property)
print(dir(db_session))
print(dir(db_session())) """


# mapped class, which creates a registry and base class all at once.
# the combination of Table, mapper(), and class objects to define a mapped class. 
# declarative allows all three to be expressed at once within the class declaration.
Base = declarative_base()

# when methods are called on registry, they are proxied to the underlying Session being maintained by the registry
# or it is like a instance of a session. (although we didn't instantiate the sesssion by calling it)
Base.query = db_session.query_property()