# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from sys import stderr

import requests

# noinspection PyCompatibility
from . import exceptions, util

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"'
)
console_output_handler = logging.StreamHandler(stderr)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)
logger.setLevel(logging.ERROR)
ad = False
session = requests.session()
API_URL = 'https://edge.qiwi.com/{0}'

CONNECT_TIMEOUT = 3.5
READ_TIMEOUT = 9999


def _make_request(token, method_name, method='get', params=None, base_url=API_URL, json=None, passthru=False, proxy=None):
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': "Bearer {0}".format(token)}
    request_url = base_url.format(method_name)
    logger.debug("Request: method={0} url={1} params={2}".format(method, request_url, params))
    read_timeout = READ_TIMEOUT
    connect_timeout = CONNECT_TIMEOUT
    if params:
        if 'timeout' in params:
            read_timeout = params['timeout'] + 10
        if 'connect-timeout' in params:
            connect_timeout = params['connect-timeout'] + 10
    result = session.request(method, request_url, params=params, timeout=(connect_timeout, read_timeout),
                             proxies=proxy, headers=headers, json=json)
    logger.debug("The server returned: '{0}'".format(result.text.encode('utf8')))
    if method_name.split('/')[0] == 'sinap':
        method_name = method_name.split('/')[len(method_name.split('/')) - 1]
    else:
        method_name = method_name.split('/')[0]
    return _check_result(method_name, result, passthru)


def _check_result(method_name, result, passthru):
    if result.text == '':
        description = exceptions.find_exception_desc(result.status_code, method_name)
        msg = 'Error code: {0} Description: {1}'.format(result.status_code, description)
        raise exceptions.APIError(msg, method_name, response=result)
    if result.status_code != 200 and result.status_code != 201:
        msg = 'The server returned HTTP {0} {1}. Response body:\n[{2}]' \
            .format(result.status_code, result.reason, result.text.encode('utf8'))
        raise exceptions.APIError(msg, method_name, response=result)
    try:
        if passthru:
            return result
        else:
            result_json = result.json()
    except Exception:
        if result.status_code == 201:
            return True
        else:
            msg = 'The server returned an invalid JSON response. Response body:\n[{0}]' \
                .format(result.text.encode('utf8'))
            raise exceptions.APIError(msg, method_name, response=result)
    return result_json


def person_profile(token, auth_info_enabled, contract_info_enabled, user_info_enabled, proxy=None):
    params = {'authInfoEnabled': str(auth_info_enabled).lower(),
              'contractInfoEnabled': str(contract_info_enabled).lower(),
              'userInfoEnabled': str(user_info_enabled).lower()
              }
    api_method = 'person-profile/v1/profile/current'
    return _make_request(token, api_method, params=params, proxy=proxy)


def funding_sources(token, proxy=None):
    api_method = 'funding-sources/v1/accounts/current'
    return _make_request(token, api_method, proxy=proxy)


def get_by_alias(token, person_id, proxy=None):
    # V2 alternative to funding_sources
    api_method = 'funding-sources/v2/persons/{0}/accounts'.format(person_id)
    return _make_request(token, api_method, proxy=proxy)


def get_accounts_offer(token, person_id, proxy=None):
    api_method = 'funding-sources/v2/persons/{0}/accounts/offer'.format(person_id)
    return _make_request(token, api_method, proxy=proxy)


def create_account(token, person_id, dto, proxy=None):
    api_method = '/funding-sources/v2/persons/{0}/accounts'.format(person_id)
    body = {
        "accountAlias": dto
    }
    return _make_request(token, api_method, method='post', json=body, proxy=proxy)


def payment_history(token, number, rows, operation=None, start_date=None, end_date=None, sources=None,
                    next_txn_date=None, next_txn_id=None, proxy=None):
    api_method = "payment-history/v2/persons/{0}/payments".format(number)
    params = {'rows': rows}
    if operation:
        params['operation'] = operation
    if sources:
        params = util.sources_list(sources, params)
    if start_date and end_date:
        params = util.stat_dates(start_date, end_date, params)
    if next_txn_id and next_txn_date:
        params['nextTxnId'] = next_txn_id
        params['nextTxnDate'] = util.qiwi_date(next_txn_date)
    return _make_request(token, api_method, params=params, proxy=proxy)


def total_payment_history(token, number, start_date, end_date, operation=None, sources=None, proxy=None):
    api_method = "payment-history/v2/persons/{0}/payments/total".format(number)
    params = {}
    if operation:
        params['operation'] = operation
    if sources:
        params = util.sources_list(sources, params)
    params = util.stat_dates(start_date, end_date, params)
    return _make_request(token, api_method, params=params, proxy=proxy)


def online_commission(token, recipient, pid, amount, proxy=None):
    api_method = "sinap/providers/{0}/onlineCommission".format(pid)
    body = {'account': recipient,
            'paymentMethod':
                {'type': 'Account',
                 'accountId': '643'},
            'purchaseTotals':
                {'total': {'amount': amount,
                           'currency': '643'}}
            }
    return _make_request(token, api_method, method='post', json=body, proxy=proxy)


def payments(token, pid, amount, recipient, comment=None, fields=None, proxy=None):
    api_method = "sinap/api/v2/terms/{0}/payments".format(pid)
    if fields:
        pass
    else:
        fields = {'account': str(recipient)}
    body = {'id': str(int(1000 * datetime.utcnow().timestamp())),
            'sum': {'amount': float(amount),
                    'currency': '643'},
            'paymentMethod': {'type': 'Account',
                              'accountId': '643'},
            'fields': fields}
    if comment:
        body['comment'] = comment
    elif ad:
        body['comment'] = 'Отправлено с помощью pyQiwi'
    return _make_request(token, api_method, method='post', json=body, proxy=proxy)


def local_commission(token, pid, proxy=None):
    api_method = "sinap/providers/{0}/form".format(pid)
    return _make_request(token, api_method, proxy=proxy)


def get_transaction(token, txn_id, txn_type, proxy=None):
    api_method = 'payment-history/v2/transactions/{0}?type={1}'.format(txn_id, txn_type)
    return _make_request(token, api_method, proxy=proxy)


def identification(token, wallet, birth_date, first_name, middle_name, last_name, passport, inn, snils, oms, proxy=None):
    api_method = 'identification/v1/persons/{0}/identification'.format(wallet)
    if inn is None:
        inn = ""
    if snils is None:
        snils = ""
    if oms is None:
        oms = ""
    identity = {
        "birthDate": birth_date,
        "firstName": first_name,
        "middleName": middle_name,
        "lastName": last_name,
        "passport": passport,
        "inn": inn,
        "snils": snils,
        "oms": oms
    }
    return _make_request(token, api_method, method='post', json=identity, proxy=proxy)


def detect(phone, proxy=None):
    result_json = requests.post('https://qiwi.com/mobile/detect.action', data={"phone": phone}, proxies=proxy)
    result_json = result_json.json()
    if result_json.get('code', {}).get('value') == '0':
        return result_json.get('message')
    else:
        return None


def cheque_file(token, txn_id, _type, _format, proxy=None):
    api_method = 'payment-history/v1/transactions/{0}/cheque/file'.format(txn_id)
    return _make_request(token, api_method, params={"type": _type, "format": _format}, passthru=True, proxy=proxy)


def cheque_send(token, txn_id, _type, email, proxy=None):
    api_method = 'payment-history/v1/transactions/{0}/cheque/send'.format(txn_id)
    return _make_request(token, api_method, method='post', params={"type": _type}, json={"email": email}, proxy=proxy)


def cross_rates(token, proxy=None):
    api_method = 'sinap/crossRates'
    return _make_request(token, api_method, proxy=proxy)
