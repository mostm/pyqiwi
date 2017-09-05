# pyQiwi
Python QIWI API Wrapper
## Установка
`pip install -r requirements`
Добавьте ваш токен для API([Получить](qiwi.com/token)) в config.py(Wallet>token)
Если вы хотите использовать функции истории, добавьте номер, на котором вы получили токен в config.py(Wallet>number)
## Использование
```python
import qiwi
```
## Быстрый туториал
#### Получить текущий баланс
```python
import qiwi

balance = qiwi.Person(number='79001234567').balance()
```
#### Отправка платежа
```python
import qiwi

payment = qiwi.Payment(id=99, recipient='79001234567', amount=1.11).send(comment='Привет!')
```
#### Получить комиссию для платежа
```python
import qiwi

comm = qiwi.Payment(id=99, recipient='79001234567', amount=1.11).commission()
```