# pyqiwi
Python QIWI API Wrapper

## Dependencies
`requests==2.18.4` This was build with this version in mind, but can support others.

#### Send Payment
```python
import qiwi

payment = qiwi.Payment(id=99, recipient='79000000000', amount=1.11).send(comment='Hi there!')
```