from datetime import datetime

import vnpy.trader.constant as const
from vnpy.app.cta_strategy import BacktestingEngine
from vnpy.app.cta_strategy.strategies.rsrs_strategy import RSRSStrategy
from vnpy.trader.utility import ArrayManager
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm


def draw_his(zscore_data, test_data):
    # RSRS标准分分布
    am = ArrayManager(200, zscore_data, 18)

    rsrs = []
    for bar in test_data:
        am.update_bar(bar)
        rsrs.append(am.rsrs_std())

    ser = pd.Series(rsrs)
    ser.hist(bins=50, color='b', edgecolor='gray', alpha=0.7, grid=False)
    plt.show()

def draw_his_2():
    engine_data = BacktestingEngine()
    # 定义合约代码
    symbol = '510050'
    exchange = 'SSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine_data.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2018, 1, 1), end=datetime(2019, 1, 1),
                               rate=5 / 10000, slippage=0,
                               size=1,
                               pricetick=0.001, capital=10000)

    # 加载到history_data中
    engine_data.load_data()
    zscore_data = engine_data.history_data
    am = ArrayManager(200, zscore_data, 18)
    print(am.beta_array)

def test_rs():
    engine_data = BacktestingEngine()
    # 定义合约代码
    symbol = '510050'
    exchange = 'SSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine_data.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2019, 6, 20), end=datetime(2019, 6, 24),
                               rate=5 / 10000, slippage=0,
                               size=1,
                               pricetick=0.001, capital=10000)

    # 加载到history_data中
    engine_data.load_data()
    zscore_data = engine_data.history_data
    highs = []
    lows = []
    for data in zscore_data:
        highs.append(data.high_price)
        lows.append(data.low_price)
    X = sm.add_constant(lows)
    model = sm.OLS(highs, X)
    beta = model.fit().params[1]
    r2 = model.fit().rsquared
    print('beta:%s, r2:%s' % (beta, r2))


if __name__ == '__main__':
    # test_rs()
    # draw_his_2()

    # 创建回测引擎实例
    engine_data = BacktestingEngine()

    # 定义合约代码
    symbol = '510050'
    exchange = 'SSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine_data.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2005, 7, 28), end=datetime(2010, 1, 29),
                               rate=5 / 10000, slippage=0,
                               size=1,
                               pricetick=0.001, capital=10000)

    # 加载到history_data中
    engine_data.load_data()
    zscore_data = engine_data.history_data

    print(len(zscore_data))
    # ---------------------

    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 定义合约代码
    symbol = '510050'
    exchange = 'SSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2010, 2, 1), end=datetime(2019, 12, 26),
                          rate=1 / 1000, slippage=0,
                          size=1,
                          pricetick=0.001, capital=10000)

    # 加载到history_data中
    engine.load_data()

    draw_his(engine_data.history_data, engine.history_data)

    date_list = []
    for data in engine.history_data[:-1]:
        date_list.append(data.datetime.strftime('%Y-%m-%d'))

    nd_open_price = []
    for data in engine.history_data[1:]:
        nd_open_price.append(data.open_price)

    his_data_dict = dict(zip(date_list, nd_open_price))

    # 添加策略
    engine.add_strategy(RSRSStrategy, {'zscore_data': zscore_data, 'his_data_dict': his_data_dict})

    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()

    engine.show_chart()
