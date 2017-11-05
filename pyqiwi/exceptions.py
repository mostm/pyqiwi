# -*- coding: utf-8 -*-
from .util import url_params

APICodes = {'400': [{'method_name': None, 'msg': 'Invalid request syntax (invalid format of data)'}],
            '401': [{'method_name': None, 'msg': 'Invalid or expired token'}],
            '404': [{'method_name': 'payment-history',
                     'msg': 'Transaction not found or no payments with specified params'},
                    {'method_name': ['funding-sources', 'person-profile', 'identification'],
                     'msg': 'Wallet not found'}],
            '423': [{'method_name': 'payment-history', 'msg': 'Too many requests, service is temporarily unavailable'}]}


class APIError(Exception):
    """
    Ошибка в Qiwi API

    Attributes
    ----------
    msg : str
        Сообщение ошибки
    method_name : str
        Название метода, вызванного при возникновении ошибки
    request : requests.Response
        Чистый ответ от сервера, полученный от requests
    response : str
        Текст выданный Qiwi API, без какой либо обработки
    method : str
        Метод вызванный на сервере Qiwi
    params : dict
        Параметры вызванного метода
    """

    def __init__(self, msg, method_name, response=None):
        self.msg = msg
        self.method_name = method_name
        self.response = response.text
        self.request = response
        self.method = response.request.path_url
        self.params = url_params(response.request.url)


def find_exception_desc(status_code, method_name):
    basic_msg = None
    msg = None
    if str(status_code) in APICodes:
        for exc in APICodes[str(status_code)]:
            if isinstance(exc['method_name'], type(None)):
                basic_msg = exc['msg']
            elif isinstance(exc['method_name'], str) and exc['method_name'] == method_name:
                msg = exc['msg']
            elif isinstance(exc['method_name'], list):
                if method_name in exc['method_name']:
                    msg = exc['msg']
            else:
                continue
        if isinstance(basic_msg, type(None)) and not isinstance(msg, type(None)):
            return msg
        elif not isinstance(basic_msg, type(None)) and isinstance(msg, type(None)):
            return basic_msg
    return 'Unknown exception {0} in {1}'.format(status_code, method_name)
