from flask import request
from flask_restful import Api, Resource, reqparse

class test(Resource):
    def get(self):
        
        args = request.args
        return args, 200

    def post(self):
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('age', required=True)
        parser.add_argument('city', required=True)
        args = parser.parse_args()
        '''
        #print(request.data)
        #print(request.form)
        data = request.get_json()
        print(data)
        return data, 201
