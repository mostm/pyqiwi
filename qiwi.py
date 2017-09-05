"""
Python Qiwi API Wrapper 1.0
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
dt_format = "{}-{}-{}T{}%3A{}%3A{}Z"


# {year}-{month}-{day}T{hour}%3A{minute}%3A{second}Z
# Like this: 2017-01-01T00%3A00%3A00Z

def person_profile(authInfoEnabled=True, contractInfoEnabled=True, userInfoEnabled=True):
    """
    Профиль пользователя
    :param authInfoEnabled: Логический признак выгрузки настроек авторизации пользователя [Default: True]
    :param contractInfoEnabled: Логический признак выгрузки данных о кошельке пользователя [Default: True]
    :param userInfoEnabled: Логический признак выгрузки прочих пользовательских данных [Default: True]
    :return:
    """
    url = f"{endpoint}/person-profile/v1/profile/current" \
          f"?authInfoEnabled={str(authInfoEnabled).lower()}" \
          f"&contractInfoEnabled={str(contractInfoEnabled).lower()}" \
          f"&userInfoEnabled={str(userInfoEnabled).lower()}"
    request = requests.get(url=url, headers=default_headers)
    return request.json()


class payment_history:
    """История платежей пользователя из токена (требуется number в config'е)"""

    def payments(rows=20, operation='ALL', startDate=None, endDate=None, sources=None):
        """
        История платежей
        [Максимальная интенсивность запросов истории платежей - не более 100 запросов в минуту с одного IP-адреса.
         При превышении доступ к API блокируется на 5 минут.]
        :param rows: Число платежей в ответе, для разбивки отчета на части. Целое число от 1 до 50 [Default: 20]
        :param operation: Тип операций в отчете, для отбора (ALL, IN, OUT, QIWI_CARD) [Default: ALL]
        Максимальный допустимый интервал между startDate и endDate - 90 календарных дней.
        :param startDate: Начальная дата поиска платежей (str в формате dt_format) [Default: Today start]
        :param endDate: Конечная дата поиска платежей (str в формате dt_format) [Default: Today end]
        :param sources: Источники платежа, для отбора (QW_RUB, QW_USD, QW_EUR, CARD, MK) [Default: All specified]
        :return:
        """
        url = f"{endpoint}/payment-history/v1/persons/{wallet['number']}/payments?rows={rows}&operation={operation}"
        if sources is None:
            print()
        else:
            for source in sources:
                url += f'&sources[{sources.index(source)}]={source}'
        if startDate is None and endDate is None:
            now = datetime.datetime.now()
            month = now.month
            day = now.day
            if len(str(month)) == 1:
                month = f'0{month}'
            if len(str(day)) == 1:
                day = f'0{day}'
            startDate = dt_format.format(now.year, month, day, '00', '00', '00')
            endDate = dt_format.format(now.year, month, day, '23', '59', '59')
            url += f"&startDate={startDate}&endDate={endDate}"
        else:
            if type(startDate) == type('') and type(endDate) == type(''):
                if startDate[4] == '-' and startDate[7] == '-' and startDate[10] == 'T' and startDate[23] == 'Z':
                    print('startDate verified!')
                else:
                    raise Exception('startDate unknown format!')
                if endDate[4] == '-' and endDate[7] == '-' and endDate[10] == 'T' and endDate[23] == 'Z':
                    print('endDate verified!')
                else:
                    raise Exception('endDate unknown format!')
                url += f"&startDate={startDate}&endDate={endDate}"
            else:
                raise Exception('Unknown type of startDate and endDate!')
        request = requests.get(url=url, headers=default_headers)
        return request.json()

    def total(startdate, enddate, operation='ALL', sources=None):
        """
        Статистика платежей
        :param startdate: Начальная дата периода статистики [Required]
        :param enddate: Конечная дата периода статистики [Required | Type: str in dt_format]
        :param operation: Тип операций, учитываемых при подсчете статистики. (ALL, IN, OUT, QIWI_CARD) [Default: ALL]
        :param sources: Источники платежа, учитываемые при подсчете статистики (QW_RUB, QW_USD, QW_EUR, CARD, MK) [Type: List | Default: All specified]
        :return:
        """
        url = f"{endpoint}/payment-history/v1/persons/{wallet['number']}/payments/total"
        param = {'operation': operation}
        if sources != None:
            for source in sources:
                param[f"sources[{sources.index(source)}]"] = source
        if type(startdate) == type('') and type(enddate) == type(''):
            if startdate[4] == '-' and startdate[7] == '-' and startdate[10] == 'T' and startdate[19] == 'Z':
                param['startDate'] = startdate
            else:
                raise Exception('startdate unknown format!')
            if enddate[4] == '-' and enddate[7] == '-' and enddate[10] == 'T' and enddate[19] == 'Z':
                param['endDate'] = enddate
            else:
                raise Exception('enddate unknown format!')
        else:
            raise Exception('Unknown type of startDate and endDate!')
        request = requests.get(url=url, headers=default_headers, params=param)
        return request.json()


def funding_sources():
    """
    Баланс QIWI Кошелька
    :return:
    """
    url = f"{endpoint}/funding-sources/v1/accounts/current"
    request = requests.get(url=url, headers=default_headers)
    return request.json()


def commission(id):
    """
    Стандартные тарифы
    :param id: ID провайдера.
    :return:
    """
    url = f"{endpoint}/sinap/providers/{id}/form"
    request = requests.get(url=url, headers=default_headers)
    return request.json()


class Payment():
    """
    Платежи

    :param provider_id: ID провайдера
    :param recipient: Получатель платежа
    :param amount: Сумма платежа
    :type id: int
    :type recipient: str
    :type amount: float
    """

    def __init__(self, id, recipient, amount):
        self.id = id
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
        :param comment: Комментарий к платежу
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
