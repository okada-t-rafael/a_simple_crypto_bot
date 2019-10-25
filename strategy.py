import pandas as pd
import indicator


class Strategy(object):
    def to_sheet(self):
        raise NotImplementedError()

    def think(self, history, response):
        raise NotImplementedError()


class StrategyOne(Strategy):
    def __init__(self):
        self._f1 = 91
        self._f2 = 198
        self._df = None

    def to_sheet(self):
        return self._df.to_dict('list')

    def think(self, history, response):
        size = response
        code = 0

        fast_ema_indicator = indicator.EMAIndicator(self._f1)
        fast_ema_indicator.calculate(history, size)
        fast_ema = pd.DataFrame(fast_ema_indicator.results_to_sheet())
        fast_ema.rename(columns={'ema': 'fast_ema'}, inplace=True)

        slow_ema_indicator = indicator.EMAIndicator(self._f2)
        slow_ema_indicator.calculate(history, size)
        slow_long = pd.DataFrame(slow_ema_indicator.results_to_sheet())
        slow_long.rename(columns={'ema': 'slow_ema'}, inplace=True)

        self._df = pd.merge(fast_ema, slow_long, on='mts')

        if self._df['fast_ema'].iloc[-2] < self._df['slow_ema'].iloc[-2]:
            code = -50
            if self._df['fast_ema'].iloc[-1] > self._df['slow_ema'].iloc[-1]:
                code = 100
        elif self._df['fast_ema'].iloc[-2] > self._df['slow_ema'].iloc[-2]:
            code = 50
            if self._df['fast_ema'].iloc[-1] < self._df['slow_ema'].iloc[-1]:
                code = -100
        return code


class StrategyTwo(Strategy):
    def __init__(self):
        self._f1 = 50
        self._f2 = 100
        self._f3 = 200

        self._f4 = 14

        self._f5 = 20
        self._f6 = 2

        self._f7 = 198
        self._f8 = 8
        self._f9 = 4

        self._df = None

    def to_sheet(self):
        return self._df.to_dict('list')

    def think(self, history, response):
        size = response
        code = 0

        fast_sma_indicator = indicator.SMAIndicator(self._f1)
        fast_sma_indicator.calculate(history, size)
        fast_sma = pd.DataFrame(fast_sma_indicator.results_to_sheet())
        fast_sma.rename(columns={'sma': 'fast_sma'}, inplace=True)

        mid_sma_indicator = indicator.SMAIndicator(self._f2)
        mid_sma_indicator.calculate(history, size)
        mid_sma = pd.DataFrame(mid_sma_indicator.results_to_sheet())
        mid_sma.rename(columns={'sma': 'mid_sma'}, inplace=True)

        slow_sma_indicator = indicator.SMAIndicator(self._f3)
        slow_sma_indicator.calculate(history, size)
        slow_sma = pd.DataFrame(slow_sma_indicator.results_to_sheet())
        slow_sma.rename(columns={'sma': 'slow_sma'}, inplace=True)

        rsi_indicator = indicator.RSIIndicator(self._f4)
        rsi_indicator.calculate(history, size)
        rsi = pd.DataFrame(rsi_indicator.results_to_sheet())

        bb_indicator = indicator.BBIndicator(self._f5, self._f6)
        bb_indicator.calculate(history, size)
        bb = pd.DataFrame(bb_indicator.results_to_sheet())

        kox_indicator = indicator.KOXIndicator(self._f7, self._f8, self._f9)
        kox_indicator.calculate(history, size)
        kox = pd.DataFrame(kox_indicator.results_to_sheet())
        kox.drop(['ema', 'ema_change_perc', 'signal'], axis=1, inplace=True)
        kox.rename(columns={'roc': 'kox'}, inplace=True)

        self._df = pd.merge(fast_sma, mid_sma, on='mts')
        self._df = pd.merge(self._df, slow_sma, on='mts')
        self._df = pd.merge(self._df, rsi, on='mts')
        self._df = pd.merge(self._df, bb, on='mts')
        self._df = pd.merge(self._df, kox, on='mts')

        return code


def main():
    pass


if __name__ == '__main__':
    main()
