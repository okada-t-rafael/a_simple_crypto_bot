import base64
import hashlib
import hmac
import json
import requests
from datetime import datetime
from enum import Enum


class OrderSide(Enum):
    BUY = 'buy'
    SELL = 'sell'


class OrderType(Enum):
    EXCHANGE_MARKET = 'exchange market'
    EXCHANGE_LIMIT = 'exchange limit'
    EXCHANGE_STOP = 'exchange stop'
    EXCHANGE_TRAILING_STOP = 'exchange trailing stop'
    MARGIN_MARKET = 'market'
    MARGIN_LIMIT = 'limit'
    MARGIN_STOP = 'stop'
    MARGIN_TRAILING_STOP = 'trailing stop'


class GenericRequest(object):
    def __init__(self):
        self.request = ''
        self.nonce = ''
        self.options = []


class Balance(object):
    def __init__(self):
        self.usd = 0.0
        self.available_usd = 0.0


class BalanceResponseItem(object):
    def __init__(self):
        self.type = ''
        self.currency = ''
        self.amount = ''
        self.available = ''


class BalancesRequest(GenericRequest):
    def __init__(self, nonce):
        super().__init__()
        self.nonce = nonce
        self.request = '/v1/balances'


class BalanceResponse(object):
    def __init__(self):
        self.total_usd = 0.0
        self.total_available_usd = 0.0
        self.trading_balance = Balance()
        self.deposit_balance = Balance()
        self.exchange_balance = Balance()

    @staticmethod
    def from_json(json_string):
        items = []
        data = json.loads(json_string)
        for row in data:
            item = BalanceResponseItem()
            item.__dict__ = row
            items.append(item)
        balance_response = BalanceResponse()
        balances = {
            'trading': balance_response.trading_balance,
            'deposit': balance_response.deposit_balance,
            'exchange': balance_response.exchange_balance
        }
        for item in items:
            if item.type == 'trading':  # Little hack to only consider MARGIN's balance. TODO Do it in a better way.
                current_balance = balances.get(item.type)
                if item.currency == 'usd':
                    current_balance.available_usd = float(item.available)
                    balance_response.total_available_usd += float(item.available)
                    current_balance.usd += float(item.amount)
                    balance_response.total_usd += float(item.amount)
        return balance_response


class OrderRequest(GenericRequest):
    def __init__(self, nonce, order_id):
        super().__init__()
        self.nonce = nonce
        self.request = '/v1/order/status'
        self.order_id = order_id


class OrderResponse(object):
    def __init__(self):
        self.id = ''
        self.cid = ''
        self.cid_date = ''
        self.gid = ''
        self.symbol = ''
        self.exchange = ''
        self.price = ''
        self.avg_execution_price = ''
        self.side = ''
        self.type = ''
        self.timestamp = ''
        self.is_live = ''
        self.is_cancelled = ''
        self.is_hidden = ''
        self.oco_order = ''
        self.was_forced = ''
        self.executed_amount = ''
        self.remaining_amount = ''
        self.original_amount = ''
        self.src = ''

    @staticmethod
    def from_json(json_string):
        order = OrderResponse()
        order.__dict__ = json.loads(json_string)
        return order


class NewOrderRequest(GenericRequest):
    def __init__(self, nonce, order_symbol, amount, price, order_side, order_type):
        super().__init__()
        self.nonce = nonce
        self.request = '/v1/order/new'
        self.symbol = order_symbol
        self.amount = str(amount)
        self.price = str(price)
        self.side = order_side.value
        self.type = order_type.value


class NewOrderResponse(OrderResponse):
    def __init__(self):
        super().__init__()
        self.order_id = ''

    @staticmethod
    def response_from_json(json_string):
        order = NewOrderResponse()
        order.__dict__ = json.loads(json_string)
        return order


class ActiveOrdersRequest(GenericRequest):
    def __init__(self, nonce):
        super().__init__()
        self.nonce = nonce
        self.request = '/v1/orders'


class ActiveOrdersResponse(object):
    def __init__(self):
        self.orders_list = []

    @staticmethod
    def from_json(json_string):
        active_orders_response = ActiveOrdersResponse()
        data = json.loads(json_string)
        for row in data:
            order = OrderResponse()
            order.__dict__ = row
            active_orders_response.orders_list.append(order)
        return active_orders_response


class CancelOrderRequest(GenericRequest):
    def __init__(self, nonce, order_id):
        super().__init__()
        self.nonce = nonce
        self.order_id = order_id
        self.request = '/v1/order/cancel'


class CancelOrderResponse(OrderResponse):
    def __init__(self):
        super().__init__()

    @staticmethod
    def from_json(json_string):
        order = CancelOrderResponse()
        order.__dict__ = json.loads(json_string)
        return order


class PositionResponse(object):
    def __init__(self):
        self.id = ''
        self.symbol = ''
        self.base = ''
        self.amount = ''
        self.timestamp = ''
        self.swap = ''
        self.pl = ''

    @staticmethod
    def from_json(json_string):
        position = PositionResponse()
        position.__dict__ = json.loads(json_string)
        return position


class ActivePositionsRequest(GenericRequest):
    def __init__(self, nonce):
        super().__init__()
        self.nonce = nonce
        self.request = '/v1/positions'


class ActivePositionsResponse(object):
    def __init__(self):
        self.positions_list = []

    @staticmethod
    def from_json(json_string):
        active_positions_response = ActivePositionsResponse()
        data = json.loads(json_string)
        for row in data:
            position = PositionResponse()
            position.__dict__ = row
            active_positions_response.positions_list.append(position)
        return active_positions_response


class ExchangeApi(object):
    def __init__(self, api_config):
        self._epoch = datetime(1970, 1, 1)
        self._nonce = 0
        self._hash_maker = hmac.new(key=str(api_config[1]).encode('utf-8'), digestmod=hashlib.sha384)
        self._key = api_config[0]

    @property
    def nonce(self):
        if self._nonce == 0:
            self._nonce = int((datetime.now() - self._epoch).total_seconds()) * 1000
        else:
            self._nonce += 1
        return str(self._nonce)

    def send_request(self, request, method):
        json_string = json.dumps(request.__dict__)
        json_string64 = base64.b64encode(json_string.encode('utf-8'))
        temp_hash_maker = self._hash_maker.copy()
        temp_hash_maker.update(json_string64)
        signature = temp_hash_maker.hexdigest()
        url = 'https://api.bitfinex.com' + request.request
        headers = {'X-BFX-APIKEY': self._key,
                   'X-BFX-PAYLOAD': json_string64,
                   'X-BFX-SIGNATURE': signature,
                   'Content-Type': 'application/json'}
        try:
            response = requests.request(method, url, headers=headers)
        except Exception as e:
            raise e
        return response

    def get_balances(self):
        request = BalancesRequest(self.nonce)
        response = self.send_request(request, 'POST')
        # print(response.text)
        return BalanceResponse.from_json(response.text)

    def get_order(self, order_id):
        request = OrderRequest(self.nonce, order_id)
        response = self.send_request(request, 'POST')
        # print(response.text)
        return OrderResponse.from_json(response.text)

    def get_active_orders(self):
        request = ActiveOrdersRequest(self.nonce)
        response = self.send_request(request, 'POST')
        # print(response.text)
        return ActiveOrdersResponse.from_json(response.text)

    def execute_order(self, order_symbol, amount, price, order_side, order_type):
        request = NewOrderRequest(self.nonce, order_symbol, amount, price, order_side, order_type)
        response = self.send_request(request, 'POST')
        # print(response.text)
        return NewOrderResponse.from_json(response.text)

    def get_active_positions(self):
        request = ActivePositionsRequest(self.nonce)
        response = self.send_request(request, 'POST')
        # print(response.text)
        return ActivePositionsResponse.from_json(response.text)


def main():
    pass


if __name__ == '__main__':
    main()
