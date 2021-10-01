from flask import request
from flask_restful import Api, Resource, reqparse

import config



class test(Resource):
    def get(self):
        args = request.args
        return args, 200

    def post(self):
        data = request.get_json() # return as a dict
        #config.logger.debug(data)
        #config.logger.debug([type(i) for i in data.values()])
        return data, 201
