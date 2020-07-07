from bybit import Bybit
from pprint import pprint
import time


bb = Bybit("", "")
pprint(bb.__dir__())

params = {"symbol": "BTCUSD", "interval": "1", "from": int(time.time() - 600)}
pprint(bb.query_kline(**params))
