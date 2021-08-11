import json
import requests
from flask import url_for
import config

class LinePay():
    def __init__(self, currency='TWD'):
        self.channel_id = config.LINE_PAY_ID
        self.secret=config.LINE_PAY_SECRET
        self.redirect_url = url_for('.confirm', _external=True, _scheme='https')
        print(self.redirect_url)
        self.currency=currency
    
    def _headers(self, **kwargs):
        return {**{'Content-Type':'application/json',
                            'X-LINE-ChannelId':self.channel_id,
                            'X-LINE-ChannelSecret':self.secret},
                            **kwargs}
    
    def pay(self, product_name, amount, order_id, product_image_url=None):
        data = {
                        'productName' : product_name,
                        'amount' : amount,
                        'currency' : self.currency,
                        'confirmUrl' : self.redirect_url,
                        'orderId' : order_id,
                        'productImageUrl' : product_image_url
        }

        response = requests.post(config.PAY_API_URL, headers=self._headers(), data=json.dumps(data).encode('utf-8'))

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
        print(res_json)

        if 200 <= response.status_code < 300:
            if res_json['returnCode'] == '0000':
                return res_json['info']

            raise Exception(f"{res_json['returnCode']}:{res_json['returnMessage']}")




