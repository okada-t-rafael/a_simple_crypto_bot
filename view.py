import time


class ReportView(object):
    def __init__(self):
        self.trade_pair = ''
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        self.action_msg = 'Just Waiting Patiently'

        self.base = 0.0
        self.amount = 0.0
        self.pl = 0.0
        self.pl_perc = 0.0
        self.pl_high_perc = 0.0

        self.real_available_usd = 0.0
        self.total_usd = 0.0
        self.last_price = 0.0
        self.peak_price = 0.0
        self.peak_price_perc = 0.0
        self.bottom_price = 0.0
        self.bottom_price_perc = 0.0
        self.daily_volume = 0.0

        self.fast_ema = 0.0
        self.slow_ema = 0.0
        self.ratio_ema = 0.0

        self.fast_sma = 0.0
        self.mid_sma = 0.0
        self.slow_sma = 0.0
        self.basis = 0.0
        self.upper = 0.0
        self.lower = 0.0
        self.rsi = 0.0
        self.rsi_change = 0.0
        self.kox = 0.0

        self.write_on_log = False

    def to_json(self):
        return str(self.__dict__).replace('\'', '"')

    @property
    def string_buffer(self):
        return f'+----------------------------------------------+\n' \
            f'|             Trading Bot - {self.trade_pair}             |\n' \
            f'+----------------------------------------------+' \
            f'\n Turn:\n' \
            f' - Trading Pair: {self.trade_pair};\n' \
            f' - Timestamp: {self.timestamp};\n' \
            f'\n Action:\n' \
            f' - {self.action_msg};\n' \
            f'\n Position:\n' \
            f' - Symbol: {self.trade_pair};\n' \
            f' - Base: {self.base:,.5f};\n' \
            f' - Amount: {self.amount:,.6f};\n' \
            f' - Profit/Loss: {self.pl:.4f};\n' \
            f' - PL Perc.: {self.pl_perc:.4f};\n' \
            f' - PL High Perc.: {self.pl_high_perc:.4f};\n' \
            f'\n Current State:\n' \
            f' - Balance: USD: {self.real_available_usd:,.4f} / {self.total_usd:,.4f};\n' \
            f' - Last Price: {self.last_price:,.5f};\n' \
            f' - Highest Price: {self.peak_price:,.5f}; Ratio: {self.peak_price_perc:.5f};\n' \
            f' - Lowest  Price: {self.bottom_price:,.5f}; Ratio: {self.bottom_price_perc:.5f};\n' \
            f' - Daily Volume: {self.daily_volume:,.4f};\n' \
            f'\n Trend Following Report:\n' \
            f' - EMA: {self.fast_ema:.4f} / {self.slow_ema:.4f}; Ratio: {self.ratio_ema:.4f};\n' \
            f'\n Overall Info Report:\n' \
            f' - SMA: Fast: {self.fast_sma:.4f}; Mid: {self.mid_sma:.4f}; Slow: {self.slow_sma:.4f};\n' \
            f' - BB : {self.basis:.4f}; Upper: {self.upper:.4f}; Lower: {self.lower:.4f};\n' \
            f' - RSI: {self.rsi:.4f} / Change: {self.rsi_change:.4f};\n' \
            f' - KOX: {self.kox:.4f};\n' \
            f'+----------------------------------------------+\n'

    def action_register(self, action, position):
        if action == 'buy' and position == 'no-position':
            self.action_msg = 'Build Long Position'
        elif action == 'buy' and position == 'short-position':
            self.action_msg = 'Build Long Position'
        elif action == 'sell' and position == 'no-position':
            self.action_msg = 'Build Short Position'
        elif action == 'sell' and position == 'long-position':
            self.action_msg = 'Build Short Position'
        elif action == 'achieved' and position == 'short-position':
            self.action_msg = 'Target Achieved, Release Short Position'
        elif action == 'achieved' and position == 'long-position':
            self.action_msg = 'Target Achieved, Release Long Position'
        elif action == 'release' and position == 'short-position':
            self.action_msg = 'Emergency, Release Short Position'
        elif action == 'release' and position == 'long-position':
            self.action_msg = 'Emergency, Release Long Position'

        # Log.
        with open('log.txt', 'a') as file:
            file.write(self.string_buffer)


def main():
    pass


if __name__ == '__main__':
    main()
