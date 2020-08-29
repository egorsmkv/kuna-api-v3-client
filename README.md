# A Python client for the Kuna API v3

## Changes from the original client

* Update API to v3
* Only support Python 3, removed support of Python 2

## Examples

```python
import logging
from pprint import pprint
from dateutil.parser import isoparse

logging.basicConfig(level=logging.DEBUG)

access_key = '****'
secret_key = '****'

k = KunaAPI(access_key, secret_key)

pprint(k.get_server_time())

pprint(k.get_currencies())

pprint(k.get_markets())

pprint(k.get_recent_market_data(['btcusdt']))

pprint(k.get_recent_market_data(['zecuah', 'xemuah']))

pprint(k.get_order_book('btcusdt'))

pprint(k.get_fees())

pprint(k.get_account_info())

pprint(k.get_account_wallets())

pprint(k.get_account_orders())

pprint(k.get_account_orders('btcuah'))
pprint(k.get_account_orders('btcusdt'))

start_date_in_isoformat = '2020-08-28T20:56:35.450686Z'
start_milliseconds = int(isoparse(start_date_in_isoformat).timestamp() * 1000)
pprint(k.get_orders_history(start=start_milliseconds))

pprint(k.get_orders_history('btcuah'))
pprint(k.get_orders_history('btcusdt'))
```
