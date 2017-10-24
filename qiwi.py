"""
Python Qiwi API Wrapper 1.2
by mostm

See Qiwi API Documentation: https://developer.qiwi.com/ru/qiwicom/index.html
"""

import datetime
from functools import partial
import requests


class Wallet:
    """
    Visa QIWI Кошелек пользователя

    :param number: Номер пользователя
    :type number: str
    :param token: Токен пользователя
    :type token: str
    :param user_info: Логический признак выгрузки настроек авторизации пользователя [Default: True]
    :type user_info: bool
    :param contract_info: Логический признак выгрузки данных о кошельке пользователя [Default: True]
    :type contract_info: bool
    :param auth_info: Логический признак выгрузки прочих пользовательских данных [Default: True]
    :type auth_info: bool
    """

    def __init__(self, number, token, contract_info=True, auth_info=True, user_info=True):
        self.number = number
        self.token = token
        self.profile_parsed = False
        self.auth_info_enabled = auth_info
        self.contract_info_enabled = contract_info
        self.user_info_enabled = user_info
        self.get_commission = partial(get_commission, self.token)
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': "Bearer {0}".format(self.token)}

    def __repr__(self):
        return '<Wallet(number={0}, token={1})>'.format(self.number, self.token)

    def balance(self):
        """
        Баланс Visa QIWI Wallet
        :return:
        """
        request = requests.get(url="https://edge.qiwi.com/funding-sources/v1/accounts/current", headers=self.headers)
        return request.json()

    def profile(self):
        """
        Профиль пользователя
        :return:
        """
        self.profile_parsed = True
        params = {'authInfoEnabled': str(self.auth_info_enabled).lower(),
                  'contractInfoEnabled': str(self.contract_info_enabled).lower(),
                  'userInfoEnabled': str(self.user_info_enabled).lower()
                  }
        request = requests.get(url="https://edge.qiwi.com/person-profile/v1/profile/current",
                               headers=self.headers, params=params)
        request = request.json()
        return request

    def history(self, rows=20, operation='ALL', start_date=None, end_date=None, sources=None):
        """
        История платежей
        [Максимальная интенсивность запросов истории платежей - не более 100 запросов в минуту с одного IP-адреса.
         При превышении доступ к API блокируется на 5 минут.]
        :param rows: Число платежей в ответе, для разбивки отчета на части. (1-50) [Default: 20]
        :type rows: int
        :param operation: Тип операций в отчете, для отбора (ALL, IN, OUT, QIWI_CARD) [Default: ALL]
        :type operation: str
        Максимальный допустимый интервал между startDate и endDate - 90 календарных дней.
        :param start_date: Начальная дата поиска платежей
        :type start_date: datetime.datetime
        :param end_date: Конечная дата поиска платежей
        :type end_date: datetime.datetime
        :param sources: Источники платежа, для отбора (QW_RUB, QW_USD, QW_EUR, CARD, MK) [Default: All specified]
        :return:
        """
        url = "https://edge.qiwi.com/payment-history/v1/persons/{0}/payments".format(self.number)
        params = {'rows': rows,
                  'operation': operation}
        if sources is not None:
            for source in sources:
                params['sources[{0}]'.format(sources.index(source))] = source
        if start_date is not None and end_date is not None:
            if isinstance(start_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
                params['startDate'] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                params['endDate'] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                raise TypeError('You should use datetime.datetime Type for start_date and end_date')
        request = requests.get(url=url, headers=self.headers, params=params)
        return request.json()

    def stat(self, start_date, end_date, operation='ALL', sources=None):
        """
        Статистика платежей
        :param start_date: Начальная дата периода статистики
        :type start_date: str
        :param end_date: Конечная дата периода статистики
        :type end_date: str
        :param operation: Тип операций, учитываемых при подсчете статистики
                          (ALL, IN, OUT, QIWI_CARD) [Default: ALL]
        :type operation: str
        :param sources: Источники платежа, учитываемые при подсчете статистики
                        (QW_RUB, QW_USD, QW_EUR, CARD, MK) [Default: All-specified]
        :type sources: list
        :return:
        """
        url = "https://edge.qiwi.com/payment-history/v1/persons/{self.number}/payments/total"
        params = {'operation': operation}
        if sources is not None:
            for source in sources:
                params['sources[{0}]'.format(sources.index(source))] = source
        if start_date is not None and end_date is not None:
            if isinstance(start_date, datetime.datetime) and isinstance(end_date, datetime.datetime):
                params['startDate'] = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                params['endDate'] = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                raise TypeError('You should use datetime.datetime Type for start_date and end_date')
        request = requests.get(url=url, headers=self.headers, params=params)
        return request.json()

    def commission(self, pid=None, recipient=None, amount=None):
        """
        Расчет комиссии для платежа
        :param pid: ID провайдера
        :param recipient: Получатель платежа
        :param amount: Сумма платежа
        :return:
        """
        url = "https://edge.qiwi.com/sinap/providers/{0}/onlineCommission".format(pid)
        body = {'account': recipient,
                'paymentMethod':
                    {'type': 'Account',
                     'accountId': '643'},
                'purchaseTotals':
                    {'total': {'amount': amount,
                               'currency': '643'}}
                }
        request = requests.post(url=url, headers=self.headers, json=body)
        return request.json()

    def send(self, fields=None, comment=None, pid=None, recipient=None, amount=None):
        """
        Отправить платеж
        :param fields: Ручное добавление dict'а в платежи.
                       Требуется для специфичных платежей
                       Например, перевод на счет в банке
        :type fields: dict
        :param comment: Комментарий к платежу
        :type comment: str
        :param pid: ID провайдера
        :param recipient: Получатель платежа
        :param amount: Сумма платежа
        :return:
        """
        url = "https://edge.qiwi.com/sinap/api/v2/terms/{0}/payments".format(pid)
        if fields is None:
            fields = {'account': str(recipient)}
        body = {'id': str(int(1000 * datetime.datetime.utcnow().timestamp())),
                'sum': {'amount': float(amount),
                        'currency': '643'},
                'paymentMethod': {'type': 'Account',
                                  'accountId': '643'},
                'fields': fields,
                'comment': 'Отправлено с помощью pyQiwi'
                }
        if comment is not None:
            body['comment'] = comment
        request = requests.post(url=url, headers=self.headers, json=body)
        return request.json()


def get_commission(token, pid):
    """
    Получение стандартной комиссии
    :param token: Токен пользователя
    :param pid: ID провайдера.
    :return:
    """
    url = "https://edge.qiwi.com/sinap/providers/{0}/form".format(pid)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': "Bearer {0}".format(token)
    }
    request = requests.get(url=url, headers=headers)
    return request.json()
