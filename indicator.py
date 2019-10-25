import copy
import math
import numpy as np
import pandas as pd
import candlestick
from enum import Enum


class Source(Enum):
    HIGH = 'high'
    OPEN = 'open'
    CLOSE = 'close'
    LOW = 'low'
    HL2 = 'hl2'
    HLC3 = 'hlc3'
    OHLC4 = 'ohlc4'
    VOLUME = 'volume'


class Indicator(object):
    def results_to_json(self):
        raise NotImplementedError()

    def results_to_sheet(self):
        raise NotImplementedError()

    def setup(self, **kwargs):
        raise NotImplementedError()

    def calculate(self, candle_history, response_size, source):
        raise NotImplementedError()


class EMAIndicator(Indicator):
    def __init__(self, f1=9):
        self._f1 = f1
        self._ema = []
        self._ema_sheet = {
            'mts': [],
            'ema': []
        }

    def results_to_json(self):
        return str(self._ema_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._ema_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')

    def calculate(self, candle_history, response_size, source=Source.CLOSE):
        size = candle_history.size
        candles = candle_history.candles

        ema_arr = np.empty(size)
        ema_arr.fill(0.0)

        # Calculation of the EMA
        total_sum = 0.0
        for i in range(0, self._f1):
            total_sum += getattr(candles[i], source.value)
        ema_arr[self._f1 - 1] = total_sum / self._f1

        w = 2.0 / (self._f1 + 1.0)
        for i in range(self._f1, size):
            ema_arr[i] = (getattr(candles[i], source.value) - ema_arr[i - 1]) * w + ema_arr[i - 1]

        # Clear Lists
        self._ema = []
        self._ema_sheet = {
            'mts': [],
            'ema': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i
            self._ema.append([candles[curr].mts, ema_arr[curr]])
            self._ema_sheet['mts'].append(candles[curr].mts)
            self._ema_sheet['ema'].append(ema_arr[curr])


class BBIndicator(Indicator):
    def __init__(self, f1=20, f2=2):
        self._f1 = f1
        self._f2 = f2
        self._bb = []
        self._bb_sheet = {
            'mts': [],
            'basis': [],
            'upper': [],
            'lower': [],
            'bandwidth': []
        }

    def results_to_json(self):
        return str(self._bb_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._bb_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')
        self._f2 = kwargs.get('f2')

    def calculate(self, candle_history, response_size, source=Source.CLOSE):
        size = candle_history.size
        candles = candle_history.candles

        sma_arr = np.empty(size)
        dev_arr = np.empty(size)
        std_dev_arr = np.empty(size)
        lower_band_arr = np.empty(size)
        upper_band_arr = np.empty(size)
        bandwidth = np.empty(size)

        sma_arr.fill(0.0)
        dev_arr.fill(0.0)
        std_dev_arr.fill(0.0)
        lower_band_arr.fill(0.0)
        upper_band_arr.fill(0.0)
        bandwidth.fill(0.0)

        # Calculation of SMA
        for j in range(self._f1 - 1, size):
            total_sum = 0.0
            i = j
            while i != j - self._f1:
                total_sum += getattr(candles[i], source.value)
                i -= 1
            sma_arr[j] = total_sum / self._f1

        # Calculation of the each period's deviation
        for j in range(self._f1 - 1, size):
            total_sum = 0.0
            i = j
            while i != j - self._f1:
                temp = getattr(candles[i], source.value) - sma_arr[j]
                total_sum += temp * temp
                i -= 1
            dev_arr[j] = total_sum

        # Calculation of the SMA of the squared period's deviation and lower & upper bands
        for j in range(2 * (self._f1 - 1), size):
            std_dev_arr[j] = math.sqrt(dev_arr[j] / self._f1)
            lower_band_arr[j] = sma_arr[j] - (self._f2 * std_dev_arr[j])
            upper_band_arr[j] = sma_arr[j] + (self._f2 * std_dev_arr[j])
            bandwidth[j] = (upper_band_arr[j] - lower_band_arr[j]) / sma_arr[j] * 100

        # Clear Lists
        self._bb = []
        self._bb_sheet = {
            'mts': [],
            'basis': [],
            'upper': [],
            'lower': [],
            'bandwidth': [],
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i
            self._bb.append([candles[curr].mts, sma_arr[curr], upper_band_arr[curr], lower_band_arr[curr],
                             bandwidth[curr]])
            self._bb_sheet['mts'].append(candles[curr].mts)
            self._bb_sheet['basis'].append(sma_arr[curr])
            self._bb_sheet['upper'].append(upper_band_arr[curr])
            self._bb_sheet['lower'].append(lower_band_arr[curr])
            self._bb_sheet['bandwidth'].append(bandwidth[curr])


class KVOIndicator(Indicator):
    def __init__(self, f1=34, f2=55, f3=13):
        self._f1 = f1
        self._f2 = f2
        self._f3 = f3
        self._kvo = []
        self._kvo_sheet = {
            'mts': [],
            'kvo': [],
            'signal': [],
            'histogram': []
        }

    def results_to_json(self):
        return str(self._kvo_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._kvo_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')
        self._f2 = kwargs.get('f2')
        self._f3 = kwargs.get('f3')

    def calculate(self, candle_history, response_size, source=Source.HLC3):
        size = candle_history.size
        candles = candle_history.candles

        sv_arr = np.empty(size - 1)
        fast_ema_arr = np.empty(size - 1)
        slow_ema_arr = np.empty(size - 1)
        kvo_arr = np.empty(size - 1)
        signal_arr = np.empty(size - 1)

        sv_arr.fill(0.0)
        fast_ema_arr.fill(0.0)
        slow_ema_arr.fill(0.0)
        kvo_arr.fill(0.0)
        signal_arr.fill(0.0)

        # Calculation of strength of volume
        for i in range(0, size - 1):
            change = getattr(candles[i + 1], source.value) - getattr(candles[i], source.value)
            sv_arr[i] = 0.0
            if change >= 0:
                sv_arr[i] += candles[i + 1].volume
            else:
                sv_arr[i] -= candles[i + 1].volume

        # Calculation of the fast EMA
        total_sum = 0.0
        for i in range(0, self._f1):
            total_sum += sv_arr[i]
        fast_ema_arr[self._f1 - 1] = total_sum / self._f1

        w = 2.0 / (self._f1 + 1.0)
        for i in range(self._f1, size - 1):
            fast_ema_arr[i] = (sv_arr[i] - fast_ema_arr[i - 1]) * w + fast_ema_arr[i - 1]

        # Calculation of the slow EMA
        total_sum = 0.0
        for i in range(0, self._f2):
            total_sum += sv_arr[i]
        slow_ema_arr[self._f2 - 1] = total_sum / self._f2

        w = 2.0 / (self._f2 + 1.0)
        for i in range(self._f2, size - 1):
            slow_ema_arr[i] = (sv_arr[i] - slow_ema_arr[i - 1]) * w + slow_ema_arr[i - 1]

        # Calculation of KVO
        for i in range(self._f2 - 1, size - 1):
            kvo_arr[i] = fast_ema_arr[i] - slow_ema_arr[i]

        # Calculation of the Signal
        total_sum = 0.0
        for i in range(self._f2 - 1, self._f2 + self._f3):
            total_sum += kvo_arr[i]
        signal_arr[self._f2 - 1 + self._f3] = total_sum / self._f3

        w = 2.0 / (self._f3 + 1.0)
        for i in range(self._f2 + self._f3, size - 1):
            signal_arr[i] = (kvo_arr[i] - signal_arr[i - 1]) * w + signal_arr[i - 1]

        # Clear Lists
        self._kvo = []
        self._kvo_sheet = {
            'mts': [],
            'kvo': [],
            'signal': [],
            'histogram': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i - 1
            self._kvo.append([candles[curr + 1].mts, kvo_arr[curr], signal_arr[curr], kvo_arr[curr] - signal_arr[curr]])
            self._kvo_sheet['mts'].append(candles[curr + 1].mts)
            self._kvo_sheet['kvo'].append(kvo_arr[curr])
            self._kvo_sheet['signal'].append(signal_arr[curr])
            self._kvo_sheet['histogram'].append(kvo_arr[curr] - signal_arr[curr])


class MACDIndicator(Indicator):
    def __init__(self, f1=12, f2=26, f3=9):
        self._f1 = f1
        self._f2 = f2
        self._f3 = f3
        self._macd = []
        self._macd_sheet = {
            'mts': [],
            'macd': [],
            'signal': [],
            'histogram': []
        }

    def results_to_json(self):
        return str(self._macd_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._macd_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')
        self._f2 = kwargs.get('f2')
        self._f3 = kwargs.get('f3')

    def calculate(self, candle_history, response_size, source=Source.CLOSE):
        size = candle_history.size
        candles = candle_history.candles

        fast_arr = np.empty(size)
        slow_arr = np.empty(size)
        macd_arr = np.empty(size)
        signal_arr = np.empty(size)

        macd_arr.fill(0.0)
        slow_arr.fill(0.0)
        fast_arr.fill(0.0)
        signal_arr.fill(0.0)

        # Calculation of Fast EMA
        total_sum = 0.0
        for i in range(0, self._f1):
            total_sum += getattr(candles[i], source.value)
        fast_arr[self._f1 - 1] = total_sum / self._f1

        w = 2.0 / (self._f1 + 1.0)
        for i in range(self._f1, size):
            fast_arr[i] = (getattr(candles[i], source.value) - fast_arr[i - 1]) * w + fast_arr[i - 1]

        # Calculation of Slow EMA
        total_sum = 0.0
        for i in range(0, self._f2):
            total_sum += getattr(candles[i], source.value)
        slow_arr[self._f2 - 1] = total_sum / self._f2

        w = 2.0 / (self._f2 + 1.0)
        for i in range(self._f2, size):
            slow_arr[i] = (getattr(candles[i], source.value) - slow_arr[i - 1]) * w + slow_arr[i - 1]

        # Calculation of MACD
        for i in range(self._f2 - 1, size):
            macd_arr[i] = fast_arr[i] - slow_arr[i]

        # Calculation of Signal
        total_sum = 0.0
        for i in range(self._f2 - 1, self._f2 + self._f3):
            total_sum += macd_arr[i]
        signal_arr[self._f2 - 1 + self._f3] = total_sum / self._f3

        w = 2.0 / (self._f3 + 1)
        for i in range(self._f2 + self._f3, size):
            signal_arr[i] = (macd_arr[i] - signal_arr[i - 1]) * w + signal_arr[i - 1]

        # Clear Lists
        self._macd = []
        self._macd_sheet = {
            'mts': [],
            'macd': [],
            'signal': [],
            'histogram': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i
            self._macd.append([candles[curr].mts, macd_arr[curr], signal_arr[curr], macd_arr[curr] - signal_arr[curr]])
            self._macd_sheet['mts'].append(candles[curr].mts)
            self._macd_sheet['macd'].append(macd_arr[curr])
            self._macd_sheet['signal'].append(signal_arr[curr])
            self._macd_sheet['histogram'].append(macd_arr[curr] - signal_arr[curr])


class SMAIndicator(Indicator):
    def __init__(self, f1=9):
        self._f1 = f1
        self._sma = []
        self._sma_sheet = {
            'mts': [],
            'sma': []
        }

    def results_to_json(self):
        return str(self._sma_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._sma_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')

    def calculate(self, candle_history, response_size, source=Source.CLOSE):
        size = candle_history.size
        candles = candle_history.candles

        sma_arr = np.empty(size)
        sma_arr.fill(0.0)

        # Calculation of the SMA
        for j in range(self._f1 - 1, size):
            total_sum = 0.0
            i = j
            while i != j - self._f1:
                total_sum += getattr(candles[i], source.value)
                i -= 1
            sma_arr[j] = total_sum / self._f1

        # Clear Lists
        self._sma = []
        self._sma_sheet = {
            'mts': [],
            'sma': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i
            self._sma.append([candles[curr].mts, sma_arr[curr]])
            self._sma_sheet['mts'].append(candles[curr].mts)
            self._sma_sheet['sma'].append(sma_arr[curr])


class TSIIndicator(Indicator):
    def __init__(self, f1=25, f2=13, f3=13):
        self._f1 = f1
        self._f2 = f2
        self._f3 = f3
        self._tsi = []
        self._tsi_sheet = {
            'mts': [],
            'tsi': [],
            'signal': [],
            'histogram': []
        }

    def results_to_json(self):
        return str(self._tsi_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._tsi_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')
        self._f2 = kwargs.get('f2')
        self._f3 = kwargs.get('f3')

    def calculate(self, candle_history, response_size, source=Source.CLOSE):
        size = candle_history.size
        candles = candle_history.candles

        price_change_arr = np.empty(size - 1)
        first_ema_arr = np.empty(size - 1)
        second_ema_arr = np.empty(size - 1)
        price_change_abs_arr = np.empty(size - 1)
        first_ema_abs_arr = np.empty(size - 1)
        second_ema_abs_arr = np.empty(size - 1)
        tsi_arr = np.empty(size - 1)
        signal_arr = np.empty(size - 1)

        price_change_arr.fill(0.0)
        first_ema_arr.fill(0.0)
        second_ema_arr.fill(0.0)
        price_change_abs_arr.fill(0.0)
        first_ema_abs_arr.fill(0.0)
        second_ema_abs_arr.fill(0.0)
        tsi_arr.fill(0.0)
        signal_arr.fill(0.0)

        # Calculation of price change and absolute price change
        for i in range(0, size - 1):
            price_change_arr[i] = getattr(candles[i + 1], source.value) - getattr(candles[i], source.value)
            price_change_abs_arr[i] = math.fabs(price_change_arr[i])

        # Calculations of the first smoothing EMAs
        total_sum = 0.0
        total_sum_abs = 0.0
        for i in range(0, self._f1):
            total_sum += price_change_arr[i]
            total_sum_abs += price_change_abs_arr[i]
        first_ema_arr[self._f1 - 1] = total_sum / self._f1
        first_ema_abs_arr[self._f1 - 1] = total_sum_abs / self._f1

        w = 2.0 / (self._f1 + 1.0)
        for i in range(self._f1, size - 1):
            first_ema_arr[i] = (price_change_arr[i] - first_ema_arr[i - 1]) * w + first_ema_arr[i - 1]
            first_ema_abs_arr[i] = (price_change_abs_arr[i] - first_ema_abs_arr[i - 1]) * w + first_ema_abs_arr[i - 1]

        # Calculation of the second smoothing EMAs
        total_sum = 0.0
        total_sum_abs = 0.0
        for i in range(self._f1 - 1, self._f1 + self._f2):
            total_sum += first_ema_arr[i]
            total_sum_abs += first_ema_abs_arr[i]
        second_ema_arr[self._f1 - 1 + self._f2] = total_sum / self._f2
        second_ema_abs_arr[self._f1 - 1 + self._f2] = total_sum_abs / self._f2

        w = 2.0 / (self._f2 + 1.0)
        for i in range(self._f1 + self._f2, size - 1):
            second_ema_arr[i] = (first_ema_arr[i] - second_ema_arr[i - 1]) * w + second_ema_arr[i - 1]
            second_ema_abs_arr[i] = (first_ema_abs_arr[i] - second_ema_abs_arr[i - 1]) * w + second_ema_abs_arr[i - 1]

        # Calculation of the True Strength Index
        for i in range(self._f1 - 1 + self._f2, size - 1):
            tsi_arr[i] = 100 * (second_ema_arr[i] / second_ema_abs_arr[i])

        # Calculation of the signal
        total_sum = 0.0
        for i in range(self._f1 - 1 + self._f2, self._f1 + self._f2 + self._f3):
            total_sum += tsi_arr[i]
        signal_arr[self._f1 - 1 + self._f2 + self._f3] = total_sum / self._f3

        w = 2.0 / (self._f3 + 1.0)
        for i in range(self._f1 + self._f2 + self._f3, size - 1):
            signal_arr[i] = (tsi_arr[i] - signal_arr[i - 1]) * w + signal_arr[i - 1]

        # Clear Lists
        self._tsi = []
        self._tsi_sheet = {
            'mts': [],
            'tsi': [],
            'signal': [],
            'histogram': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i - 1
            self._tsi.append([candles[curr + 1].mts, tsi_arr[curr], signal_arr[curr], tsi_arr[curr] - signal_arr[curr]])
            self._tsi_sheet['mts'].append(candles[curr + 1].mts)
            self._tsi_sheet['tsi'].append(tsi_arr[curr])
            self._tsi_sheet['signal'].append(signal_arr[curr])
            self._tsi_sheet['histogram'].append(tsi_arr[curr] - signal_arr[curr])


class ADXIndicator(Indicator):
    def __init__(self, f1=14, f2=14):
        self._f1 = f1
        self._f2 = f2
        self._adx = []
        self._adx_sheet = {
            'mts': [],
            'adx': [],
            'plus_di': [],
            'minus_di': [],
            'histogram': []
        }

    def results_to_json(self):
        return str(self._adx_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._adx_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')
        self._f2 = kwargs.get('f2')

    def calculate(self, candle_history, response_size, source=None):
        size = candle_history.size
        candles = candle_history.candles

        tr_arr = np.empty(size - 1)
        plus_dm_arr = np.empty(size - 1)
        minus_dm_arr = np.empty(size - 1)
        sm_tr_arr = np.empty(size - 1)
        sm_plus_dm_arr = np.empty(size - 1)
        sm_minus_dm_arr = np.empty(size - 1)
        plus_di_arr = np.empty(size - 1)
        minus_di_arr = np.empty(size - 1)
        dx_arr = np.empty(size - 1)
        adx_arr = np.empty(size - 1)

        tr_arr.fill(0.0)
        plus_dm_arr.fill(0.0)
        minus_dm_arr.fill(0.0)
        sm_tr_arr.fill(0.0)
        sm_plus_dm_arr.fill(0.0)
        sm_minus_dm_arr.fill(0.0)
        plus_di_arr.fill(0.0)
        minus_di_arr.fill(0.0)
        dx_arr.fill(0.0)
        adx_arr.fill(0.0)

        # Calculation of True Range and Plus/Minus Directional Movement
        for i in range(0, size - 1):
            ch_less_cl = candles[i + 1].high - candles[i + 1].low
            ch_less_pc = abs(candles[i + 1].high - candles[i].close)
            cl_less_pc = abs(candles[i + 1].low - candles[i].close)

            tr_arr[i] = ch_less_cl if ch_less_cl >= ch_less_pc else ch_less_pc
            tr_arr[i] = ch_less_pc if ch_less_pc >= cl_less_pc else cl_less_pc

            plus_change = candles[i + 1].high - candles[i].high
            minus_change = candles[i].low - candles[i + 1].low

            plus_dm_arr[i] = plus_change if plus_change > 0 else 0
            minus_dm_arr[i] = minus_change if minus_change > 0 else 0

            plus_dm_arr[i] = plus_dm_arr[i] if plus_dm_arr[i] > minus_dm_arr[i] else 0
            minus_dm_arr[i] = minus_dm_arr[i] if plus_dm_arr[i] < minus_dm_arr[i] else 0

        # Smoothing of TR, +DM and -DM
        for i in range(0, self._f1):
            sm_tr_arr[self._f1 - 1] += tr_arr[i]
            sm_plus_dm_arr[self._f1 - 1] += plus_dm_arr[i]
            sm_minus_dm_arr[self._f1 - 1] += minus_dm_arr[i]

        for i in range(self._f1, size - 1):
            sm_tr_arr[i] = sm_tr_arr[i - 1] - (sm_tr_arr[i - 1] / self._f1) + tr_arr[i]
            sm_plus_dm_arr[i] = sm_plus_dm_arr[i - 1] - (sm_plus_dm_arr[i - 1] / self._f1) + plus_dm_arr[i]
            sm_minus_dm_arr[i] = sm_minus_dm_arr[i - 1] - (sm_minus_dm_arr[i - 1] / self._f1) + minus_dm_arr[i]

        # Calculation of Plus/Minus Directional Indicator & Index
        for i in range(self._f1 - 1, size - 1):
            plus_di_arr[i] = (sm_plus_dm_arr[i] / sm_tr_arr[i]) * 100
            minus_di_arr[i] = (sm_minus_dm_arr[i] / sm_tr_arr[i]) * 100
            dx_arr[i] = abs(plus_di_arr[i] - minus_di_arr[i]) / (plus_di_arr[i] + minus_di_arr[i]) * 100

        # Calculation of Average Directional Movement Index
        total_sum = 0.0
        for i in range(self._f1 - 1, self._f1 + self._f2):
            total_sum += dx_arr[i]
        adx_arr[self._f1 + self._f2 - 1] = total_sum / self._f2

        for i in range(self._f1 + self._f2, size - 1):
            adx_arr[i] = (adx_arr[i - 1] * 13 + dx_arr[i]) / self._f2

        # Clear Lists
        self._adx = []
        self._adx_sheet = {
            'mts': [],
            'adx': [],
            'plus_di': [],
            'minus_di': [],
            'histogram': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i - 1
            self._adx.append([
                candles[curr + 1].mts,
                adx_arr[curr],
                plus_di_arr[curr],
                minus_di_arr[curr],
                plus_di_arr[curr] - minus_di_arr[curr]
            ])
            self._adx_sheet['mts'].append(candles[curr + 1].mts)
            self._adx_sheet['adx'].append(adx_arr[curr])
            self._adx_sheet['plus_di'].append(plus_di_arr[curr])
            self._adx_sheet['minus_di'].append(minus_di_arr[curr])
            self._adx_sheet['histogram'].append(plus_di_arr[curr] - minus_di_arr[curr])


class RSIIndicator(Indicator):
    def __init__(self, f1=14):
        self._f1 = f1
        self._rsi = []
        self._rsi_sheet = {
            'mts': [],
            'rsi': []
        }

    def results_to_json(self):
        return str(self._rsi_sheet).replace('\'', '"')

    def results_to_sheet(self):
        return copy.deepcopy(self._rsi_sheet)

    def setup(self, **kwargs):
        self._f1 = kwargs.get('f1')

    def calculate(self, candle_history, response_size, source=Source.CLOSE):
        size = candle_history.size
        candles = candle_history.candles

        price_change_arr = np.empty(size - 1)
        gain_arr = np.empty(size - 1)
        loss_arr = np.empty(size - 1)
        avg_gain_arr = np.empty(size - 1)
        avg_loss_arr = np.empty(size - 1)
        rs_arr = np.empty(size - 1)
        rsi_arr = np.empty(size - 1)

        price_change_arr.fill(0.0)
        gain_arr.fill(0.0)
        loss_arr.fill(0.0)
        avg_gain_arr.fill(0.0)
        avg_loss_arr.fill(0.0)
        rs_arr.fill(0.0)
        rsi_arr.fill(0.0)

        # Calculation of Price Change
        for i in range(0, size - 1):
            price_change_arr[i] = getattr(candles[i + 1], source.value) - getattr(candles[i], source.value)
            if price_change_arr[i] > 0:
                gain_arr[i] = price_change_arr[i]
            else:
                loss_arr[i] = abs(price_change_arr[i])

        # Calculation of RSI
        total_sum1 = 0.0
        total_sum2 = 0.0
        for i in range(0, self._f1):
            total_sum1 += gain_arr[i]
            total_sum2 += loss_arr[i]
        avg_gain_arr[self._f1 - 1] = total_sum1 / self._f1
        avg_loss_arr[self._f1 - 1] = total_sum2 / self._f1

        for i in range(self._f1, size - 1):
            avg_gain_arr[i] = (avg_gain_arr[i - 1] * (self._f1 - 1) + gain_arr[i]) / self._f1
            avg_loss_arr[i] = (avg_loss_arr[i - 1] * (self._f1 - 1) + loss_arr[i]) / self._f1

            if avg_loss_arr[i] == 0:
                rsi_arr[i] = 100
            elif avg_gain_arr[i] == 0:
                rsi_arr[i] = 0
            else:
                rsi_arr[i] = 100 - 100 / (1 + avg_gain_arr[i] / avg_loss_arr[i])

        # Clear Lists
        self._rsi = []
        self._rsi_sheet = {
            'mts': [],
            'rsi': []
        }

        # Summary
        for i in range(response_size, 0, -1):
            curr = size - i - 1
            self._rsi.append([candles[curr + 1].mts, rsi_arr[curr]])
            self._rsi_sheet['mts'].append(candles[curr + 1].mts)
            self._rsi_sheet['rsi'].append(rsi_arr[curr])


def new_indicator(indicator):
    return {
        'ema': EMAIndicator(),
        'bb': BBIndicator(),
        'kvo': KVOIndicator(),
        'macd': MACDIndicator(),
        'sma': SMAIndicator(),
        'tsi': TSIIndicator(),
        'adx': ADXIndicator(),
        'rsi': RSIIndicator()
    }[indicator]


def main():
    pass


if __name__ == '__main__':
    main()
