import datetime
import json

import six


class JsonDeserializable:
    """
    Субклассы этого класса гарантированно могут быть созданы из json-подобного dict'а или форматированной json строки
    Все субклассы этого класса должны перезаписывать de_json
    """

    @classmethod
    def de_json(cls, json_type):
        """
        Returns инстанс этого класса из созданного json dict'а или строки
        Эта функция должна быть перезаписана для каждого субкласса

        Returns
        -------
        Инстанс этого класса из созданного json dict'а или строки 
        """
        raise NotImplementedError

    @staticmethod
    def check_json(json_type):
        """
        Проверяет, json_type или dict или str.
        Если это dict, Returns его в исходном виде
        Иначе, Returns dict созданный из json.loads(json_type)
        """

        if type(json_type) == dict:
            return json_type
        elif type(json_type) == str:
            return json.loads(json_type)
        else:
            raise ValueError("json_type should be a json dict or string.")

    @staticmethod
    def decode_date(date_string):
        """
        Декодирует дату из строки вида отправляемого Qiwi API: %Y-%m-%dT%H:%M:%SZ

        Returns
        -------
        datetime.datetime данной строки 
        """
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

    def __str__(self):
        d = {}
        for x, y in six.iteritems(self.__dict__):
            if hasattr(y, '__dict__'):
                d[x] = y.__dict__
            else:
                d[x] = y

        return six.text_type(d)


class Account(JsonDeserializable):
    """
    Счет из Visa QIWI Кошелька

    Attributes
    ----------
    alias : str
        Псевдоним пользовательского баланса
    fs_alias : str
        Псевдоним банковского баланса
    title : str
        Название соответствующего счета кошелька
    has_balance : str
        Логический признак реального баланса в системе QIWI Кошелек 
        (не привязанная карта, не счет мобильного телефона и т.д.)
    currency : int
        Код валюты баланса (number-3 ISO-4217). 
        Возвращаются балансы в следующих валютах: 
        643 - российский рубль, 840 - американский доллар, 978 - евро
    type : :class:`AccountType <pyqiwi.types.AccountType>`
        Сведения о счете
    balance : Optional[float]
        Псевдоним пользовательского баланса
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        balance = None
        alias = obj['alias']
        fs_alias = obj['fsAlias']
        title = obj['title']
        has_balance = obj['hasBalance']
        if has_balance:
            balance = obj['balance']
        currency = obj['currency']
        _type = AccountType.de_json(obj['type'])
        return cls(alias, fs_alias, title, has_balance, currency, _type, balance)

    def __init__(self, alias, fs_alias, title, has_balance, currency, _type, balance):
        self.alias = alias
        self.fs_alias = fs_alias
        self.title = title
        self.has_balance = has_balance
        self.currency = currency
        self.type = _type
        self.balance = balance


class AccountType(JsonDeserializable):
    """
    Сведения о счете из Visa QIWI Кошелька
    
    Attributes
    ----------
    id : str
        Кодовое название счета
    title : str
        Название счета
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        return cls(obj['id'], obj['title'])

    def __init__(self, _id, title):
        self.id = _id
        self.title = title


class Profile(JsonDeserializable):
    """
    Профиль пользователя Visa QIWI Кошелька

    Attributes
    ----------
    auth_info : Optional[:class:`AuthInfo <pyqiwi.types.AuthInfo>`]
        Настройки авторизации пользователя
    contract_info : Optional[:class:`ContractInfo <pyqiwi.types.ContractInfo>`]
        Информация о кошельке пользователя
    user_info : Optional[:class:`UserInfo <pyqiwi.types.UserInfo>`]
        Прочие пользовательские данные
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        auth_info = AuthInfo.de_json(obj['authInfo'])
        contract_info = ContractInfo.de_json(obj['contractInfo'])
        user_info = UserInfo.de_json(obj['userInfo'])
        return cls(auth_info, contract_info, user_info)

    def __init__(self, auth_info, contract_info, user_info):
        self.auth_info = auth_info
        self.contract_info = contract_info
        self.user_info = user_info


class AuthInfo(JsonDeserializable):
    """
    Профиль пользователя Visa QIWI Кошелька

    Attributes
    ----------
    bound_email : str/None
        E-mail, привязанный к кошельку.
        Если отсутствует, то ``None``
    ip : str
        IP-адрес последней пользовательской сессии
    last_login_date : str
        Дата/время последней сессии в QIWI Кошельке
    mobile_pin_info : :class:`MobilePinInfo <pyqiwi.types.MobilePinInfo>`
        Данные о PIN-коде мобильного приложения QIWI Кошелька
    pass_info : :class:`PassInfo <pyqiwi.types.PassInfo>`
        Данные о пароле к сайту qiwi.com
    person_id : int
        Номер кошелька пользователя
    pin_info : :class:`PinInfo <pyqiwi.types.PinInfo>`
        Данные о PIN-коде к приложению QIWI Кошелька на QIWI терминалах
    registration_date : datetime.datetime
        Дата/время регистрации QIWI Кошелька пользователя 
        (через сайт либо мобильное приложение, либо другим способом)
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        bound_email = obj['boundEmail']
        ip = obj['ip']
        last_login_date = cls.decode_date(obj['lastLoginDate'])
        mobile_pin_info = MobilePinInfo.de_json(obj['mobilePinInfo'])
        pass_info = PassInfo.de_json(obj['passInfo'])
        person_id = obj['personId']
        pin_info = PinInfo.de_json(obj['pinInfo'])
        registration_date = cls.decode_date(obj['registrationDate'])
        return cls(bound_email, ip, last_login_date, mobile_pin_info,
                   pass_info, person_id, pin_info, registration_date)

    def __init__(self, bound_email, ip, last_login_date, mobile_pin_info,
                 pass_info, person_id, pin_info, registration_date):
        self.bound_email = bound_email
        self.ip = ip
        self.last_login_date = last_login_date
        self.mobile_pin_info = mobile_pin_info
        self.pass_info = pass_info
        self.person_id = person_id
        self.pin_info = pin_info
        self.registration_date = registration_date


class MobilePinInfo(JsonDeserializable):
    """
    Данные о PIN-коде мобильного приложения QIWI Кошелька

    Attributes
    ----------
    mobile_pin_used : bool
        Логический признак использования PIN-кода 
        (фактически означает, что мобильное приложение используется)
    last_mobile_pin_change : datetime.datetime
        Дата/время последнего изменения PIN-кода мобильного приложения QIWI Кошелька
    next_mobile_pin_change : datetime.datetime
        Дата/время следующего (планового) изменения PIN-кода мобильного приложения QIWI Кошелька
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        last_mobile_pin_change = None
        next_mobile_pin_change = None
        mobile_pin_used = obj['mobilePinUsed']
        if mobile_pin_used:
            last_mobile_pin_change = cls.decode_date(obj['lastMobilePinChange'])
            next_mobile_pin_change = cls.decode_date(obj['nextMobilePinChange'])
        return cls(mobile_pin_used, last_mobile_pin_change, next_mobile_pin_change)

    def __init__(self, mobile_pin_used, last_mobile_pin_change, next_mobile_pin_change):
        self.mobile_pin_used = mobile_pin_used
        self.last_mobile_pin_change = last_mobile_pin_change
        self.next_mobile_pin_change = next_mobile_pin_change


class PassInfo(JsonDeserializable):
    """
    Данные о пароле к сайту qiwi.com

    Attributes
    ----------
    last_pass_change : str
        Дата/время последнего изменения пароля сайта qiwi.com
    next_pass_change : str
        Дата/время следующего (планового) изменения пароля сайта qiwi.com
    password_used : bool
        Логический признак использования пароля 
        (фактически означает, что пользователь заходит на сайт)
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        last_pass_change = None
        next_pass_change = None
        password_used = obj['passwordUsed']
        if password_used:
            last_pass_change = cls.decode_date(obj['lastPassChange'])
            next_pass_change = cls.decode_date(obj['nextPassChange'])
        return cls(last_pass_change, next_pass_change, password_used)

    def __init__(self, last_pass_change, next_pass_change, password_used):
        self.last_pass_change = last_pass_change
        self.next_pass_change = next_pass_change
        self.password_used = password_used


class PinInfo(JsonDeserializable):
    """
    Данные о PIN-коде к приложению QIWI Кошелька на QIWI терминалах

    Attributes
    ----------
    pin_used : bool
        Логический признак использования PIN-кода
        (фактически означает, что пользователь заходил в приложение)
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        pin_used = obj['pinUsed']
        return cls(pin_used)

    def __init__(self, pin_used):
        self.pin_used = pin_used


class ContractInfo(JsonDeserializable):
    """
    Информация о кошельке пользователя

    Attributes
    ----------
    blocked : bool
        Логический признак блокировки кошелька
    contract_id : int
        Номер кошелька пользователя
    creation_date : datetime.datetime
        Дата/время создания QIWI Кошелька пользователя
        (через сайт либо мобильное приложение, либо при первом пополнении, либо другим способом)
    features : ???
        Служебная информация
    identification_info : list[:class:`IdentificationInfo <pyqiwi.types.IdentificationInfo>`]
        Данные об идентификации пользователя
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        blocked = obj['blocked']
        contract_id = obj['contractId']
        creation_date = cls.decode_date(obj['creationDate'])
        features = obj['features']
        identification_info = []
        for _id in obj['identificationInfo']:
            identification_info.append(IdentificationInfo.de_json(_id))
        return cls(blocked, contract_id, creation_date, features, identification_info)

    def __init__(self, blocked, contract_id, creation_date, features, identification_info):
        self.blocked = blocked
        self.contract_id = contract_id
        self.creation_date = creation_date
        self.features = features
        self.identification_info = identification_info


class IdentificationInfo(JsonDeserializable):
    """
    Данные об идентификации пользователя

    Attributes
    ----------
    bank_alias : str
        Акроним системы, в которой пользователь получил идентификацию:
        QIWI - QIWI Кошелек.
    identification_level : str
        Текущий уровень идентификации кошелька
        Возможные значения:
        ANONYMOUS - без идентификации
        SIMPLE, VERIFIED - упрощенная идентификация
        FULL - полная идентификация
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        bank_alias = obj['bankAlias']
        identification_level = obj['identificationLevel']
        return cls(bank_alias, identification_level)

    def __init__(self, bank_alias, identification_level):
        self.bank_alias = bank_alias
        self.identification_level = identification_level


class UserInfo(JsonDeserializable):
    """
    Прочие пользовательские данные

    Attributes
    ----------
    default_pay_currency : int
        Код валюты баланса кошелька по умолчанию (number-3 ISO-4217)
    default_pay_source : ???
        Служебная информация
    email : str
        E-mail пользователя
    first_txn_id : int
        Номер первой транзакции пользователя после регистрации
    language : ???
        Служебная информация
    operator : str
        Название мобильного оператора номера пользователя
    phone_hash : ???
        Служебная информация
    promo_enabled : ???
        Служебная информация
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        default_pay_currency = obj['defaultPayCurrency']
        default_pay_source = obj['defaultPaySource']
        email = obj['email']
        first_txn_id = obj['firstTxnId']
        language = obj['language']
        operator = obj['operator']
        phone_hash = obj['phoneHash']
        promo_enabled = obj['promoEnabled']
        return cls(default_pay_currency, default_pay_source, email, first_txn_id,
                   language, operator, phone_hash, promo_enabled)

    def __init__(self, default_pay_currency, default_pay_source, email, first_txn_id,
                 language, operator, phone_hash, promo_enabled):
        self.default_pay_currency = default_pay_currency
        self.default_pay_source = default_pay_source
        self.email = email
        self.first_txn_id = first_txn_id
        self.language = language
        self.operator = operator
        self.phone_hash = phone_hash
        self.promo_enabled = promo_enabled


class Transaction(JsonDeserializable):
    """
    Транзакция

    Attributes
    ----------
    txn_id : int
        ID транзакции в процессинге
    person_id : int
        Номер кошелька
    date : datetime.datetime
        Дата/время платежа, время московское 
    error_code : int/float
        Код ошибки платежа
    error : str
        Описание ошибки
    status : str
        Статус платежа. Возможные значения:
        WAITING - платеж проводится, 
        SUCCESS - успешный платеж, 
        ERROR - ошибка платежа.
    type : str
        Тип платежа. Возможные значения:
        IN - пополнение, 
        OUT - платеж, 
        QIWI_CARD - платеж с карт QIWI (QVC, QVP).
    status_text : str
        Текстовое описание статуса платежа
    trm_txn_id : str
        Клиентский ID транзакции
    account : str
        Номер счета получателя
    sum : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Данные о сумме платежа
    commission : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Данные о комиссии платежа
    total : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Данные об общей сумме платежа
    provider : :class:`TransactionProvider <pyqiwi.types.TransactionProvider>`
        Данные о провайдере
    comment : str
        Комментарий к платежу
    currency_rate : float/int
        Курс конвертации (если применяется в транзакции)
    source : ???
        ???
    extras : ???
        Служебная информация
    cheque_ready : bool
        Специальное поле
    bank_document_available : bool
        Специальное поле
    bank_document_ready : bool
        Специальное поле
    repeat_payment_enabled : bool
        Специальное поле
    favorite_payment_enabled : bool
        Специальное поле
    regular_payment_enabled : bool
        Специальное поле
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        txn_id = obj['txnId']
        person_id = obj['personId']
        date = cls.decode_date(obj['date'])
        error_code = obj['errorCode']
        error = obj['error']
        status = obj['status']
        _type = obj['type']
        status_text = obj['statusText']
        trm_txn_id = obj['trmTxnId']
        account = obj['account']
        _sum = TransactionSum.de_json(obj['sum'])
        commission = TransactionSum.de_json(obj['commission'])
        total = TransactionSum.de_json(obj['total'])
        provider = TransactionProvider.de_json(obj['provider'])
        source = obj['source']
        comment = obj['comment']
        currency_rate = obj['currencyRate']
        extras = obj['extras']
        cheque_ready = obj['chequeReady']
        bank_document_available = obj['bankDocumentAvailable']
        bank_document_ready = obj['bankDocumentReady']
        repeat_payment_enabled = obj['repeatPaymentEnabled']
        favorite_payment_enabled = obj['favoritePaymentEnabled']
        regular_payment_enabled = obj['regularPaymentEnabled']
        return cls(txn_id, person_id, date, error_code, error,
                   status, _type, status_text, trm_txn_id, account, _sum, commission, total,
                   provider, source, comment, currency_rate, extras, cheque_ready, bank_document_available,
                   bank_document_ready, repeat_payment_enabled, favorite_payment_enabled, regular_payment_enabled)

    def __init__(self, txn_id, person_id, date, error_code, error,
                 status, _type, status_text, trm_txn_id, account, _sum, commission, total,
                 provider, source, comment, currency_rate, extras, cheque_ready, bank_document_available,
                 bank_document_ready, repeat_payment_enabled, favorite_payment_enabled, regular_payment_enabled):
        self.txn_id = txn_id
        self.person_id = person_id
        self.date = date
        self.error_code = error_code
        self.error = error
        self.status = status
        self.type = _type
        self.status_text = status_text
        self.trm_txn_id = trm_txn_id
        self.account = account
        self.sum = _sum
        self.commission = commission
        self.total = total
        self.provider = provider
        self.source = source
        self.comment = comment
        self.currency_rate = currency_rate
        self.extras = extras
        self.cheque_ready = cheque_ready
        self.bank_document_available = bank_document_available
        self.bank_document_ready = bank_document_ready
        self.repeat_payment_enabled = repeat_payment_enabled
        self.favorite_payment_enabled = favorite_payment_enabled
        self.regular_payment_enabled = regular_payment_enabled


class TransactionSum(JsonDeserializable):
    """
    Данные о платеже

    Attributes
    ----------
    amount : float/int
        Сумма
    currency : str
        Валюта
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        amount = obj['amount']
        currency = obj['currency']
        return cls(amount, currency)

    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency


class TransactionProvider(JsonDeserializable):
    """
    Данные о провайдере

    Attributes
    ----------
    id : int
        ID провайдера в процессинге
    short_name : str
        Краткое наименование провайдера
    long_name : str
        Развернутое наименование провайдера
    logo_url : str
        Cсылка на логотип провайдера
    description : str
        Описание провайдера (HTML)
    keys : str
        Список ключевых слов
    site_url : str
        Сайт провайдера
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        _id = obj['id']
        short_name = obj['shortName']
        long_name = obj['longName']
        logo_url = obj['logoUrl']
        description = obj['description']
        keys = obj['keys']
        site_url = obj['siteUrl']
        return cls(_id, short_name, long_name, logo_url, description, keys, site_url)

    def __init__(self, _id, short_name, long_name, logo_url, description, keys, site_url):
        self.id = _id
        self.short_name = short_name
        self.long_name = long_name
        self.logo_url = logo_url
        self.description = description
        self.keys = keys
        self.site_url = site_url


class Statistics(JsonDeserializable):
    """
    Статистика платежей

    Attributes
    ----------
    incoming_total : list[:class:`TransactionSum <pyqiwi.types.TransactionSum>`]
        Данные о входящих платежах (пополнениях), отдельно по каждой валюте
    outgoing_total : list[:class:`TransactionSum <pyqiwi.types.TransactionSum>`]
        Данные об исходящих платежах, отдельно по каждой валюте
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        incoming_total = []
        for currency in obj['incomingTotal']:
            incoming_total.append(TransactionSum.de_json(currency))
        outgoing_total = []
        for currency in obj['outgoingTotal']:
            outgoing_total.append(TransactionSum.de_json(currency))
        return cls(incoming_total, outgoing_total)

    def __init__(self, incoming_total, outgoing_total):
        self.incoming_total = incoming_total
        self.outgoing_total = outgoing_total


class Commission(JsonDeserializable):
    """
    Стандартная комиссия

    Attributes
    ----------
    ranges : list[:class:`CommissionRange <pyqiwi.types.CommissionRange>`]
        Массив объектов с граничными условиями комиссий
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        ranges = []
        for com_range in obj['content']['terms']['commission']['ranges']:
            ranges.append(CommissionRange.de_json(com_range))
        return cls(ranges)

    def __init__(self, ranges):
        self.ranges = ranges


class CommissionRange(JsonDeserializable):
    """
    Условия комиссии

    Attributes
    ----------
    bound : Optional[float/int]
        Сумма платежа, начиная с которой применяется условие
    rate : Optional[float/int]
        Комиссия (абсолютный множитель)
    min : Optional[float/int]
        Минимальная сумма комиссии
    max : Optional[float/int]
        Максимальная сумма комиссии
    fixed : Optional[float/int]
        Фиксированная сумма комиссии
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        bound = obj.get('bound')
        fixed = obj.get('fixed')
        rate = obj.get('rate')
        _min = obj.get('min')
        _max = obj.get('max')
        return cls(bound, fixed, rate, _min, _max)

    def __init__(self, bound, fixed, rate, _min, _max):
        self.bound = bound
        self.fixed = fixed
        self.rate = rate
        self.min = _min
        self.max = _max


class OnlineCommission(JsonDeserializable):
    """
    Подсчитанная комиссия

    Attributes
    ----------
    provider_id : int
        Идентификатор провайдера
    withdraw_sum : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Общая сумма платежа
    enrollment_sum : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Сумма платежа с учетом комиссии
    qw_commission : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Комиссия Qiwi
    funding_source_commission : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Комиссия платежной системы(если Qiwi, то всегда 0)
    withdraw_to_enrollment_rate : float/int
        ???
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        provider_id = obj['providerId']
        withdraw_sum = TransactionSum.de_json(obj['withdrawSum'])
        enrollment_sum = TransactionSum.de_json(obj['enrollmentSum'])
        qw_commission = TransactionSum.de_json(obj['qwCommission'])
        funding_source_commission = TransactionSum.de_json(obj['fundingSourceCommission'])
        withdraw_to_enrollment_rate = obj['withdrawToEnrollmentRate']
        return cls(provider_id, withdraw_sum, enrollment_sum,
                   qw_commission, funding_source_commission, withdraw_to_enrollment_rate)

    def __init__(self, provider_id, withdraw_sum, enrollment_sum,
                 qw_commission, funding_source_commission, withdraw_to_enrollment_rate):
        self.provider_id = provider_id
        self.withdraw_sum = withdraw_sum
        self.enrollment_sum = enrollment_sum
        self.qw_commission = qw_commission
        self.funding_source_commission = funding_source_commission
        self.withdraw_to_enrollment_rate = withdraw_to_enrollment_rate


class Payment(JsonDeserializable):
    """
    Данные о принятом платеже

    Attributes
    ----------
    id : str
        Клиентский ID транзакции
        (В этой библиотеке, он считается 1000*Unix timestamp)
    terms : str
        Идентификатор провайдера
    fields : :class:`PaymentFields <pyqiwi.types.PaymentFields>`
        Реквизиты платежа
    sum : :class:`TransactionSum <pyqiwi.types.TransactionSum>`
        Данные о сумме платежа
    source : str
        ???
    comment : Optional[str]
        Комментарий к платежу
    transaction : dict
        Данные о транзакции в процессинге
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        _id = obj['id']
        terms = obj['terms']
        fields = PaymentFields.de_json(obj['fields'])
        _sum = TransactionSum.de_json(obj['sum'])
        transaction = obj['transaction']
        source = obj['source']
        comment = obj.get('comment')
        return cls(_id, terms, fields, _sum, transaction, source, comment)

    def __init__(self, _id, terms, fields, _sum, transaction, source, comment):
        self.id = _id
        self.terms = terms
        self.fields = fields
        self.sum = _sum
        self.transaction = transaction
        self.source = source
        self.comment = comment


class PaymentFields(JsonDeserializable):
    """
    Реквизиты платежа

    Данный класс представляет из себя полностью хаотичную структуру
    Судя по документации Qiwi API, создается из исходного поля fields для платежа
    
    Note
    -----
    Если вы хотите посмотреть исходный вид выданный Qiwi API, используйте str(PaymentFields)
    """

    @classmethod
    def de_json(cls, json_type):
        obj = cls.check_json(json_type)
        fields = cls()
        for key in obj:
            setattr(fields, key, obj[key])
        return fields

    def __init__(self):
        pass
