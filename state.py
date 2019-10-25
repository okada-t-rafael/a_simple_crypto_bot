import candlestick as cs
import config
import sys
from exchange import ExchangeApi, OrderType

CONFIG_FILE = 'config.ini'


class State(object):
    def __init__(self, trade_pair, time_frame):
        self._api = None
        self.balance = None
        self.trade_pair = trade_pair
        self.time_frame = time_frame
        self.position = None
        self.mts = 0

        self.curr_bid_price = 0.0
        self.curr_ask_price = 0.0
        self.last_price = 0.0
        self.peak_price = 0.0
        self.bottom_price = sys.maxsize
        self.curr_high_price = 0.0
        self.curr_low_price = 0.0
        self.curr_open_price = 0.0
        self.daily_volume = 0.0

        self.pl_perc = 0
        self.pl_high_perc = 0

        self.setup_api()
        self.update()

    def setup_api(self):
        self._api = ExchangeApi(config.rescue(CONFIG_FILE, self.trade_pair))

    def update(self):
        self.balance = self._api.get_balances()
        self.position = self.check_position()

        ticker = cs.Ticker.last_ticker(self.trade_pair)
        candle = cs.Candle.last_candle(self.trade_pair, self.time_frame)

        self.curr_bid_price = ticker.bid
        self.curr_ask_price = ticker.ask
        self.last_price = ticker.last_price
        self.mts = candle.mts
        self.curr_high_price = candle.high
        self.curr_low_price = candle.low
        self.curr_open_price = candle.open
        self.daily_volume = ticker.volume

        if self.last_price > self.peak_price:
            self.peak_price = self.last_price

        if self.curr_high_price > self.peak_price:
            self.peak_price = self.curr_high_price

        if self.last_price < self.bottom_price:
            self.bottom_price = self.last_price

        if self.curr_low_price < self.bottom_price:
            self.bottom_price = self.curr_low_price

        if self.position:
            base = float(self.position.base)
            amount = abs(float(self.position.amount))
            pl = float(self.position.pl)
            initial = base * amount
            self.pl_perc = pl / initial
            if self.pl_high_perc < self.pl_perc:
                self.pl_high_perc = self.pl_perc

    def check_position(self):
        positions = self._api.get_active_positions()
        position = None
        for p in positions.positions_list:
            if p.symbol == self.trade_pair.lower():
                position = p
        return position

    def adjust_position(self, amount, side):
        self.peak_price = self.last_price
        self.bottom_price = self.last_price
        self._api.execute_order(self.trade_pair, amount, self.last_price, side, OrderType.MARGIN_MARKET)

    def to_sheet(self):
        mts_list = []
        curr_bid_price_list = []
        curr_ask_price_list = []
        last_price_list = []
        peak_price_list = []
        bottom_price_list = []
        curr_high_price_list = []
        curr_low_price_list = []
        daily_volume_list = []
        is_holding_position_list = []
        total_available_usd_list = []

        mts_list.append(self.mts)
        curr_bid_price_list.append(self.curr_bid_price)
        curr_ask_price_list.append(self.curr_ask_price)
        last_price_list.append(self.last_price)
        peak_price_list.append(self.peak_price)
        bottom_price_list.append(self.bottom_price)
        curr_high_price_list.append(self.curr_high_price)
        curr_low_price_list.append(self.curr_low_price)
        daily_volume_list.append(self.daily_volume)
        is_holding_position_list.append(self.position)
        total_available_usd_list.append(self.balance.total_available_usd)

        return {
            'mts': mts_list,
            'curr_bid_price': curr_bid_price_list,
            'curr_ask_price': curr_ask_price_list,
            'last_price': last_price_list,
            'peak_price': peak_price_list,
            'bottom_price': bottom_price_list,
            'curr_high_price': curr_high_price_list,
            'curr_low_price': curr_low_price_list,
            'is_holding_position': is_holding_position_list,
            'total_available_usd': total_available_usd_list
        }


def main():
    pass


if __name__ == '__main__':
    main()
