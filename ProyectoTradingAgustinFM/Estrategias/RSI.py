from __future__ import (absolute_import,division,print_function,unicode_literals)
import matplotlib
import datetime
import os.path
import sys
import backtrader as bt
import backtrader.indicators as btind


class RSI(bt.Strategy):
    params = (
        ('rsi_period', 14),)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.rsi = bt.indicators.RSI(period = self.params.rsi_period)
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        if self.rsi < 30 and not self.position:
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy()
        if self.rsi > 70 and self.position:
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