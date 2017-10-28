# pyQiwi
Python QIWI API Wrapper

## Установка
`pip install -U qiwipy`
или
`pip install git+https://github.com/mostm/pyqiwi.git`

## Использование
```python
import pyqiwi
wallet = pyqiwi.Wallet(token='', number='79001234567')
```

## Быстрый туториал

#### Получить текущий баланс
```python
print(wallet.balance(643))
```

#### Отправка платежа
```python
payment = wallet.send(id=99, recipient='79001234567', amount=1.11, comment='Привет!')
example = 'Payment is {0}\nRecipient: {1}\nPayment Sum: {2}'.format(
          payment.transaction['state']['code'], payment.fields['account'], payment.sum)
print(example)
```

#### Получить комиссию для платежа
```python
commission = wallet.commission(pid=99, recipient='79001234567', amount=1.11)
print(commission.qw_commission.amount)
```