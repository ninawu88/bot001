import json
import requests
from flask import url_for
import config
from linepay import LinePayApi


linepay_api = LinePayApi(config.LINE_PAY_ID, config.LINE_PAY_SECRET, is_sandbox=True)

class LinePay():
    def __init__(self, currency='TWD'):
        self.confirm_url = url_for('.confirm', _external=True, _scheme='https') #https://rvproxy.fun2go.energy/confirm
        self.cancel_url = url_for('.cancel', _external=True, _scheme='https') #https://rvproxy.fun2go.energy/cancel
        self.currency=currency
    
    def pay(self, amount, order_id, packages=[]):
        request_options = {
            "amount": amount,
            "currency": self.currency,
            "orderId": order_id,
            "packages": packages,
            "redirectUrls": {
                "confirmUrl": self.confirm_url,
                "cancelUrl": self.cancel_url
            }
        }

        response = linepay_api.request(request_options)

        return self._check_response(response)

    def confirm(self, tx_id, amount):
        data = json.dumps({
                    'amount' : amount,
                    'currency' : self.currency
        }).encode('utf-8')

        response = requests.post(config.CONFIRM_API_URL.format(tx_id), headers=self._headers(), data=data)

        return self._check_response(response)

    def _check_response(self, response):
        res_json = response.json()
        #print(res_json)

        if 200 <= response.status_code < 300:
            if res_json['returnCode'] == '0000':
                return res_json['info']

            raise Exception(f"{res_json['returnCode']}:{res_json['returnMessage']}")




