======
pyQiwi
======


.. image:: https://img.shields.io/pypi/v/qiwipy.svg
        :target: https://pypi.python.org/pypi/qiwipy
        :alt: Релиз на PyPI

.. image:: https://img.shields.io/travis/mostm/pyqiwi.svg
        :target: https://travis-ci.org/mostm/pyqiwi
        :alt: Статус сборки

.. image:: https://readthedocs.org/projects/pyqiwi/badge/?version=latest
        :target: https://pyqiwi.readthedocs.io/ru/latest/?badge=latest
        :alt: Статус документации


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

.. code-block:: console

    $ pip install qiwipy

Использование
---------

.. code-block:: python

    import pyqiwi
    wallet = pyqiwi.Wallet(token='', number='79001234567')



Быстрый туториал
----------------

Получить текущий баланс
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    print(wallet.balance())

Отправка платежа
~~~~~~~~~~~~~~~~


.. code-block:: python

    payment = wallet.send(id=99, recipient='79001234567', amount=1.11, comment='Привет!')
    example = 'Payment is {0}\nRecipient: {1}\nPayment Sum: {2}'.format(
              payment.transaction['state']['code'], payment.fields['account'], payment.sum)
    print(example)


Получить комиссию для платежа
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

    commission = wallet.commission(pid=99, recipient='79001234567', amount=1.11)
    print(commission.qw_commission.amount)


Для более подробных инструкций, посетите `документацию`_.

.. _документацию: https://pyqiwi.readthedocs.io