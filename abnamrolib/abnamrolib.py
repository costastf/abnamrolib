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
from datetime import date
from time import sleep

import backoff
import requests
from bankinterfaceslib import AccountAuthenticator, Comparable, Transaction, Contract
from selenium.common.exceptions import TimeoutException
from urllib3.util import parse_url

from abnamrolib.abnamrolibexceptions import AuthenticationFailed

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''19-07-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos", "Gareth Hawker"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''abnamrolib'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class AbnAmroAccountAuthenticator(AccountAuthenticator):
    """Extends the authenticator for an account."""

    def authenticate(self,  # pylint: disable=arguments-differ
                     account_number,
                     card_number,
                     pin_number,
                     url='https://www.abnamro.nl/portalserver/my-abnamro/my-overview/overview/index.html'):
        """Implements the business logic of authenticating to an account.

        Args:
            account_number (str): The number of an account to authenticate to
            card_number (str):  The card number of an account to authenticate to
            pin_number (str):  The pin number of an account to authenticate to
            url (str):  The url to authenticate to

        Returns:
            bool: True in success

        """
        try:
            self._logger.debug('Loading login page')
            self._driver.get(url)
            self._logger.debug('Accepting cookies')
            try:
                self._click_on("//*[text()='Save cookie-level']")
            except TimeoutException:
                self._logger.warning("Cookies window didn't pop up")
            self._logger.debug('Logging in')
            element = self._driver.find_element_by_xpath("//*[(@label='Identification code')]")
            element.click()
            self._driver.find_element_by_name('accountNumber').send_keys(account_number)
            self._driver.find_element_by_name('cardNumber').send_keys(card_number)
            self._driver.find_element_by_name('inputElement').send_keys(pin_number)
            self._driver.find_element_by_id('login-submit').click()
        except Exception:
            self._logger.exception('Error authenticating')
            raise AuthenticationFailed
        return True


class Customer:
    """Models the customer."""

    def __init__(self, data):
        self._data = data

    @property
    def appearance_type(self):
        """Appearence type."""
        return self._data.get('appearanceType')

    @property
    def bc_number(self):
        """BC Number."""
        return self._data.get('bcNumber')

    @property
    def interpay_name(self):
        """Interpay name."""
        return self._data.get('interpayName')


class Product:
    """Models the product."""

    def __init__(self, data):
        self._data = data

    @property
    def resource_type(self):
        """Resource type."""
        return self._data.get('resourceType')

    @property
    def id(self):  # pylint: disable=invalid-name
        """ID."""
        return self._data.get('id')

    @property
    def building_block_id(self):
        """Building block ID."""
        return self._data.get('buildingBlockId')

    @property
    def name(self):
        """Name."""
        return self._data.get('name')

    @property
    def group(self):
        """Product group."""
        return self._data.get('productGroup')

    @property
    def account_type(self):
        """Account type."""
        return self._data.get('accountType')

    @property
    def transfer_options(self):
        """Transfer options."""
        return self._data.get('transferOptions')


class Account(Comparable):
    """Models a contract."""

    def __init__(self, contract, data):
        super().__init__(data)
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.contract = contract
        self._data = data

    @property
    def _contract(self):
        """Number."""
        return self._data.get('contract', {})

    @property
    def _balance(self):
        """Balance."""
        return self._data.get('contract', {}).get('balance', {})

    @property
    def account_number(self):
        """Account number."""
        return self._contract.get('accountNumber', '')

    @property
    def resource_type(self):
        """Resource type."""
        return self._contract.get('resourceType')

    @property
    def id(self):  # pylint: disable=invalid-name
        """Id."""
        return self._contract.get('id')

    @property
    def number(self):
        """Number."""
        return self._contract.get('contractNumber')

    @property
    def chid(self):
        """CHID."""
        return self._contract.get('chid')

    @property
    def status(self):
        """Status."""
        return self._contract.get('status')

    @property
    def is_blocked(self):
        """Is blocked."""
        return self._contract.get('isBlocked')

    @property
    def concerning(self):
        """Concerning."""
        return self._contract.get('concerning')

    @property
    def amount(self):
        """Amount."""
        return self._balance.get('amount')

    @property
    def currency_code(self):
        """Currency code."""
        return self._balance.get('currencyCode')

    @property
    def product(self):
        """Product."""
        return Product(self._contract.get('product'))

    @property
    def customer(self):
        """Customer."""
        return Customer(self._contract.get('customer'))

    @property
    def parent_contract_id(self):
        """Parent Contract."""
        return self._data.get('parentContract', {}).get('id')

    @property
    def iban(self):
        """Iban."""
        return self.account_number

    def _get_transactions(self, params=None):
        if not self.iban:
            self._logger.error('Account does not expose transactions')
            return [], None
        url = f'{self.contract.base_url}/mutations/{self.iban}'
        headers = {'x-aab-serviceversion': 'v3'}
        response = self.contract.session.get(url, headers=headers, params=params)
        if not response.ok:
            self._logger.warning('Error retrieving transactions for account "%s" '
                                 'error message was "%s" with status code "%s"',
                                 self.account_number,
                                 response.text,
                                 response.status_code)
            return [], None
        mutations_list = response.json().get('mutationsList', {})
        last_mutation_key = mutations_list.get('lastMutationKey', None)
        transactions = [AccountTransaction(data.get('mutation'))
                        for data in mutations_list.get('mutations')]
        return transactions, last_mutation_key

    @property
    def transactions(self):
        """Transactions."""
        transactions, last_mutation_key = self._get_transactions()
        for transaction in transactions:
            yield transaction
        while last_mutation_key:
            params = {'lastMutationKey': last_mutation_key}
            transactions, last_mutation_key = self._get_transactions(params=params)
            for transaction in transactions:
                yield transaction

    def get_latest_transactions(self):
        """Retrieves the latest transactions.

        Returns:
            transactions (list): A list of transaction objects for the latest transactions

        """
        if not self.iban:
            self._logger.error('Account does not expose transactions')
            return []
        url = f'{self.contract.base_url}/mutations/{self.iban}'
        headers = {'x-aab-serviceversion': 'v3'}
        response = self.contract.session.get(url, headers=headers)
        if not response.ok:
            self._logger.warning('Error retrieving transactions for account "%s"', self.account_number)
            return []
        return [AccountTransaction(data.get('mutation'))
                for data in response.json().get('mutationsList', {}).get('mutations', [])]


class ForeignAccount(Comparable):
    """Models an account foreign to ABNAmro."""

    def __init__(self, contract, data):
        super().__init__(data)
        self._data = data
        self.contract = contract
        self._transactions_url = self._account.get('_links').get('transactions').get('href')

    @property
    def _account(self):
        return self._data.get('account')

    @property
    def account_number(self):
        """Account number."""
        return self._account.get('accountNumber')

    @property
    def iban(self):
        """iban."""
        return self._account.get('accountNumber')

    @property
    def transactions(self):
        """Transactions."""
        for transaction in self.get_latest_transactions():
            yield transaction

    def get_latest_transactions(self):
        """Get transactions from foreign account."""
        response = self.contract.session.get(self._transactions_url)
        if not response.ok:
            self._logger.warning('Error retrieving transactions for account "%s"', self.account_number)
            return []
        return [ForeignAccountTransaction(data.get('transaction', {})) for data in
                response.json().get('transactionList', {}).get('transactions', [{}])]


class MortgageAccount(Comparable):
    """Models a contract."""

    def __init__(self, contract, account):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.contract = contract
        self.account = account
        self._data = self._get_data()
        super().__init__(self._data)

    def _get_data(self):
        url = f'{self.contract.base_url}/nl/havikonline/service/api/v1/Hypotheek/{self.account.number}'
        response = self.contract.session.get(url)
        if not response.ok:
            self._logger.warning('Error retrieving data for mortgage account "%s"', self.account.number)
            return {}
        return response.json()

    @property
    def full_amount(self):
        """Full amount."""
        return self._data.get('leningdelen', [{}])[0].get('oorspronkelijkHypotheekbedrag')

    @property
    def remaining_amount(self):
        """Remaining amount."""
        return self._data.get('totaalResterendHypotheekbedrag')

    @property
    def remaining_months(self):
        """Remaining months."""
        return self._data.get('leningdelen', [{}])[0].get('restantLooptijdInMaanden')

    @property
    def monthly_amount(self):
        """Monthly amount."""
        return self._data.get('leningdelen', [{}])[0].get('brutoMaandlast')

    @property
    def mortgage_type(self):
        """Mortgage type."""
        return self._data.get('leningdelen', [{}])[0].get('hypotheeksoort')


class AccountTransaction(Transaction):
    """Models a banking transaction."""

    @property
    def mutation_code(self):
        """Mutation code."""
        return self._data.get('mutationCode')

    @property
    def description(self):
        """Description."""
        return ' '.join([self._clean_up(line.strip()) for line in self._data.get('descriptionLines', [])])

    @staticmethod
    def _timestamp_to_date(timestamp):
        if timestamp is None:
            return None
        return date.fromtimestamp(int(timestamp) / 1000)

    @property
    def transaction_date(self):
        """Transaction date."""
        return self._timestamp_to_date(self._data.get('transactionDate'))

    @property
    def value_date(self):
        """Value date."""
        return self._timestamp_to_date(self._data.get('valueDate'))

    @property
    def book_date(self):
        """Book date."""
        return self._timestamp_to_date(self._data.get('bookDate'))

    @property
    def balance_after_mutation(self):
        """Balance after mutation."""
        return self._data.get('balanceAfterMutation')

    @property
    def transaction_type(self):
        """Transaction type."""
        return self._data.get('debitCredit')

    @property
    def indicator_digital_invoice(self):
        """Indicator digital invoice."""
        return self._data.get('indicatorDigitalInvoice')

    @property
    def counter_account_number(self):
        """Counter account number."""
        return self._data.get('counterAccountNumber')

    @property
    def counter_account_type(self):
        """Counter account type."""
        return self._data.get('counterAccountType')

    @property
    def counter_account_name(self):
        """Counter account name."""
        return self._data.get('counterAccountName')

    @property
    def currency_iso_code(self):
        """Currency iso code."""
        return self._data.get('currencyIsoCode')

    @property
    def source_inquiry_number(self):
        """Source in inquiry number."""
        return self._data.get('sourceInquiryNumber')

    @property
    def account_number(self):
        """Account number."""
        return self._data.get('accountNumber')

    @property
    def account_number_type(self):
        """Account number type."""
        return self._data.get('accountNumberType')

    @property
    def transaction_timestamp(self):
        """Transaction timestamp."""
        return self._data.get('transactionTimestamp')

    @property
    def status_timestamp(self):
        """Status timestamp."""
        return self._data.get('statusTimestamp')

    @property
    def amount(self):
        """Amount."""
        return float(self._data.get('amount'))


class ForeignAccountTransaction(AccountTransaction):
    """Models a transaction foreign to ABNAmro."""

    @property
    def description(self):
        """Description."""
        return ' '.join([self._clean_up(line.strip()) for line in self._data.get('description', [])])

    @property
    def counter_account_name(self):
        """Counter account name."""
        return self._data.get('holder', {}).get('name', '')


class AccountContract(Contract):  # pylint: disable=too-many-instance-attributes
    """Models the service."""

    def __init__(self, account_number, card_number, pin_number):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.account_number = account_number
        self.card_number = card_number
        self.pin_number = pin_number
        self._base_url = 'https://www.abnamro.nl'
        self._accounts = None
        self.session = self._get_authenticated_session()

    @property
    def host(self):
        """Host."""
        return parse_url(self.base_url).host

    @property
    def base_url(self):
        """Base url."""
        return self._base_url

    def _get_authenticated_session(self):
        authenticator = AbnAmroAccountAuthenticator()
        authenticator.authenticate(self.account_number, self.card_number, self.pin_number)
        sleep(2)  # give time to the headless browser to execute all the code to get all the cookies
        session = authenticator.get_authenticated_session()
        session.headers.update({'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                               'Gecko/20100101 Firefox/67.0')})
        self.original_get = session.get
        session.get = self._patched_get
        return session

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException)
    def _patched_get(self, *args, **kwargs):
        url = args[0]
        self._logger.debug('Using patched get request for url %s', url)
        try:
            response = self.original_get(*args, **kwargs)
            if not url.startswith(self.base_url):
                self._logger.debug('Url "%s" requested is not from abn amro account api, passing through', url)
                return response
            if response.status_code == 401:
                self._logger.info('Expired session detected, trying to re authenticate!')
                self.session = self._get_authenticated_session()
                response = self.original_get(*args, **kwargs)
                self._logger.info('Successfully re authenticated!')
        except requests.exceptions.ConnectionError:
            self._logger.info('Connection reset detected, trying to re authenticate!')
            self.session = self._get_authenticated_session()
            response = self.original_get(*args, **kwargs)
        return response

    @property
    def accounts(self):
        """Accounts."""
        if self._accounts is None:
            url = f'{self.base_url}/contracts'
            headers = {'x-aab-serviceversion': 'v2'}
            response = self.session.get(url, headers=headers)
            if not response.ok:
                self._logger.warning('Error retrieving accounts for contract')
                return []
            self._accounts = [Account(self, data) for data in response.json().get('contractList', [])]
            self._accounts.extend(self._get_foreign_accounts())
        return self._accounts

    def _get_foreign_accounts(self):
        url = f'{self.base_url}/mul/accounts/v1'
        response = self.session.get(url)
        if response.status_code == 403:
            self._logger.info('No foreign accounts enabled on this account')
            return []
        if not response.ok:
            self._logger.warning('Could not get info on foreign accounts')
            return []
        return [ForeignAccount(self, data) for data in response.json().get('accounts')]

    def get_account(self, id_):
        """Retrieves the account by the provided id.

        Args:
            id_ (str): The iban to retrieve the account for

        Returns:
            account (Account): The account if it exists, None otherwise.

        """
        return self.get_account_by_iban(id_)

    def get_account_by_iban(self, iban):
        """Retrieves an account object by the provided IBAN.

        Args:
            iban (str): The iban to match the account with

        Returns:
            account (Account): Account object on match, None otherwise

        """
        return next((account for account in self.accounts
                     if account.account_number.lower() == iban.lower()), None)

    def get_mortgage_account(self, account_number):
        """Retrieves a mortgage account by account number.

        Args:
            account_number (str): The account number of the mortgage account to match

        Returns:
            account (MortgageAccount): A MortgageAccount object on success, None otherwise

        """
        return next((MortgageAccount(self, account)
                     for account in self.accounts
                     if all([account.product.group == 'MORTGAGE',
                             account.number == account_number])), None)
