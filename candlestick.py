import copy
import json
import requests


class Candle(object):
    URI = 'https://api.bitfinex.com/v2/candles/trade:{0}:t{1}/last'

    def __init__(self):
        self.mts = 0
        self.open = 0.0
        self.close = 0.0
        self.high = 0.0
        self.low = 0.0
        self.volume = 0.0

    @property
    def hl2(self):
        return (self.high + self.low) / 2

    @property
    def hlc3(self):
        return (self.high + self.low + self.close) / 3

    @property
    def ohlc4(self):
        return (self.open + self.high + self.low + self.close) / 4

    def to_json(self):
        return str(self.__dict__).replace('\'', '"')

    def to_sheet(self):
        return {
            'mts': [self.mts],
            'open': [self.open],
            'close': [self.close],
            'high': [self.high],
            'low': [self.low],
            'volume': [self.volume],
            'hl2': [self.hl2],
            'hlc3': [self.hlc3],
            'ohlc4': [self.ohlc4]
        }

    @staticmethod
    def from_json(json_string):
        candle = Candle()
        data = json.loads(json_string)
        if isinstance(data, list):
            candle.mts = int(data[0])
            candle.open = float(data[1])
            candle.close = float(data[2])
            candle.high = float(data[3])
            candle.low = float(data[4])
            candle.volume = float(data[5])
        elif isinstance(data, dict):
            candle.__dict__ = data
        return candle

    @staticmethod
    def last_candle(trade_pair, time_frame):
        uri = Candle.URI.format(time_frame, trade_pair)
        response = requests.get(uri)
        return Candle.from_json(response.content)


class CandleHistory(object):
    URI: str = "https://api.bitfinex.com/v2/candles/trade:{0}:t{1}/hist?limit={2}"

    def __init__(self, trade_pair, time_frame, size):
        self._trade_pair = trade_pair
        self._time_frame = time_frame
        self._size = size
        self._candle_list = []
        self.update()

    @property
    def candles(self):
        return copy.deepcopy(self._candle_list)

    @candles.setter
    def candles(self, value):
        self._candle_list = value

    @property
    def size(self):
        return self._size

    @property
    def trade_pair(self):
        return self._trade_pair

    @property
    def time_frame(self):
        return self._time_frame

    def update(self):
        uri = CandleHistory.URI.format(self._time_frame, self._trade_pair, self._size)
        response = requests.get(uri)
        data = json.loads(response.content)
        self._candle_list = []
        for row in data:
            candle = Candle()
            candle.mts = int(row[0])
            candle.open = float(row[1])
            candle.close = float(row[2])
            candle.high = float(row[3])
            candle.low = float(row[4])
            candle.volume = float(row[5])
            self._candle_list.append(candle)
        self._candle_list.reverse()

    def to_sheet(self):
        mts_list = []
        open_list = []
        close_list = []
        high_list = []
        low_list = []
        volume_list = []
        hl2_list = []
        hlc3_list = []
        ohlc4_list = []

        for candle in self._candle_list:
            mts_list.append(candle.mts)
            open_list.append(candle.open)
            close_list.append(candle.close)
            high_list.append(candle.high)
            low_list.append(candle.low)
            volume_list.append(candle.volume)
            hl2_list.append(candle.hl2)
            hlc3_list.append(candle.hlc3)
            ohlc4_list.append(candle.ohlc4)

        return {
            'mts': mts_list,
            'open': open_list,
            'close': close_list,
            'high': high_list,
            'low': low_list,
            'volume': volume_list,
            'hl2': hl2_list,
            'hlc3': hlc3_list,
            'ohlc4': ohlc4_list
        }


class Ticker(object):
    URI = 'https://api.bitfinex.com/v2/ticker/t{0}'

    def __init__(self):
        self.bid = 0.0
        self.bid_size = 0.0
        self.ask = 0.0
        self.ask_size = 0.0
        self.daily_change = 0.0
        self.daily_change_perc = 0.0
        self.last_price = 0.0
        self.volume = 0.0
        self.high = 0.0
        self.low = 0.0

    def to_json(self):
        return str(self.__dict__).replace('\'', '"')

    def to_sheet(self):
        return {
            'bid': [self.bid],
            'bid_size': [self.bid_size],
            'ask': [self.ask],
            'ask_size': [self.ask_size],
            'daily_change': [self.daily_change],
            'daily_change_perc': [self.daily_change_perc],
            'last_price': [self.last_price],
            'volume': [self.volume],
            'high': [self.high],
            'low': [self.low]
        }

    @staticmethod
    def from_json(json_string):
        ticker = Ticker()
        data = json.loads(json_string)
        if isinstance(data, list):
            ticker.bid = float(data[0])
            ticker.bid_size = float(data[1])
            ticker.ask = float(data[2])
            ticker.ask_size = float(data[3])
            ticker.daily_change = float(data[4])
            ticker.daily_change_perc = float(data[5])
            ticker.last_price = float(data[6])
            ticker.volume = float(data[7])
            ticker.high = float(data[8])
            ticker.low = float(data[9])
        elif isinstance(data, dict):
            ticker.__dict__ = data
        return ticker

    @staticmethod
    def last_ticker(trade_pair):
        ticker_uri = Ticker.URI.format(trade_pair)
        response = requests.get(ticker_uri)
        return Ticker.from_json(response.content)


def main():
    pass


if __name__ == '__main__':
    main()
