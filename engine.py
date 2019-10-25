import state
import strategy
import candlestick
import view
import pandas as pd
from exchange import OrderSide


class Engine(object):
    TOLERANCE = 0.02
    INVESTMENT_PERC = 0.25

    def __init__(self, trade_pair, time_frame, size=500):
        self.trade_pair = trade_pair
        self.size = size
        self.state = state.State(trade_pair, time_frame)
        self.history = candlestick.CandleHistory(trade_pair, time_frame, size)
        self.stgy1 = strategy.StrategyOne()
        self.stgy2 = strategy.StrategyTwo()

    def loop_once(self):
        self.history.update()
        self.state.update()
        result_one = self.stgy1.think(self.history, int(self.size / 2))
        result_two = self.stgy2.think(self.history, int(self.size / 2))
        report = view.ReportView()
        self.report_update(report)

        # Build Long / Short Positions
        if result_one == 100:
            self.adjust_position('buy', report)
        elif result_one == -100:
            self.adjust_position('sell', report)

        # Target Achieved.
        if self.state.position and self.state.pl_perc >= Engine.TOLERANCE * 2:
            self.release_position('achieved', report)

        # Emergency Exit.
        if self.state.position and self.state.pl_perc <= -Engine.TOLERANCE:
            self.release_position('release', report)

        return report

    def adjust_position(self, action, report):
        position = self.check_position()
        amount = self.state.balance.total_usd / self.state.last_price * Engine.INVESTMENT_PERC
        if action == 'buy' and position == 'no-position':
            self.buy(amount)
            report.action_register(action, position)
        elif action == 'buy' and position == 'short-position':
            amount += abs(float(self.state.position.amount))
            self.buy(amount)
            report.action_register(action, position)
        elif action == 'sell' and position == 'no-position':
            self.sell(amount)
            report.action_register(action, position)
        elif action == 'sell' and position == 'long-position':
            amount += abs(float(self.state.position.amount))
            self.buy(amount)
            report.action_register(action, position)

    def release_position(self, action, report):
        position = self.check_position()
        if position == 'long-position':
            amount = abs(float(self.state.position.amount))
            self.sell(amount)
            report.action_register(action, position)
        elif position == 'short-position':
            amount = abs(float(self.state.position.amount))
            self.buy(amount)
            report.action_register(action, position)

    def buy(self, amount):
        self.state.adjust_position(amount, OrderSide.BUY)
        self.state.pl_high_perc = 0

    def sell(self, amount):
        self.state.adjust_position(amount, OrderSide.SELL)
        self.state.pl_high_perc = 0

    def check_position(self):
        if self.state.position:
            if float(self.state.position.amount) > 0:
                return 'long-position'
            elif float(self.state.position.amount) < 0:
                return 'short-position'
        else:
            return 'no-position'

    def report_update(self, report):
        report.trade_pair = self.trade_pair

        if self.state.position:
            report.base = float(self.state.position.base)
            report.amount = float(self.state.position.amount)
            report.pl = float(self.state.position.pl)
            report.pl_perc = float(self.state.pl_perc)
            report.pl_high_perc = float(self.state.pl_high_perc)

        total_available_usd = self.state.balance.total_available_usd
        total_usd = self.state.balance.total_usd
        max_leverage = 3.3
        report.real_available_usd = total_usd * (1 - max_leverage) + total_available_usd * max_leverage
        report.total_usd = total_usd
        report.last_price = self.state.last_price
        report.peak_price = self.state.peak_price
        report.peak_price_perc = self.state.last_price / self.state.peak_price if self.state.peak_price != 0 else 0
        report.bottom_price = self.state.bottom_price
        report.bottom_price_perc = self.state.last_price / self.state.bottom_price

        stgy1_df = pd.DataFrame(self.stgy1.to_sheet())
        f_ema = stgy1_df['fast_ema'].iloc[-1]
        s_ema = stgy1_df['slow_ema'].iloc[-1]
        report.fast_ema = f_ema
        report.slow_ema = s_ema
        report.ratio_ema = (f_ema - s_ema) / f_ema if f_ema > s_ema else (f_ema - s_ema) / s_ema
        report.daily_volume = self.state.daily_volume

        stgy2_df = pd.DataFrame(self.stgy2.to_sheet())
        report.fast_sma = stgy2_df['fast_sma'].iloc[-1]
        report.mid_sma = stgy2_df['mid_sma'].iloc[-1]
        report.slow_sma = stgy2_df['slow_sma'].iloc[-1]
        report.basis = stgy2_df['basis'].iloc[-1]
        report.upper = stgy2_df['upper'].iloc[-1]
        report.lower = stgy2_df['lower'].iloc[-1]
        report.rsi = stgy2_df['rsi'].iloc[-1]
        report.rsi_change = stgy2_df['rsi'].iloc[-1] - stgy2_df['rsi'].iloc[-4]
        report.kox = stgy2_df['kox'].iloc[-1]


def main():
    pass


if __name__ == '__main__':
    main()
