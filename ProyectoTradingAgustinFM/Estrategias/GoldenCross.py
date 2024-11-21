import math
import datetime
import backtrader as bt

class GoldenCross(bt.Strategy):
    params = (('fast',50),
              ('slow',200),
              ('ticker','Datafeed/Oracle1995-2014'))
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.fast_moving_average = bt.indicators.SMA(
            self.data.close, period = self.params.fast, plotname = '50 days moving average'
        )
        self.slow_moving_average = bt.indicators.SMA(
            self.data.close, period = self.params.slow, plotname = '200 days moving average'
        )
        self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)
        self.dataclose = self.datas[0].close
        self.order = None


    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        if not self.position:
            if self.crossover > 0:
                print("Buy {} shares of {} at {}".format(self.position.size, self.params.ticker, self.data.close[0]))
                self.order = self.buy()
        if self.position:
            if self.crossover < 0:
                print("Sell {} shares of {} at {}".format(self.position.size, self.params.ticker, self.data.close[0]))
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, %.2f, %2f, %2f' % (order.executed.price, order.executed.value, order.executed.comm))
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
            elif order.issell():
                self.log(
                    'SELL EXECUTED, %.2f, %2f, %2f' % (order.executed.price, order.executed.value, order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

