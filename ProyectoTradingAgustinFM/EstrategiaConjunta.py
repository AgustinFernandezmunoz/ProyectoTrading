from __future__ import (absolute_import,division,print_function,unicode_literals)
import datetime
import backtrader as bt



# Definir la estrategia
class Conjunta(bt.Strategy):
    params = (
        ('fast', 50), #Fast SMA Golden Cross (50 dias)
        ('slow', 200), #Slow SMA Golden Cross (200 dias)
        ('rsi_period', 14), #Periodo del RSI (14 dias el mas comun)
        ('macd1', 12), #EMA 12 dias
        ('macd2', 26), #EMA 26 dias
        ('macdsig', 9), #EMA 9 dias señal
        ('atrperiod', 14), #ATR 14 dias
        ('atrdist', 3.0), #Distancia de ATR
        ('smaperiod', 30), #SMA de tendencia de mercado
        ('dirperiod', 10),) #10 dias menos del SMA

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        #Golden Cross
        self.fast_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.fast, plotname='50 days moving average')
        self.slow_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.slow, plotname='200 days moving average')

        self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)

        #RSI
        self.rsi = bt.indicators.RSI(period = self.params.rsi_period)

        #MACD
        self.macd = bt.indicators.MACD(self.data,
                                       period_me1=self.params.macd1,
                                       period_me2=self.params.macd2,
                                       period_signal=self.params.macdsig)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atrperiod)
        self.sma = bt.indicators.SMA(self.data, period=self.params.smaperiod)
        self.smadir = self.sma - self.sma(-self.params.dirperiod)

        self.dataclose = self.datas[0].close
        self.order = None

        #Indicadores de compra particulares de cada tecnica
        self.buy_rsi = False
        self.buy_crossover = False
        self.buy_macd = False

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        # Si no hay una orden abierta, evaluamos las condiciones de compra
        if not self.buy_rsi and not self.buy_crossover and not self.buy_macd:
            if self.rsi < 30:  # RSI compra
                self.log('RSI: BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
                self.buy_rsi = True  # Marca la compra por la tecnica RSI

            elif self.crossover > 0:  # Golden Cross compra
                self.log('Golden Cross: BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
                self.buy_crossover = True  # Marca la compra por la tecnica Golden Cross

            elif self.mcross[0] > 0.0 and self.smadir < 0.0:  # MACD compra
                self.log('MACD: BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
                pdist = self.atr[0] * self.p.atrdist
                self.pstop = self.data.close[0] - pdist
                self.buy_macd = True  # Marca la compra por la tecnica MACD

        # Si ya tenemos una compra por un indicador/tecnica, evaluamos la venta para el mismo indicador
        else:
            if self.buy_rsi and self.rsi > 70:  # Venta basada en RSI
                self.log('RSI: SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
                self.buy_rsi = False  # Restablece la bandera RSI

            elif self.buy_crossover and self.crossover < 0:  # Venta basada en Golden Cross
                self.log('Golden Cross: SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
                self.buy_crossover = False  # Restablece la bandera Golden Cross

            elif self.buy_macd: # Venta basada en MACD
                pclose = self.data.close[0]
                pstop = self.pstop
                if pclose < pstop:
                    self.close()  # stop met - get out
                else:
                    pdist = self.atr[0] * self.p.atrdist
                    # Update only if greater than
                    self.pstop = max(pstop, pclose - pdist)
                    self.log('MACD: SELL CREATE, %.2f' % self.dataclose[0])
                    self.order = self.sell()
                    self.buy_macd = False  # Restablece la bandera MACD

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f, %2f, %2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))
                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm

            elif order.issell():
                self.log('SELL EXECUTED, %.2f, %2f, %2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.broker.setcash(100000.0)

    data1 = bt.feeds.YahooFinanceCSVData(
            dataname = 'Datafeeds/Oracle1995-2014',
            fromdate = datetime.datetime(2005,1,1),
            todate = datetime.datetime(2014,1,1),
            reverse = False)

    data2 = bt.feeds.YahooFinanceCSVData(
        dataname='Datafeeds/Yahoo1996-2015',
        fromdate=datetime.datetime(2010, 1, 1),
        todate=datetime.datetime(2014, 1, 1),
        reverse=False)

    data3 = bt.feeds.YahooFinanceCSVData(
        dataname='Datafeeds/Meta2014-2024',
        fromdate=datetime.datetime(2015, 1, 1),
        todate=datetime.datetime(2023, 1, 1),
        reverse=False)

    #Aca seleccionas que Datafeed vas a utilizar para el backtesting
    cerebro.adddata(data3)

    cerebro.addsizer(bt.sizers.PercentSizer, percents = 90)

    cerebro.addstrategy(Conjunta)

    cerebro.broker.setcommission(commission=0.001)

    initial = cerebro.broker.getvalue()

    print('Starting Portfolio Value: %.2f' % initial)

    cerebro.run()

    final = cerebro.broker.getvalue()

    print('Final Portfolio Value: %.2f' % final)

    profit = final - initial

    percentage = ((final / initial) * 100 - 100)

    print('Profit: %2f Percentage: %2f' % (profit, percentage))

    cerebro.plot()