"""
Python Qiwi API Wrapper 2.0
by mostm

See Qiwi API Documentation: https://developer.qiwi.com/ru/qiwicom/index.html
"""

import datetime
import logging
import sys
from functools import partial

logger = logging.getLogger('pyqiwi')
formatter = logging.Formatter(
    '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"'
)

console_output_handler = logging.StreamHandler(sys.stderr)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

logger.setLevel(logging.ERROR)
ad = True

from . import exceptions, types, apihelper


class Wallet:
    """
    Visa QIWI Кошелек пользователя

    :param token: Токен пользователя
    :type token: str
    :param number: Номер пользователя (если не указан, статистика и история работать не будет)
    :type number: str
    :param user_info: Логический признак выгрузки настроек авторизации пользователя [Default: True]
    :type user_info: bool
    :param contract_info: Логический признак выгрузки данных о кошельке пользователя [Default: True]
    :type contract_info: bool
    :param auth_info: Логический признак выгрузки прочих пользовательских данных [Default: True]
    :type auth_info: bool
    """

    def __init__(self, token, number=None, contract_info=True, auth_info=True, user_info=True):
        self.number = number
        self.token = token
        self.auth_info_enabled = auth_info
        self.contract_info_enabled = contract_info
        self.user_info_enabled = user_info
        self.get_commission = partial(get_commission, self.token)
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': "Bearer {0}".format(self.token)}

    def __str__(self):
        return '<Wallet(number={0}, token={1})>'.format(self.number, self.token)

    @property
    def accounts(self):
        """
        Все доступные методы оплаты для кошелька
        (но в API все-равно доступен только рублевый Qiwi Wallet)

        :return: list(types.Account)
        """
        result_json = apihelper.funding_sources(self.token)
        accounts = []
        for account in result_json['accounts']:
            accounts.append(types.Account.de_json(account))
        return accounts

    def balance(self, currency):
        """
        Баланс Visa QIWI Wallet

        :param currency: ID валюты
        :return: int
        """
        for account in self.accounts:
            if account.currency == currency:
                return account.balance.get('amount')

    @property
    def profile(self):
        """
        Профиль пользователя

        :return: types.Profile
        """
        result_json = apihelper.person_profile(self.token, self.auth_info_enabled,
                                               self.contract_info_enabled, self.user_info_enabled)
        return types.Profile.de_json(result_json)

    def history(self, rows=20, operation=None, start_date=None, end_date=None, sources=None):
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
        :return: list(types.Transaction)
        """
        result_json = apihelper.payment_history(self.token, self.number, rows, operation=operation,
                                                start_date=start_date, end_date=end_date, sources=sources)
        transactions = []
        for transaction in result_json['data']:
            transactions.append(types.Transaction.de_json(transaction))
        return transactions

    def stat(self, start_date=None, end_date=None, operation=None, sources=None):
        """
        Статистика платежей
        Изначально берется статистика с начала месяца

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
        :return: types.Statistics
        """
        if start_date:
            pass
        else:
            start_date = datetime.datetime.utcnow()
            start_date = start_date.replace(day=1, hour=0, minute=0, second=1)
        if end_date:
            pass
        else:
            end_date = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        result_json = apihelper.total_payment_history(self.token, self.number, start_date, end_date,
                                                      operation=operation, sources=sources)
        return types.Statistics.de_json(result_json)

    def commission(self, pid, recipient, amount):
        """
        Расчет комиссии для платежа
        :param pid: ID провайдера
        :param recipient: Получатель платежа
        :param amount: Сумма платежа
        :return: types.OnlineCommission
        """
        result_json = apihelper.online_commission(self.token, recipient, pid, amount)
        return types.OnlineCommission.de_json(result_json)

    def send(self, pid, recipient, amount, comment=None, fields=None):
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
        :return: types.Payment
        """
        result_json = apihelper.payments(self.token, pid, amount, recipient, comment=comment, fields=fields)
        return types.Payment.de_json(result_json)


def get_commission(token, pid):
    """
    Получение стандартной комиссии
    :param token: Токен пользователя
    :param pid: ID провайдера.
    :return: types.Commission
    """
    result_json = apihelper.local_commission(token, pid)
    return types.Commission.de_json(result_json)
