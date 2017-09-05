"""
Python Qiwi API Wrapper 1.1
by mostm

See Qiwi API Documentation: https://developer.qiwi.com/ru/qiwicom/index.html
"""
import datetime

import requests

import config

endpoint = 'https://edge.qiwi.com'
wallet = config.Wallet
default_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {wallet['token']}"
}
dt_format = "{}-{}-{}T{}:{}:{}Z"


class Person:
    """
    Пользователь (Ура! Хоть где-то)
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

    def __init__(self, number, contract_info=True, auth_info=True, user_info=True, token=wallet['token']):
        self.number = number
        self.token = token
        self.profile_parsed = False
        self.auth_info_enabled = auth_info
        self.contract_info_enabled = contract_info
        self.user_info_enabled = user_info

    def __repr__(self):
        return '<Person(number={})>'.format(self.number)

    @staticmethod
    def balance():
        """
        Баланс Visa QIWI Wallet
        :return:
        """
        url = f"{endpoint}/funding-sources/v1/accounts/current"
        request = requests.get(url=url, headers=default_headers)
        return request.json()

    def profile(self):
        """
        Профиль пользователя
        :return:
        """
        self.profile_parsed = True
        url = f"{endpoint}/person-profile/v1/profile/current"
        params = {'authInfoEnabled': str(self.auth_info_enabled).lower(),
                  'contractInfoEnabled': str(self.contract_info_enabled).lower(),
                  'userInfoEnabled': str(self.user_info_enabled).lower()
                  }
        request = requests.get(url=url, headers=default_headers, params=params)
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
        :param start_date: Начальная дата поиска платежей (str в формате dt_format) [Default: Today start]
        :param end_date: Конечная дата поиска платежей (str в формате dt_format) [Default: Today end]
        :param sources: Источники платежа, для отбора (QW_RUB, QW_USD, QW_EUR, CARD, MK) [Default: All specified]
        :return:
        """
        url = "{}/payment-history/v1/persons/{}/payments".format(endpoint, self.number)
        params = {'rows': rows,
                  'operation': operation
                  }
        if sources is not None:
            for source in sources:
                string = 'sources[{}]'.format(sources.index(source))
                params[string] = source
        if start_date is None and end_date is None:
            now = datetime.datetime.now()
            month = str(now.month).zfill(2)
            day = str(now.day).zfill(2)
            start_date = dt_format.format(now.year, month, day, '00', '00', '00')
            end_date = dt_format.format(now.year, month, day, '23', '59', '59')
            params['startDate'] = start_date
            params['endDate'] = end_date
        else:
            if isinstance(start_date, str) and isinstance(end_date, str):
                if start_date[4] == '-' and start_date[7] == '-' and start_date[10] == 'T' and start_date[23] == 'Z':
                    params['startDate'] = start_date
                else:
                    raise ValueError('Unknown format of start_date')
                if end_date[4] == '-' and end_date[7] == '-' and end_date[10] == 'T' and end_date[23] == 'Z':
                    params['endDate'] = end_date
                else:
                    raise ValueError('Unknown format of end_date')
            else:
                raise TypeError('Unknown type of start_date and end_date!')
        request = requests.get(url=url, headers=default_headers, params=params)
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
        url = f"{endpoint}/payment-history/v1/persons/{self.number}/payments/total"
        params = {'operation': operation}
        if sources is not None:
            for source in sources:
                current_source = "sources[{}]".format(sources.index(source))
                params[current_source] = source
        if isinstance(start_date, str) and isinstance(end_date, str):
            if start_date[4] == '-' and start_date[7] == '-' and start_date[10] == 'T' and start_date[19] == 'Z':
                params['startDate'] = start_date
            else:
                raise ValueError('Unknown format of start_date')
            if end_date[4] == '-' and end_date[7] == '-' and end_date[10] == 'T' and end_date[19] == 'Z':
                params['endDate'] = end_date
            else:
                raise ValueError('Unknown format of end_date')
        else:
            raise TypeError('Unknown type of start_date and end_date')
        request = requests.get(url=url, headers=default_headers, params=params)
        return request.json()


class Payment:
    """
    Платежи

    :param pid: ID провайдера
    :type pid: int
    :param recipient: Получатель платежа
    :type recipient: str
    :param amount: Сумма платежа
    :type amount: float
    """

    def __init__(self, pid, recipient, amount):
        self.id = pid
        self.recipient = recipient
        self.amount = amount

    def __repr__(self):
        return '<Payment(id={}, ' \
               'recipient={}, ' \
               'amount={})>' \
               ''.format(self.id, self.recipient, self.amount)

    def commission(self):
        """
        Расчет комиссии для платежа
        :return:
        """
        url = "{}/sinap/providers/{}/onlineCommission".format(endpoint, self.id)
        body = {'account': self.recipient,
                'paymentMethod':
                    {'type': 'Account',
                     'accountId': '643'},
                'purchaseTotals':
                    {'total': {'amount': self.amount,
                               'currency': '643'}}
                }
        request = requests.post(url=url, headers=default_headers, json=body)
        return request.json()

    def send(self, fields=None, comment=None):
        """
        Отправить платеж
        :param fields: Ручное добавление dict'а в платежи.
                       Требуется для специфичных платежей
                       Например, перевод на счет в банке
        :type fields: dict
        :param comment: Комментарий к платежу
        :type comment: str
        :return:
        """
        url = "{}/sinap/api/v2/terms/{}/payments".format(endpoint, id)
        if fields is None:
            fields = {'account': str(self.recipient)}
        body = {'id': str(int(1000 * datetime.datetime.utcnow().timestamp())),
                'sum': {'amount': self.amount,
                        'currency': '643'},
                'paymentMethod': {'type': 'Account',
                                  'accountId': '643'},
                'fields': fields,
                'comment': 'Отправлено с помощью Visa QIWI Wallet API'
                }
        if comment is not None:
            body['comment'] = comment
        request = requests.post(url=url, headers=default_headers, json=body)
        return request.json()


def commission(pid):
    """
    Получение стандартной комиссии
    :param pid: ID провайдера.
    :return:
    """
    url = f"{endpoint}/sinap/providers/{pid}/form"
    request = requests.get(url=url, headers=default_headers)
    return request.json()
