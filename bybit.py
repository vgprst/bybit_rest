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
        "query_mark_price_kline": "/v2/public/mark-price-kline",
        "query_index_price_kline": "/v2/public/index-price-kline",
        "query_premium_index_kline": "/v2/public/premium-index-kline",
        "open_interest": "/v2/public/open-interest",
        "latest_big_deal": "/v2/public/big-deal",
        "long_short_ratio": "/v2/public/account-ratio",
        "get_the_last_funding_late": "/v2/public/funding/prev-funding-rate",
        "get_risk_limit": "/v2/public/risk-limit/list",

        # https://bybit-exchange.github.io/docs/inverse/#t-api
        "server_time": "/v2/public/time",
        "announcement": "/v2/public/announcement"
    }

    # https://bybit-exchange.github.io/docs/inverse/#t-accountdata
    _private = {
        "get":
            {
                "get_active_order": "/v2/private/order/list",
                "get_conditional_order": "/v2/private/stop-order/list",
                "query_active_order": "/v2/private/order",
                "query_conditional_order": "/v2/private/stop-order",

                "my_position": "/v2/private/position/list",
                "user_trade_records": "/v2/private/execution/list",
                "closed_profit_and_loss": "/v2/private/trade/closed-pnl/list",
                "my_last_funding_fee": "/v2/private/funding/prev-funding",
                "predicted_funding": "/v2/private/funding/predicted-funding",
                "api_key_info": "/v2/private/account/api-key",
                "lcp_info": "/v2/private/account/lcp",

                # https://bybit-exchange.github.io/docs/inverse/#t-wallet
                "get_wallet_balance": "/v2/private/wallet/balance",
                "wallet_fund_records": "/v2/private/wallet/fund/records",
                "withdraw_records": "/v2/private/wallet/withdraw/list",
                "asset_exchange_record": "/v2/private/exchange-order/list"
            },
        "post":
            {
                "place_active_order": "/v2/private/order/create",
                "cancel_active_order": "/v2/private/order/cancel",
                "cancel_all_active_order": "/v2/private/order/cancelAll",
                "replace_active_order": "/v2/private/order/replace",
                "place_conditional_order": "/v2/private/stop-order/create",
                "cancel_conditional_order": "/v2/private/stop-order/cancel",
                "cancel_all_conditional_order": "/v2/private/stop-order/cancelAll",
                "replace_conditional_order": "/v2/private/stop-order/replace",

                "change_margin": "/v2/private/position/change-position-margin",
                "set_trading_stop": "/v2/private/position/trading-stop",
                "set_leverage": "/v2/private/position/leverage/save",

                "tpsl_switch_mode": "/v2/private/tpsl/switch-mode",
                "isolated_margin_switch": "/v2/private/position/switch-isolated",
                "set_risk_limit": "/v2/private/position/risk-limit"
            }
    }

    def __init__(self, api_key: str, api_secret: str) -> None:
        self._key = api_key
        self._secret = api_secret
        self._define_api()

    def _define_api(self) -> None:
        self._define_publics()
        self._define_privates()

    def _define_publics(self) -> None:
        for name, url_tail in self._public.items():
            setattr(self, name, partial(self._request_public, url_tail))

    def _define_privates(self) -> None:
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
    def _get_signature(secret: str, req_params: Dict) -> str:
        """ https://github.com/bybit-exchange/api-connectors/blob/master/encryption_example/Encryption.py """
        val = '&'.join([f"{k}={v}" for k, v in sorted(req_params.items()) if (k != 'sign') and (v is not None)])
        return str(hmac.new(bytes(secret, "utf-8"), bytes(val, "utf-8"), digestmod="sha256").hexdigest())

    def _set_commons(self, params: Dict) -> None:
        params["timestamp"] = int(time.time() * 1000)
        params["api_key"] = self._key
        params["sign"] = self._get_signature(self._secret, params)
