# -*- coding: utf-8 -*-
"""
Python Qiwi API Wrapper 2.1
by mostm

See pyQiwi Documentation: pyqiwi.readthedocs.io
"""
import datetime
from functools import partial

from requests.models import PreparedRequest

from . import apihelper, types


class Wallet:
    """
    Visa QIWI Кошелек

    Parameters
    ----------
    token : str
        `Ключ Qiwi API`_ пользователя.
    number : Optional[str]
        Номер для указанного кошелька.
        По умолчанию - ``None``.
        Если не указан, статистика и история работать не будет.
    contract_info : Optional[bool]
        Логический признак выгрузки данных о кошельке пользователя.
        По умолчанию - ``True``.
    auth_info : Optional[bool]
        Логический признак выгрузки настроек авторизации пользователя.
        По умолчанию - ``True``.
    user_info : Optional[bool]
        Логический признак выгрузки прочих пользовательских данных.
        По умолчанию - ``True``.

    Attributes
    -----------
    accounts : iterable of :class:`Account <pyqiwi.types.Account>`
        Все доступные счета на кошельке.
        Использовать можно только рублевый Visa QIWI Wallet.
    profile : :class:`Profile <pyqiwi.types.Profile>`
        Профиль пользователя.
    offered_accounts : iterable of :class:`Account <pyqiwi.types.Account>`
        Доступные счета для создания
    """

    def __init__(self, token, number=None, contract_info=True, auth_info=True, user_info=True):
        if isinstance(self.number, str):
            self.number = number.replace('+', '')
            if self.number.startswith('8'):
                self.number = '7' + self.number[1:]
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

    def balance(self, currency=643):
        """
        Баланс Visa QIWI Кошелька

        Parameters
        ----------
        currency : int
            ID валюты в ``number-3 ISO-4217``.
            Например, ``643`` для российского рубля.

        Returns
        -------
        float
            Баланс кошелька.

        Raises
        ------
        ValueError
            Во всех добавленных вариантах оплаты с указанного Qiwi-кошелька нет информации об балансе и его сумме.
            Скорее всего это временная ошибка Qiwi API, и вам стоит попробовать позже.
            Так же, эта ошибка может быть вызвана только-что зарегистрированным Qiwi-кошельком,
             либо довольно старым Qiwi-кошельком, которому необходимо изменение пароля.
        """
        for account in self.accounts:
            if account.currency == currency and account.balance and account.balance.get('amount'):
                return account.balance.get('amount')
        raise ValueError("There is no Payment Account that has balance and amount on it."
                         " Maybe this is temporary Qiwi API error, you should try again later."
                         " Also, this error can be caused by just registered Qiwi Account or "
                         "really old Qiwi Account that needs password change.")

    @property
    def profile(self):
        result_json = apihelper.person_profile(self.token, self.auth_info_enabled,
                                               self.contract_info_enabled, self.user_info_enabled)
        return types.Profile.de_json(result_json)

    def history(self, rows=20, operation=None, start_date=None, end_date=None, sources=None, next_txn_date=None,
                next_txn_id=None):
        """
        История платежей

        Warning
        -------
        Максимальная интенсивность запросов истории платежей - не более 100 запросов в минуту
         для одного и того же номера кошелька.
        При превышении доступ к API блокируется на 5 минут.

        Parameters
        ----------
        rows : Optional[int]
            Число платежей в ответе, для разбивки отчета на части.
            От 1 до 50, по умолчанию 20.
        operation : Optional[str]
            Тип операций в отчете, для отбора.
            Варианты: ALL, IN, OUT, QIWI_CARD.
            По умолчанию - ALL.
        start_date : Optional[datetime.datetime]
            Начальная дата поиска платежей.
        end_date : Optional[datetime.datetime]
            Конечная дата поиска платежей.
        sources : Optional[list]
            Источники платежа, для отбора.
            Варианты: QW_RUB, QW_USD, QW_EUR, CARD, MK.
            По умолчанию - все указанные.
        next_txn_date : Optional[datetime.datetime]
            Дата транзакции для отсчета от предыдущего списка (равна параметру nextTxnDate в предыдущем списке).
        next_txn_id : Optional[int]
            Номер предшествующей транзакции для отсчета от предыдущего списка
            (равен параметру nextTxnId в предыдущем списке).

        Note
        ----
        Если вы хотите использовать start_date или end_date, вы должны указать оба параметра.
        Такое же использование и у next_txn_date и next_txn_id.
        Максимальный допустимый интервал между start_date и end_date - 90 календарных дней.

        Returns
        -------
        dict
            Состоит из:
            transactions[list[:class:`Transaction <pyqiwi.types.Transaction>`]] - Транзакции.
            next_txn_date[datetime.datetime] - Дата транзакции(для использования в следующем использовании).
            next_txn_id[int] - Номер транзакции.
        """
        result_json = apihelper.payment_history(self.token, self.number, rows, operation=operation,
                                                start_date=start_date, end_date=end_date, sources=sources,
                                                next_txn_date=next_txn_date, next_txn_id=next_txn_id)
        transactions = []
        for transaction in result_json['data']:
            transactions.append(types.Transaction.de_json(transaction))
        ntd = None
        if result_json.get("nextTxnDate") is not None:
            ntd = types.JsonDeserializable.decode_date(result_json.get("nextTxnDate"))
        return {"transactions": transactions,
                "next_txn_date": ntd,
                "next_txn_id": result_json.get('nextTxnId')}

    def transaction(self, txn_id, txn_type):
        """
        Получение транзакции из Qiwi API

        Parameters
        ----------
        txn_id : str
            ID транзакции.
        txn_type : str
            Тип транзакции (IN/OUT/QIWI_CARD).

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
            Тип операций в отчете, для отбора.
            Варианты: ALL, IN, OUT, QIWI_CARD.
            По умолчанию - ALL.
        start_date : Optional[datetime.datetime]
            Начальная дата поиска платежей.
        end_date : Optional[datetime.datetime]
            Конечная дата поиска платежей.
        sources : Optional[list]
            Источники платежа, для отбора.
            Варианты: QW_RUB, QW_USD, QW_EUR, CARD, MK.
            По умолчанию - все указанные.

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
            end_date = datetime.datetime.utcnow()
        result_json = apihelper.total_payment_history(self.token, self.number, start_date, end_date,
                                                      operation=operation, sources=sources)
        return types.Statistics.de_json(result_json)

    def commission(self, pid, recipient, amount):
        """
        Расчет комиссии для платежа

        Parameters
        ----------
        pid : str
            Идентификатор провайдера.
        recipient : str
            Номер телефона (с международным префиксом) или номер карты/счета получателя.
            В зависимости от провайдера.
        amount : float/int
            Сумма платежа.
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
            Идентификатор провайдера.
        recipient : str
            Номер телефона (с международным префиксом) или номер карты/счета получателя.
            В зависимости от провайдера.
        amount : float/int
            Сумма платежа.
            Положительное число, округленное до 2 знаков после десятичной точки.
            При большем числе знаков значение будет округлено до копеек в меньшую сторону.
        comment : Optional[str]
            Комментарий к платежу.
        fields : dict
            Ручное добавление dict'а в платежи.
            Требуется для специфичных платежей.
            Например, перевод на счет в банке.

        Returns
        -------
        :class:`Payment <pyqiwi.types.Payment>`
            Платеж
        """
        result_json = apihelper.payments(self.token, pid, amount, recipient, comment=comment, fields=fields)
        return types.Payment.de_json(result_json)

    def identification(self, birth_date, first_name, middle_name, last_name, passport, inn=None, snils=None, oms=None):
        """
        Идентификация пользователя

        Данный запрос позволяет отправить данные для упрощенной идентификации своего QIWI кошелька.

        Warnings
        --------
        Данный метод не тестируется, соответственно я не могу гарантировать того что он будет работать как должен.
        Вы делаете это на свой страх и риск.

        Parameters
        ----------
        birth_date : str
            Дата рождения пользователя (в формате “ГГГГ-ММ-ДД”)
        first_name : str
            Имя пользователя
        middle_name : str
            Отчество пользователя
        last_name : str
            Фамилия пользователя
        passport : str
            Серия и номер паспорта пользователя (только цифры)
        inn : str
            ИНН пользователя
        snils : str
            Номер СНИЛС пользователя
        oms : str
            Номер полиса ОМС пользователя

        Returns
        -------
        :class:`Identity <pyqiwi.types.Identity>`
            Текущая идентификация пользователя.
            Параметр внутри отвечающий за подтверждение успешной идентификации: Identity.check
        """
        result_json = apihelper.identification(self.token, self.number, birth_date, first_name, middle_name, last_name,
                                               passport, inn, snils, oms)
        result_json['base_inn'] = inn
        return types.Identity.de_json(result_json)

    def create_account(self, account_alias):
        """
        Создание счета-баланса в Visa QIWI Wallet

        Parameters
        ----------
        account_alias : str
            Псевдоним нового счета.
            Один из доступных в Wallet.offered_accounts.

        Returns
        -------
        bool
            Был ли успешно создан счет?
        """
        created = apihelper.create_account(self.token, self.number, account_alias)
        return created

    @property
    def offered_accounts(self):
        result_json = apihelper.get_accounts_offer(self.token, self.number)
        accounts = []
        for account in result_json:
            accounts.append(types.Account.de_json(account))
        return accounts

    def cheque(self, txn_id, txn_type, file_format='PDF', email=None):
        """
        Получение чека по транзакции, на E-Mail или файл.

        Parameters
        ----------
        txn_id : int
            ID транзакции
        txn_type : str
            Тип указанной транзакции
        file_format : str
            Формат файла(игнорируется при использовании email)
        email : str
            E-Mail, куда отправить чек, если это необходимо.
        Returns
        -------
        list[file]
        """
        if email:
            return apihelper.cheque_send(self.token, txn_id, txn_type, email)
        else:
            return apihelper.cheque_file(self.token, txn_id, txn_type, file_format)

    def qiwi_transfer(self, account, amount, comment=None):
        """
        Перевод на Qiwi Кошелек

        Parameters
        ----------
        account : str
            Номер Qiwi Кошелька
        amount : float
            Сумма перевода
        comment : str
            Комментарий

        Returns
        -------
        :class:`Payment <pyqiwi.types.Payment>`
            Платеж
        """
        return self.send("99", account, amount, comment=comment)

    def mobile(self, account, amount):
        """
        Оплата мобильной связи.

        Parameters
        ----------
        account : str
            Номер мобильного телефона
        amount : float
            Сумма платежа

        Returns
        -------
        :class:`Payment <pyqiwi.types.Payment>`
            Платеж

        Raises
        ------
        ValueError
            В случае, если не удалось определить провайдера.
        """
        pid = detect_mobile(account)
        if pid:
            return self.send(pid, account, amount)
        else:
            raise ValueError("Не удалось определить провайдера!")


def get_commission(token, pid):
    """
    Получение стандартной комиссии

    Parameters
    ----------
    token : str
        `Ключ Qiwi API`_
    pid : str
        Идентификатор провайдера.

    Returns
    -------
    :class:`Commission <pyqiwi.types.Commission>`
        Комиссия для платежа
    """
    result_json = apihelper.local_commission(token, pid)
    return types.Commission.de_json(result_json)


def generate_form_link(pid, account, amount, comment):
    """
    Создание автозаполненной платежной формы

    Parameters
    ----------
    pid : str
        ID провайдера
    account : str
        Счет получателя
    amount : float
        Сумма платежа
    comment : str
        Комментарий

    Returns
    -------
    str
        Ссылка
    """
    url = "https://qiwi.com/payment/form/{0}".format(pid)
    params = {"currency": 643}
    if type(amount) == float:
        params['amountInteger'] = str(amount).split('.')[0]
        params['amountFraction'] = str(amount).split('.')[1]
    else:
        params['amountInteger'] = amount
    from urllib.parse import urlencode
    if comment:
        params['comment'] = urlencode(comment)
    if account:
        params['account'] = urlencode(account)
    return PreparedRequest().prepare_url(url, params).url


def detect_mobile(phone):
    """
    Определение провайдера мобильного телефона

    Parameters
    ----------
    phone : str
        Номер телефона

    Returns
    -------
    str
        ID провайдера
    """
    return apihelper.detect(phone)
