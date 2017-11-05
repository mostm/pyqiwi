# -*- coding: utf-8 -*-
"""
Python Qiwi API Wrapper 2.0
by mostm

See pyQiwi Documentation: pyqiwi.readthedocs.io
"""
import datetime
from functools import partial

from . import types, apihelper

__title__ = 'pyQiwi'
__version__ = "2.0.5"
__author__ = "mostm"
__license__ = 'MIT'
__copyright__ = 'Copyright 2017 {0}'.format(__author__)
version_info = tuple(map(int, __version__.split('.')))


class Wallet:
    """
    Visa QIWI Кошелек

    Parameters
    ----------
    token : str
        `Ключ Qiwi API`_ пользователя
    number : Optional[str]
        Номер для указанного кошелька
        По умолчанию - ``None``
        Если не указан, статистика и история работать не будет
    contract_info : Optional[bool]
        Логический признак выгрузки данных о кошельке пользователя
        По умолчанию - ``True``
    auth_info : Optional[bool]
        Логический признак выгрузки настроек авторизации пользователя
        По умолчанию - ``True``
    user_info : Optional[bool]
        Логический признак выгрузки прочих пользовательских данных
        По умолчанию - ``True``

    Attributes
    -----------
    accounts : iterable of :class:`Account <pyqiwi.types.Account>`
        Все доступные методы оплаты для кошелька
    profile : :class:`Profile <pyqiwi.types.Profile>`
        Профиль пользователя
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
        result_json = apihelper.funding_sources(self.token)
        accounts = []
        for account in result_json['accounts']:
            accounts.append(types.Account.de_json(account))
        return accounts

    def balance(self, currency):
        """
        Баланс Visa QIWI Кошелька

        Parameters
        ----------
        currency : int
            ID валюты в ``number-3 ISO-4217``
            Например, ``643`` для российского рубля

        Returns
        -------
        float
            Баланс кошелька
        """
        for account in self.accounts:
            if account.currency == currency:
                return account.balance.get('amount')

    @property
    def profile(self):
        result_json = apihelper.person_profile(self.token, self.auth_info_enabled,
                                               self.contract_info_enabled, self.user_info_enabled)
        return types.Profile.de_json(result_json)

    def history(self, rows=20, operation=None, start_date=None, end_date=None, sources=None):
        """
        История платежей

        Warning
        -------
        Максимальная интенсивность запросов истории платежей - не более 100 запросов в минуту с одного IP-адреса.
        При превышении доступ к API блокируется на 5 минут.

        Parameters
        ----------
        rows : Optional[int]
            Число платежей в ответе, для разбивки отчета на части.
            От 1 до 50, по умолчанию 20.
        operation : Optional[str]
            Тип операций в отчете, для отбора\n
            Варианты: ALL, IN, OUT, QIWI_CARD\n
            По умолчанию - ALL
        start_date : Optional[datetime.datetime]
            Начальная дата поиска платежей
        end_date : Optional[datetime.datetime]
            Конечная дата поиска платежей
        sources : Optional[list]
            Источники платежа, для отбора\n
            Варианты: QW_RUB, QW_USD, QW_EUR, CARD, MK\n
            По умолчанию - все указанные

        Note
        ----
        Если вы хотите использовать startDate или endDate, вы должны указать оба параметра
        Максимальный допустимый интервал между startDate и endDate - 90 календарных дней.

        Returns
        -------
        list[:class:`Transaction <pyqiwi.types.Transaction>`]
            Транзакции
        """
        result_json = apihelper.payment_history(self.token, self.number, rows, operation=operation,
                                                start_date=start_date, end_date=end_date, sources=sources)
        transactions = []
        for transaction in result_json['data']:
            transactions.append(types.Transaction.de_json(transaction))
        return transactions

    def transaction(self, txn_id, txn_type):
        """
        Получение транзакции из Qiwi API

        Parameters
        ----------
        txn_id : str
            ID транзакции
        txn_type : str
            Тип транзакции (IN/OUT)

        Returns
        -------
        :class:`Transaction <pyqiwi.types.Transaction>`
            Транзакция
        """
        result_json = apihelper.get_transaction(self.token, txn_id, txn_type)
        return types.Transaction.de_json(result_json)

    def stat(self, start_date=None, end_date=None, operation=None, sources=None):
        """
        Статистика платежей

        Note
        ----
        Изначально берется статистика с начала месяца

        Parameters
        ----------
        operation : Optional[str]
            Тип операций в отчете, для отбора
            Варианты: ALL, IN, OUT, QIWI_CARD
            По умолчанию - ALL
        
        start_date : Optional[datetime.datetime]
            Начальная дата поиска платежей

        end_date : Optional[datetime.datetime]
            Конечная дата поиска платежей

        sources : Optional[list]
            Источники платежа, для отбора
            Варианты: QW_RUB, QW_USD, QW_EUR, CARD, MK
            По умолчанию - все указанные

        Returns
        -------
        :class:`Statistics <pyqiwi.types.Statistics>`
            Статистика
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

        Parameters
        ----------
        pid : str
            Идентификатор провайдера
        
        recipient : str
            Номер телефона (с международным префиксом) или номер карты/счета получателя
            В зависимости от провайдера

        amount : float/int
            Сумма платежа
            Положительное число, округленное до 2 знаков после десятичной точки.
            При большем числе знаков значение будет округлено до копеек в меньшую сторону.

        Returns
        -------
        :class:`OnlineCommission <pyqiwi.types.OnlineCommission>`
            Комиссия для платежа
        """
        result_json = apihelper.online_commission(self.token, recipient, pid, amount)
        return types.OnlineCommission.de_json(result_json)

    def send(self, pid, recipient, amount, comment=None, fields=None):
        """
        Отправить платеж

        Parameters
        ----------
        pid : str
            Идентификатор провайдера
        
        recipient : str
            Номер телефона (с международным префиксом) или номер карты/счета получателя
            В зависимости от провайдера

        amount : float/int
            Сумма платежа
            Положительное число, округленное до 2 знаков после десятичной точки.
            При большем числе знаков значение будет округлено до копеек в меньшую сторону.

        comment : Optional[str]
            Комментарий к платежу

        fields : dict
            Ручное добавление dict'а в платежи.
            Требуется для специфичных платежей
            Например, перевод на счет в банке
        
        Returns
        -------
        :class:`Payment <pyqiwi.types.Payment>`
            Платеж
        """
        result_json = apihelper.payments(self.token, pid, amount, recipient, comment=comment, fields=fields)
        return types.Payment.de_json(result_json)


def get_commission(token, pid):
    """
    Получение стандартной комиссии

    Parameters
    ----------
    token : str
        `Ключ Qiwi API`_

    pid : str
        Идентификатор провайдера
    
    Returns
    -------
    :class:`Commission <pyqiwi.types.Commission>`
        Комиссия для платежа
    """
    result_json = apihelper.local_commission(token, pid)
    return types.Commission.de_json(result_json)
