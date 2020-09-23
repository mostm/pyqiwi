======
pyQiwi
======

Python Qiwi API Wrapper

* Лицензия: MIT
* Документация: https://pyqiwi.readthedocs.io.


Возможности
-----------

* Оплата любых услуг
* Переводы на любой Qiwi Кошелек
* Статистика по платежам
* История о сделанных платежах в любой промежуток времени
* Прохождение упрощенной идентификации
* Определение провайдера мобильного телефона

Установка
---------

$ pip install qiwipy


Использование
---------

import pyqiwi
wallet = pyqiwi.Wallet(token='', number='79001234567')

Быстрый туториал
----------------

Получить текущий баланс
~~~~~~~~~~~~~~~~~~~~~~~

print(wallet.balance())

Отправка платежа
~~~~~~~~~~~~~~~~

payment = wallet.send(pid=99, recipient='79001234567', amount=1.11, comment='Привет!')
example = 'Payment is {0}\nRecipient: {1}\nPayment Sum: {2}'.format(
           payment.transaction['state']['code'], payment.fields['account'], payment.sum)
print(example)


Получить комиссию для платежа
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

commission = wallet.commission(pid=99, recipient='79001234567', amount=1.11)
print(commission.qw_commission.amount)


Для более подробных инструкций, посетите документацию.
