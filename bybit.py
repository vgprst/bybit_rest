from typing import Dict
from functools import partial
import hmac
import time
import requests


class Bybit:
    """Bybit inverse rest api"""
    _base = "https://api.bybit.com"

    # https://bybit-exchange.github.io/docs/inverse/#t-marketdata
    _public = {
        "orderbook": "/v2/public/orderBook/L2",
        "query_kline": "/v2/public/kline/list",
        "ticker": "/v2/public/tickers",
        "trading_records": "/v2/public/trading-records",
        "query_symbol": "/v2/public/symbols",
        "liquidated_orders": "/v2/public/liq-records",
        "query_mark_price_kline": "/v2/public/mark-price-kline"
    }

    # https://bybit-exchange.github.io/docs/inverse/#t-accountdata
    _private = {
        "get": {
            "get_active_order": "/open-api/order/list",
            "get_conditional_order": "/open-api/stop-order/list",
            "query_active_order": "/v2/private/order",
            "query_conditional_order": "/v2/private/stop-order",
            "my_position": "/v2/private/position/list",
            "user_leverage": "/user/leverage",
            "user_trade_records": "/v2/private/execution/list",
            "closed_profit_and_loss": "/v2/private/trade/closed-pnl/list",
            "get_wallet_balance": "/v2/private/wallet/balance",
            "wallet_fund_records": "/open-api/wallet/fund/records",
            "withdraw_records": "/open-api/wallet/withdraw/list",
            "get_risk_limit": "/open-api/wallet/risk-limit/list",
            "api_key_info": "/open-api/api-key"
        },
        "post": {
            "place_active_order": "/v2/private/order/create",
            "cancel_active_order": "/v2/private/order/cancel",
            "cancel_all_active_order": "/v2/private/order/cancelAll",
            "place_conditional_order": "/open-api/stop-order/create",
            "cancel_conditional_order": "/open-api/stop-order/cancel",
            "cancel_all_conditional_order": "/v2/private/stop-order/cancelAll",
            "replace_active_order": "/open-api/order/replace",
            "replace_conditional_order": "/open-api/stop-order/replace",
            "change_margin": "/position/change-position-margin",
            "set_trading_stop": "/open-api/position/trading-stop",
            "change_user_leverage": "/user/leverage/save",
            "set_risk_limit": "/open-api/wallet/risk-limit"
        }
    }

    def __init__(self, api_key: str, api_secret: str) -> None:
        self._key = api_key
        self._secret = api_secret
        self._define_api()

    def _define_api(self):
        # public
        for name, url_tail in self._public.items():
            setattr(self, name, partial(self._request_public, url_tail))
        # private
        for req_type, methods in self._private.items():
            for name, url_tail in methods.items():
                setattr(self, name, partial(self._request_private, req_type, url_tail))

    # request
    def _request_public(self, url_tail: str, **params) -> Dict:
        return requests.get(self._base + url_tail, params).json()

    def _request_private(self, req_type: str, url_tail: str, **params) -> Dict:
        self._set_commons(params)
        return getattr(requests, req_type)(self._base + url_tail, params).json()

    # misc
    @staticmethod
    def _get_signature(secret: str, req_params: dict):
        """ https://github.com/bybit-exchange/api-connectors/blob/master/encryption_example/Encryption.py """
        val = '&'.join([f"{k}={v}" for k, v in sorted(req_params.items()) if (k != 'sign') and (v is not None)])
        return str(hmac.new(bytes(secret, "utf-8"), bytes(val, "utf-8"), digestmod="sha256").hexdigest())

    def _set_commons(self, params: Dict) -> None:
        params["timestamp"] = int(time.time() * 1000)
        params["api_key"] = self._key
        params["sign"] = self._get_signature(self._secret, params)
