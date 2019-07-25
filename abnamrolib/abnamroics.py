#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: abnamrolib.py
#
# Copyright 2019 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

"""
Main code for abnamrolib.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

from requests import Session
from urllib3.util import parse_url

from abnamrolib.lib.core import Transaction, Comparable
from abnamrolib.abnamrolibexceptions import AuthenticationFailed

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''19-07-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".

# This is the main prefix used for logging
LOGGER_BASENAME = '''abnamrolib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class Account(Comparable):  # pylint: disable=too-many-public-methods
    """Models a credit card account."""

    @property
    def number(self):
        """Number."""
        return self._data.get('accountNumber')

    @property
    def product_id(self):
        """Product id."""
        return self._data.get('productId')

    @property
    def credit_limit(self):
        """Credit limit."""
        return self._data.get('creditLimit')

    @property
    def current_balance(self):
        """Current balance."""
        return self._data.get('currentBalance')

    @property
    def available_credit(self):
        """Available credit."""
        return self._data.get('creditLeftToUse')

    @property
    def authorized_balance(self):
        """Authorized balance."""
        return self._data.get('authorizedBalance')

    @property
    def in_arrears(self):
        """In arrears."""
        return self._data.get('inArrears')

    @property
    def arrears_status(self):
        """Arrears status."""
        return self._data.get('arrearsStatus')

    @property
    def in_overlimit(self):
        """In overlimit."""
        return self._data.get('inOverLimit')

    @property
    def loyalty_points(self):
        """Loyalty points."""
        return self._data.get('loyaltyPoints')

    @property
    def loyalty_amount(self):
        """Loyalty amount."""
        return self._data.get('loyaltyAmount')

    @property
    def is_valid(self):
        """Is Valid."""
        return self._data.get('valid')

    @property
    def next_payment_date(self):
        """Next payment date."""
        return self._data.get('paymentDate')

    @property
    def last_available_payment_date(self):
        """Last available payment date."""
        return self._data.get('lastDayOfStatementToBePaid')

    @property
    def amount_due(self):
        """Amount due."""
        return self._data.get('amountDue')

    @property
    def due_date(self):
        """Due date."""
        return self._data.get('dueDate')

    @property
    def iban(self):
        """Iban."""
        return self._data.get('iban')

    @property
    def balance_carried_forward(self):
        """Balance carried forward."""
        return self._data.get('balanceCarriedForward')

    @property
    def payment_condition(self):
        """Payment condition."""
        return self._data.get('paymentCondition')

    @property
    def remaining_amount_due(self):
        """Remaining amount due."""
        return self._data.get('remainingAmountDue')

    @property
    def credit_agreement(self):
        """Credit Agreement."""
        return self._data.get('creditAgreement')

    @property
    def payment_state(self):
        """Payment state."""
        return self._data.get('paymentState')

    @property
    def charge_percentage(self):
        """Charge percentage."""
        return self._data.get('chargePercentage')

    @property
    def fixed_amount(self):
        """Fixed amount."""
        return self._data.get('fixedAmount')

    @property
    def prepaid(self):
        """Prepaid."""
        return self._data.get('prepaid')

    @property
    def continuous_credit(self):
        """Continuous credit."""
        return self._data.get('continuousCredit')

    @property
    def migrated(self):
        """Migrated."""
        return self._data.get('migrated')

    @property
    def credit_agreement_conditional(self):
        """Credit agreement conditional."""
        return self._data.get('creditagreementConditional')

    @property
    def main_card_holder(self):
        """Main card holder."""
        return self._data.get('mainCardHolder')

    @property
    def app_enrolled(self):
        """App enrolled."""
        return self._data.get('appEnrolled')

    @property
    def over_limit(self):
        """Over limit."""
        return self._data.get('overLimit')


class Period:
    """Models the payment period."""

    def __init__(self, credit_card, data):
        self._credit_card = credit_card
        self._data = data
        self._transactions = None

    @property
    def period(self):
        """Period."""
        return self._data.get('period')

    @property
    def start_date(self):
        """Start date."""
        return self._data.get('startDatePeriod')

    @property
    def end_date(self):
        """End date."""
        return self._data.get('endDatePeriod')

    @property
    def current_period(self):
        """Current period."""
        return self._data.get('currentPeriod')

    @property
    def show_statement(self):
        """Show statement."""
        return self._data.get('showStatement')

    @property
    def balance_brought_forward(self):
        """Balance brought forward."""
        return self._data.get('balanceBroughtForward')

    @property
    def balance_carried_forward(self):
        """Balance carried forward."""
        return self._data.get('balanceCarriedForward')

    @property
    def transactions(self):
        """Transactions.

        Returns:
            transactions (list): A list of the transaction objects for the account

        """
        if self._transactions is None:
            url = f'{self._credit_card.base_url}/sec/nl/sec/transactions'
            params = {'accountNumber': self._credit_card.account_number,
                      'flushCache': True,
                      'fromPeriod': self.period,
                      'untilPeriod': self.period}
            response = self._credit_card.session.get(url, params=params)
            response.raise_for_status()
            self._transactions = [CreditCardTransaction(data) for data in response.json()]
        return self._transactions


class CreditCardTransaction(Transaction):
    """Models a credit card transaction."""

    @property
    def country_code(self):
        """Country code."""
        return self._data.get('countryCode')

    @property
    def card_last_four_digits(self):
        """Card last four digits."""
        return self._data.get('lastFourDigits')

    @property
    def transaction_date(self):
        """Transaction date."""
        return self._data.get('transactionDate')

    @property
    def description(self):
        """Description."""
        return self._clean_up(self._data.get('description'))

    @property
    def billing_amount(self):
        """Billing amount."""
        return self._data.get('billingAmount')

    @property
    def billing_currency(self):
        """Billing currency."""
        return self._data.get('billingCurrency')

    @property
    def source_amount(self):
        """Source amount."""
        return self._data.get('sourceAmount')

    @property
    def source_currency(self):
        """Source currency."""
        return self._data.get('sourceCurrency')

    @property
    def merchant_category_description(self):
        """Merchant category description."""
        return self._data.get('merchantCategoryCodeDescription')

    @property
    def type_of_transaction(self):
        """Type of transaction."""
        return self._data.get('typeOfTransaction')

    @property
    def batch_number(self):
        """Batch number."""
        return self._data.get('batchNr')

    @property
    def batch_sequence_number(self):
        """Batch sequence number."""
        return self._data.get('batchSequenceNr')

    @property
    def type_of_purchase(self):
        """Type of purchase."""
        return self._data.get('typeOfPurchase')

    @property
    def processing_time(self):
        """Processing time."""
        return self._data.get('processingTime')

    @property
    def indicator_extra_card(self):
        """Indicator extra card."""
        return self._data.get('indicatorExtraCard')

    @property
    def embossing_name(self):
        """Embossing name."""
        return self._data.get('embossingName')

    @property
    def direct_debit_state(self):
        """Direct debit state."""
        return self._data.get('directDebitState')

    @property
    def is_mobile(self):
        """Is mobile."""
        return self._data.get('mobile')

    @property
    def loyalty_points(self):
        """Loyalty points."""
        return self._data.get('loyaltyPoints')

    @property
    def charge_back_allowed(self):
        """Charge back allowed."""
        return self._data.get('chargeBackAllowed')


class CreditCard(Comparable):  # pylint: disable=too-many-instance-attributes
    """Models a credit card account."""

    def __init__(self, username, password):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self._username = username
        self._password = password
        self._base_url = 'https://www.icscards.nl'
        self.session = self._get_authenticated_session()
        self._account_number = None
        self._periods = None
        self._account = None
        super().__init__(self.account._data)  # pylint: disable=protected-access

    @property
    def host(self):
        """Host."""
        return parse_url(self.base_url).host

    @property
    def base_url(self):
        """Base url."""
        return self._base_url

    def _get_authenticated_session(self):
        session = Session()
        headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                  'Gecko/20100101 Firefox/67.0')}
        session.headers.update(headers)
        session.headers.update({'X-XSRF-TOKEN': self._get_xsrf_token(session,
                                                                     self._username,
                                                                     self._password)})
        self.original_get = session.get
        session.get = self._patched_get
        return session

    def _patched_get(self, *args, **kwargs):
        url = args[0]
        self._logger.debug('Using patched get request for url %s', url)
        response = self.original_get(*args, **kwargs)
        if not url.startswith(self._base_url):
            self._logger.debug('Url "%s" requested is not from credit card api, passing through', url)
            return response
        if 'USERNAME=unauthenticated' in response.url:
            self._logger.info('Expired session detected, trying to re authenticate!')
            self.session = self._get_authenticated_session()
            response = self.original_get(*args, **kwargs)
        return response

    def _get_xsrf_token(self, session, username, password):
        login_url = f'{self.base_url}/pub/nl/pub/login'
        self._logger.debug('Trying to authenticate to url "%s"', login_url)
        payload = {'loginType': 'PASSWORD',
                   'virtualPortal': 'ICS-ABNAMRO',
                   'username': username,
                   'password': password}
        response = session.post(login_url, json=payload)
        if not response.ok:
            raise AuthenticationFailed(response.text)
        return session.cookies.get('XSRF-TOKEN')

    @property
    def account_number(self):
        """Account number in Iban format."""
        if not self._account_number:
            url = f'{self.base_url}/sec/nl/sec/allaccountsv2'
            self._logger.debug('Trying to get all accounts from url "%s"', url)
            response = self.session.get(url)
            response.raise_for_status()
            self._account_number = response.json()[0].get('accountNumber')
        return self._account_number

    @property
    def periods(self):
        """Payment periods."""
        if self._periods is None:
            url = f'{self.base_url}/sec/nl/sec/periods'
            params = {'accountNumber': self.account_number}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self._periods = [Period(self, data)
                             for data in response.json()]
        return self._periods

    @property
    def account(self):
        """Account."""
        if self._account is None:
            url = f'{self.base_url}/sec/nl/sec/accountv5'
            params = {'accountNumber': self.account_number}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            self._account = Account(response.json())
        return self._account

    def get_period(self, year, month):
        """Get a period.

        Args:
            year (str): The year of the period to retrieve
            month (str): The month of the period to retrieve

        Returns:
            period (Period): The period for the provided date

        """
        return next((period for period in self.periods
                     if period.period == f'{year}-{month.zfill(2)}'), None)

    def get_transactions_for_period(self, year, month):
        """Retrieves the transactions for that period.

        Args:
            year (str): The year to retrieve transactions for
            month (str): The month to retrieve transactions for

        Returns:
            transactions (list): A list of transaction objects for the provided period

        """
        period_ = self.get_period(year, month)
        if not period_:
            return []
        return period_.transactions

    @property
    def transactions(self):
        """Transactions.

        Returns:
            transaction (Transaction): Every available transaction

        """
        for period in self.periods:
            for transaction in period.transactions:
                yield transaction

    def get_current_period_transactions(self):
        """Retrieves transactions for the current period.

        Returns:
            transactions (list): A list of transaction object for the current period

        """
        url = f'{self.base_url}/sec/nl/sec/transactions'
        params = {'accountNumber': self.account_number,
                  'flushCache': True}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [CreditCardTransaction(data)
                for data in response.json()]
