from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
import config

engine = create_engine(config.db_path, convert_unicode=True)
#print(engine)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

if __name__ == "__main__":
    print(db_session.get_bind())
    a = db_session()
    b = db_session()
    print(a == b)
    print(a == db_session)
    print(b == db_session)
    print(dir(db_session))
    print(db_session == db_session())
    a = db_session()
    print(a == db_session())
    print(a == db_session.registry.registry.value)
    db_session.remove()
    print(db_session.get_bind())
    print(db_session.registry.registry.value)
