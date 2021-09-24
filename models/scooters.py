# import library
from sqlalchemy import Column, Integer, String
from database import Base

# custom package

class Scooters(Base):
    # class attr
    # create a Table in database
    __tablename__ = 'scooters'
    id = Column(Integer, primary_key=True)
    license_plate = Column(String)
    modem_id = Column(String)
    status = Column(Integer) # 0:idle, 1:used, ...
    plan = Column(String)
    location = Column(String)
    
    # print an instance
    def __repr__(self):
        return f'<Products {self.name!r}>'


scooter_lst = [Scooters(license_plate='EPA0276', 
                        modem_id='357364080996860',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0277', 
                        modem_id='357364080584757',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0278', 
                        modem_id='357364081020470',
                        status=0,
                        plan='rent',
                        location='澎湖'),
                Scooters(license_plate='EPA0279', 
                        modem_id='357364081020397',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0280', 
                        modem_id='357364081020124',
                        status=0,
                        plan='rent',
                        location='澎湖'),
                Scooters(license_plate='EPA0281', 
                        modem_id='357364080997793',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0282', 
                        modem_id='357364080609265',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0283', 
                        modem_id='357364080609174',
                        status=0,
                        plan='rent',
                        location='竹北'),
                Scooters(license_plate='EPA0285', 
                        modem_id='357364081002379',
                        status=0,
                        plan='rent',
                        location='澎湖'),
                Scooters(license_plate='EPA0286', 
                        modem_id='357364081006461',
                        status=0,
                        plan='rent',
                        location='竹北'),
            ]   