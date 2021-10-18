from flask import request
from flask_restful import Api, Resource, reqparse
from pprint import pprint
from datetime import datetime

#custom lib
import config
from models.mashamallow import ModemSchema_750
from models.modem import Modem_750
from database import db_session


ModemSchema_750 = ModemSchema_750()

def strf_datetime(dt):
    date_args = [u for i in dt.split(',') for u in i.split(' ') if all([u != cond for cond in ['','PM','AM']])]
    #config.logger.debug(date_args)
    time_args = date_args[-1].split(':')
    #config.logger.debug(time_args)
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
        
        for i in ['gpsTime', 'rtcTime', 'posTime']:
            if data.get(i):
                data[i] = strf_datetime(data[i])
        
        msg_id = data['messageId']
        if msg_id == '750':
            db_session.add(Modem_750(**ModemSchema_750.load(data)))
        elif msg_id == '275':
            config.logger.info('Format_275')
            config.logger.info(data)
        elif msg_id == '180':
            config.logger.info('Event Reserve Table')
            config.logger.info(data)
        elif msg_id == '177':
            config.logger.info('Tow Alert')
            config.logger.info(data)
        elif any([msg_id == s for s in ('160', '166', '167', '168', '175')]):
            config.logger.info('Format_extend')
            config.logger.info(data)
        elif any([msg_id == s for s in ('809', '810', '500', '501', '402')]):
            config.logger.info('Format_std')
            config.logger.info(data)
        db_session.commit()

        #config.logger.debug([type(i) for i in data.values()])
        return data, 201
