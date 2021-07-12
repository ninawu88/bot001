from sqlalchemy_utils import database_exists
from models.products import Products, product_lst
from models.users import Users
from database import Base

import config


def init_products(self):
    result = init_db()
    if result:
        init_data = product_lst
        self.bulk_save_objects(init_data) # a way to insert many query
        self.commit()

    #print(self.query(Products).all())


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    #import yourapplication.models
    if database_exists(config.db_path):
        return False
    else:    
        Base.metadata.create_all(bind=engine)
        return True


def get_or_create_user(self, user_id):
    user = self.query(Users).filter_by(id=user_id).first()
    
    if not user:
        profile = config.line_bot_api.get_profile(user_id)
        # insert entries into the database
        user = Users(id=user_id, nick_name=profile.display_name, image_url=profile.picture_url)
        self.add(user) # insert query
        self.commit()
        print(f"Add {user} to db")

    return user