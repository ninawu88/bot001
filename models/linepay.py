import json
import requests
from flask import url_for, render_template, redirect
from urllib.parse import parse_qsl, urlencode
from linepay import LinePayApi

import config

linepay_api = LinePayApi(config.LINE_PAY_ID, config.LINE_PAY_SECRET, is_sandbox=True)

class LinePay():
    def __init__(self, currency='TWD'):
        self.confirm_url = url_for('.confirm', _external=True, _scheme='https') #https://rvproxy.fun2go.energy/confirm
        self.cancel_url = url_for('.cancel', _external=True, _scheme='https') #https://rvproxy.fun2go.energy/cancel
        self.channel_id = config.LINE_PAY_ID
        self.secret=config.LINE_PAY_SECRET
        self.currency=currency

    def _headers(self, **kwargs):
        return {**{'Content-Type':'application/json',
                            'X-LINE-ChannelId':self.channel_id,
                            'X-LINE-ChannelSecret':self.secret},
                            **kwargs}

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

        response = linepay_api.request(request_options) # return a dict, where the key ['info'] also holds a dict
        return self._pay_check_response(response)

    def confirm(self, tx_id, amount):
        response = linepay_api.confirm(
            tx_id,
            amount,
            self.currency
        )
        return self._confirm_check_response(response)

    def _pay_check_response(self, response):
        transaction_id = int(response.get("info", {}).get("transactionId", 0))
        check_result = linepay_api.check_payment_status(transaction_id)
        config.logger.debug(check_result)
        config.logger.debug(response.get("info"))
        if check_result.get("returnCode") == '0000':
            return response.get("info")
        else:
            raise Exception(f'{check_result.get("returnCode")}:{ check_result.get("returnMessage")}')

    def _confirm_check_response(self, response):
        transaction_id = int(response.get("info", {}).get("transactionId", 0))
        check_result = linepay_api.check_payment_status(transaction_id)
        config.logger.debug(check_result)
        config.logger.debug(response.get("info"))
        if check_result.get("returnCode") == '0123':
            return response.get("info")
        else:
            raise Exception(f'{check_result.get("returnCode")}:{ check_result.get("returnMessage")}')