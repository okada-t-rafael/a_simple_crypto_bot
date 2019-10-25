import engine
import time
import os


TRADE_PAIR = 'BTCUSD'
TIME_FRAME = '3h'
SIZE = 500
TICK = int(60000 / 1000)  # 60S


class TradingBotConsole(object):
    def __init__(self):
        self.engine = engine.Engine(TRADE_PAIR, TIME_FRAME, SIZE)
        self._is_running = True

    def start(self):
        self.run()

    def run(self):
        while self._is_running:
            try:
                start_time = time.time()
                report = self.engine.loop_once().string_buffer
                os.system('cls' if os.name == 'nt' else 'clear')
                print(report)
                sleep_time = TICK - (time.time() - start_time)
            except Exception as e:
                time.sleep(TICK)
                print(e)
            else:
                if sleep_time >= 0:
                    time.sleep(sleep_time)
                else:
                    time.sleep(TICK)


if __name__ == '__main__':
    app = TradingBotConsole()
    app.start()
