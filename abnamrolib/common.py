#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: common.py
#
# Copyright 2019 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
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
Main code for common.

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging
from dataclasses import dataclass

from requests import Session

from .abnamrolibexceptions import InvalidCookies

__author__ = '''Costas Tyfoxylos <costas.tyf@gmail.com>'''
__docformat__ = '''google'''
__date__ = '''09-12-2019'''
__copyright__ = '''Copyright 2019, Costas Tyfoxylos'''
__credits__ = ["Costas Tyfoxylos"]
__license__ = '''MIT'''
__maintainer__ = '''Costas Tyfoxylos'''
__email__ = '''<costas.tyf@gmail.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''common'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


@dataclass
class Cookie:
    """Models a cookie."""

    domain: str
    flag: bool
    path: str
    secure: bool
    expiry: int
    name: str
    value: str

    def to_dict(self):
        """Returns the cookie as a dictionary.

        Returns:
            cookie (dict): The dictionary with the required values of the cookie

        """
        return {key: getattr(self, key) for key in ('domain', 'name', 'value', 'path')}


class CookieAuthenticator:  # pylint: disable=too-few-public-methods
    """Models the authenticator with a provided cookie."""

    def __init__(self, cookie_file):
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')
        self.session = self._get_authenticated_session(cookie_file)

    def _get_authenticated_session(self, cookie_file):
        session = Session()
        try:
            cfile = open(cookie_file, 'rb')
        except FileNotFoundError:
            message = 'Could not open cookies file, either file does not exist or no read access.'
            raise InvalidCookies(message)
        session = self._load_text_cookies(session, cfile)
        session.headers.update({'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:67.0)'
                                               'Gecko/20100101 Firefox/67.0')})
        return session

    def _load_text_cookies(self, session, cookies_file):
        try:
            text = cookies_file.read().decode('utf-8')
            cookie_entries = [line.strip().split() for line in text.splitlines()
                              if line and not line.strip().startswith('#')]
            cookies = [Cookie(*data) for data in cookie_entries if len(data) == 7]
            for cookie in cookies:
                session.cookies.set(**cookie.to_dict())
        except Exception:
            self._logger.exception('Things broke...')
            message = 'Could not properly load cookie text file.'
            raise InvalidCookies(message)
        return session
