import hmac
import hashlib
import logging
import requests
import time
import os
from urllib.parse import urlencode


ENDPOINT = "https://www.binance.com"

#if the API id data is stored as enviroment variable (recommended method)

# APIid = {'key': os.environ.get('BINANCE_KEY'),
#          'secret': os.environ.get('BINANCE_SECRET')}

# if you want to hard code the API data directly (not recommended)

APIid = {'key': "YOUR_API_KEY_HERE",
         'secret': "YOUR_API_SECRET_HERE"}


def request(method, path, params=None):
    """
    Makes a request to the public API
    :param method: request method
    :param path: URL path
    :param params: additional request parameters
    """
    resp = requests.request(method, ENDPOINT + path, params=params)
    data = resp.json()
    if "msg" in data:
        logging.error(data['msg'])
    return data


def signedRequest(method, path, params):
    """
    it makes an authenticated request to the Binance Rest API
    :param method: request method
    :param path: URL path
    :param params: request parameters
    """
    if "key" not in APIid or "secret" not in APIid:
        raise ValueError("Api key and secret must be set")

    query = urlencode(sorted(params.items()))
    query += "&timestamp={}".format(int(time.time() * 1000))
    secret = bytes(APIid["secret"].encode("utf-8"))
    signature = hmac.new(secret, query.encode("utf-8"), hashlib.sha256).hexdigest()
    query += "&signature={}".format(signature)
    resp = requests.request(method, ENDPOINT + path + "?" + query, headers={"X-MBX-APIKEY": APIid["key"]})
    data = resp.json()

    if "msg" in data:
        logging.error(data['msg'])
    return data


def formatNumber(x):
    """
    it formats the inpput to an 8 decimal format
    :param x: float
    """
    if isinstance(x, float):
        return "{:.8f}".format(x)
    else:
        return str(x)


def systemStatus():
    """
    Fetch system status.
    """
    data = signedRequest("GET", "/wapi/v3/systemStatus.html", {})
    return data['msg']

def ping():
    """
    Test connectivity to the Rest API.
    """
    params = {}
    data = request("GET", "/api/v3/ping", params)
    if data == {}:
        return True
    return False


def balances():
    """
    Get current balances for all symbols.
    """
    myBalances = []
    data = signedRequest("GET", "/api/v3/account", {})
    if 'msg' in data:
        raise ValueError("Error from exchange: {}".format(data['msg']))

    for balance in data['balances']:
        if float(balance['free']) != 0 or float(balance['locked']) != 0:
            myBalances.append(balance)
    return myBalances


def price(symbol=''):
    """
    Get latest prices for one or all symbols.
    :param symbol: currency symbol i.e.g BNBBTC, if left empty returns last price for all symbols
    """
    if symbol == "":
        params = {}
    else:
        params = {"symbol": symbol}
    data = request("GET", "/api/v3/ticker/price", params)
    return data

