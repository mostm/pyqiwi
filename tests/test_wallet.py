# -*- coding: utf-8 -*-
import sys

sys.path.append('../')

import pytest
import os
import datetime

import pyqiwi
from pyqiwi import Wallet
from pyqiwi.util import url_params, merge_dicts, split_float
from urllib.parse import unquote

should_skip = 'TOKEN' and 'NUMBER' not in os.environ

if not should_skip:
    TOKEN = os.environ['TOKEN']
    NUMBER = os.environ['NUMBER']


@pytest.mark.skipif(should_skip, reason="No environment variables configured")
class TestWallet:
    def test_create_wallet(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        qiwi_wallet = Wallet(TOKEN)
        assert isinstance(qiwi_wallet, Wallet)

    def test_check_history(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        history = qiwi_wallet.history()
        assert type(history) == dict
        for tnx in history['transactions']:
            assert type(tnx) == pyqiwi.types.Transaction
        assert type(history['next_txn_date']) == datetime.datetime
        assert type(history['next_txn_id']) == int

    def test_check_profile(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        profile = qiwi_wallet.profile
        assert type(profile) == pyqiwi.types.Profile

    def test_stat(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        stat = qiwi_wallet.stat()
        assert type(stat) == pyqiwi.types.Statistics

    def test_check_accounts(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        accounts = qiwi_wallet.offered_accounts
        for account in accounts:
            assert type(account) == pyqiwi.types.Account

    def test_get_commission(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        commission = qiwi_wallet.get_commission('26476')
        assert type(commission) == pyqiwi.types.Commission
        for commission_range in commission.ranges:
            assert type(commission_range) == pyqiwi.types.CommissionRange

    def test_online_commission(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        commission = qiwi_wallet.get_commission('26476')
        assert type(commission) == pyqiwi.types.Commission
        saved_range = None
        for commission_range in commission.ranges:
            assert type(commission_range) == pyqiwi.types.CommissionRange
            if commission_range.rate != 1.0 or commission_range.rate != 1:
                saved_range = commission_range
        online_commission = qiwi_wallet.commission('26476', qiwi_wallet.number, 100)
        assert online_commission.qw_commission.amount == 100 * saved_range.rate

    def test_cross_rates(self):
        qiwi_wallet = Wallet(TOKEN, number=NUMBER)
        assert isinstance(qiwi_wallet, Wallet)
        rates = qiwi_wallet.cross_rates
        assert type(rates) == list
        for rate in rates:
            assert type(rate) == pyqiwi.types.Rate

    def test_form_link(self):
        data = {
            'pid': 99,
            'account': 79000000000,
            'amount': 123,
            'comment': 'Hey, it works!'
        }
        paylink = pyqiwi.generate_form_link(**data)
        result = url_params(unquote(paylink))
        data.pop('pid') # It is not on params, it's in URL
        # Qiwi requires for amount to be split into integer and fraction
        data = merge_dicts(data, split_float(data.get('amount')))
        data.pop('amount')
        # unquote won't process + to <Space>, but Qiwi should
        if result.get("extra['comment']"):
            result["extra['comment']"] = result["extra['comment']"].replace('+', ' ')
        for key in data:
            if key == 'account':
                assert result["extra['account']"] == str(data[key])
            elif key == 'comment':
                assert result["extra['comment']"] == str(data[key])
