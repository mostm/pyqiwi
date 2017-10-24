# pyQiwi
Python QIWI API Wrapper

## Установка
1. `pip install -r requirements.txt`
2. Получите токен для Qiwi API [здесь](https://qiwi.com/api)
3. Добавьте qiwi.py в ваш проект

## Использование
```python
import qiwi
```

## Быстрый туториал

#### Получить текущий баланс
```python
wallet = qiwi.Wallet(token='', number='79001234567')
balance = wallet.balance()
```

#### Отправка платежа
```python
wallet = qiwi.Wallet(token='', number='79120004567')
payment = wallet.send(id=99, recipient='79001234567', amount=1.11, comment='Привет!')
```

#### Получить комиссию для платежа
```python
wallet = qiwi.Wallet(token='', number='79120004567')
comission = wallet.commission(pid=99, recipient='79001234567', amount=1.11)
```