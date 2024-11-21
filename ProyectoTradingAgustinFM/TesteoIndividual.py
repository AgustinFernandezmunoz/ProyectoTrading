from __future__ import (absolute_import,division,print_function,unicode_literals)
import matplotlib
import datetime
import os.path
import sys
import backtrader as bt
from Estrategias.GoldenCross import GoldenCross
from Estrategias.BuyHold import BuyHold
from Estrategias.MACD import MACD
from Estrategias.RSI import RSI


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)

    data1 = bt.feeds.YahooFinanceCSVData(
        dataname = 'Datafeeds/Oracle1995-2014',
        fromdate = datetime.datetime(2005,1,1),
        todate = datetime.datetime(2014,1,1),
        reverse = False)

    data2 = bt.feeds.YahooFinanceCSVData(
        dataname= 'Datafeeds/Yahoo1996-2015',
        fromdate=datetime.datetime(2005, 1, 1),
        todate=datetime.datetime(2014, 1, 1),
        reverse=False)

    data3 = bt.feeds.YahooFinanceCSVData(
        dataname='Datafeeds/Meta2014-2024',
        fromdate=datetime.datetime(2015, 1, 1),
        todate=datetime.datetime(2023, 1, 1),
        reverse=False)

    cerebro.adddata(data3)
    cerebro.addsizer(bt.sizers.PercentSizer, percents = 90)
    cerebro.addstrategy(BuyHold)
    cerebro.broker.setcommission(commission=0.001)
    initial = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % initial)
    cerebro.run()
    final = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % final)
    profit = final - initial
    percentage = ((final/initial) * 100 - 100)
    print('Profit: %2f Percentage: %2f' % (profit,percentage))
    cerebro.plot()