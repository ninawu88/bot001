from flask import request
from flask_restful import Api, Resource, reqparse
from pprint import pprint
from datetime import datetime

#custom lib
import config
from models.mashamallow import ModemSchema
from models.modem import Modem
from database import db_session


ModemSchema = ModemSchema()

def strf_datetime(dt):
    date_args = [u for i in dt.split(',') for u in i.split(' ') if all([u != cond for cond in ['', 'PM']])]
    time_args = date_args[-1].split(':')
    return str(datetime(
                year=int(date_args[2]), month=int(datetime.strptime(date_args[0], "%b").month), day=int(date_args[1]), 
                hour=int(time_args[0]), minute=int(time_args[1]), second=int(time_args[2]))
                )

class test(Resource):
    def get(self):
        args = request.args
        return args, 200

    def post(self):
        data = request.get_json() # return as a dict
        pprint(data)

        for i in ['gpsTime', 'rtcTime', 'posTime']:
            if data.get(i):
                data[i] = strf_datetime(data[i])

        db_session.add(Modem(**ModemSchema.load(data)))
        db_session.commit()

        #config.logger.debug([type(i) for i in data.values()])
        return data, 201
