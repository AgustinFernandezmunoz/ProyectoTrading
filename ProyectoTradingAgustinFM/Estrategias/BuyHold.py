import backtrader as bt

class BuyHold(bt.Strategy):

    def __init__(self):
        pass
    def next(self):
        self.buy()