import hashlib
import hmac
import json
import time
import logging

import requests

# Based on Dmytro Litvinov's client for the Kuna API v2, but rewritten to use the Kuna API v3
# Original client's repository: https://github.com/DmytroLitvinov/kuna
__author__ = 'Dmytro Litvinov'
__email__ = 'litvinov.do.it@gmail.com'
__version__ = '0.3.3'

logger = logging.getLogger('kuna_api')

API_VERSION = '3'
KUNA_API_URL_PREFIX = 'v{}'.format(API_VERSION)
KUNA_API_BASEURL = 'https://api.kuna.io/{}/'.format(KUNA_API_URL_PREFIX)


class KunaAPI:
    def __init__(self, access_key: str = None, secret_key: str = None):

        self.access_key = access_key
        self.secret_key = secret_key

    def get_server_time(self):
        """
        Get the server time from server.
        :return: unix timestamp
        """
        return self.request('timestamp')

    def get_currencies(self):
        """
        Get the list of available currencies.
        :return: the list
        """
        return self.request('currencies')

    def get_markets(self):
        """
        Get the list of available markets.
        :return: the list
        """
        return self.request('markets')

    def get_recent_market_data(self, markets: list):
        """
        Get recent market data from server.
        :param markets:
        :return:
        """
        args = {
            'symbols': ','.join(markets)
        }
        return self.request('tickers', args=args)

    def get_order_book(self, symbol):
        """
        Get order book data from server.
        :param symbol:
        :return:
        """
        return self.request('book/' + symbol)

    def get_fees(self):
        """
        Get the list of fees.
        :return: the list
        """
        return self.request('fees')

    def get_account_info(self):
        """
        Get the account info.
        :return: the account info
        """
        return self.request('auth/me', method='POST', is_user_method=True)

    def get_account_wallets(self):
        """
        Get the account wallets.
        :return: the account wallets
        """
        return self.request('auth/r/wallets', method='POST', is_user_method=True)

    def get_account_orders(self, market=None):
        """
        Active User Orders.
        This is a User method.
        :return:
        """

        url = 'auth/r/orders'
        if market:
            url = f'auth/r/orders/{market}'

        return self.request(url, method='POST', is_user_method=True)

    def get_orders_history(self, market: str = None, start: int = None, end: int = None, limit: int = 25, sort: int = 1):
        """
        User trade history
        This is a User method.
        :param sort:
        :param limit:
        :param end:
        :param start:
        :param market:
        :return:
        """

        url = 'auth/r/orders/hist'
        if market:
            url = f'auth/r/orders/{market}/hist'

        args = {
            'limit': limit,
            'sort': sort,
        }

        if start:
            args['start'] = start

        if end:
            args['start'] = end

        return self.request(url, method='POST', args=args, is_user_method=True)

    def request(self, path, args=None, method='GET', is_user_method=False):
        """
        Fetches the given path in the Kuna API.
        We translate args to a valid query string. If post_args is
        given, we send a POST request to the given path with the given
        arguments.
        :param path:
        :param args:
        :param method:
        :param is_user_method:
        :return:
        """
        if args is None:
            args = dict()

        headers = dict()

        try:
            if is_user_method:
                headers['accept'] = 'application/json'
                headers['content-type'] = 'application/json'
                headers['kun-apikey'] = self.access_key
                headers['kun-nonce'] = str(int(time.time() * 1000))
                headers['kun-signature'] = self._generate_signature(headers['kun-nonce'], path, args)

                response = requests.request(method, KUNA_API_BASEURL + path, json=args, headers=headers)

                logger.debug('Headers of the request:')
                logger.debug(headers)
                logger.debug('Response headers of the request:')
                logger.debug(response.headers)
                logger.debug('Body of the request: ' + json.dumps(args))
                logger.debug('Response of the request: ' + json.dumps(response.json()))
            else:
                response = requests.request(
                    method,
                    KUNA_API_BASEURL + path,
                    headers=headers,
                    params=args)
        except requests.RequestException as e:
            response = json.loads(e.read())
            raise APIError(response)

        result = response.json()

        if result and isinstance(result, dict) and result.get('error'):
            raise APIError(result)
        elif response.status_code not in [200, 201, 202]:
            raise APIError(response.reason)

        return result

    def _generate_signature(self, nonce, path, args):
        """
        Signature is generated by an algorithm HEX(HMAC-SHA384("HTTP-verb|URI|params", secret_key))
        :param nonce:
        :param path:
        :param args:
        :return:
        """
        body = json.dumps(args)
        uri = '/' + KUNA_API_URL_PREFIX + '/' + path
        msg = uri + nonce + body  # "{apiPath} + {nonce} + JSON({body})"

        # HMAC can only handle ascii (byte) strings
        # https://bugs.python.org/issue5285
        key = self.secret_key.encode('ascii')
        msg = msg.encode('ascii')

        m = hmac.new(key, digestmod=hashlib.sha384)
        m.update(msg)

        return m.hexdigest()


class APIError(Exception):
    def __init__(self, result):

        try:
            self.message = result["error"]["message"]
            self.code = result["error"].get("code")
        except:
            self.message = result

        Exception.__init__(self, self.message)
