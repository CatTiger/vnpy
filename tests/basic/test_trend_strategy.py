from datetime import datetime

import vnpy.trader.constant as const
from vnpy.app.cta_strategy import BacktestingEngine
from vnpy.app.cta_strategy.strategies.trend_strategy import TrendStrategy

if __name__ == '__main__':
    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 定义合约代码
    symbol = '510050'
    exchange = 'SSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2005, 1, 1), end=datetime(2019, 1, 1), rate=5 / 10000, slippage=0,
                          size=1,
                          pricetick=0.001, capital=10000)

    # 加载到history_data中
    engine.load_data()

    date_list = []
    for data in engine.history_data[:-1]:
        date_list.append(data.datetime.strftime('%Y-%m-%d'))

    nd_open_price = []
    for data in engine.history_data[1:]:
        nd_open_price.append(data.open_price)

    his_data_dict = dict(zip(date_list, nd_open_price))

    # 添加策略
    engine.add_strategy(TrendStrategy, {'his_data_dict': his_data_dict})

    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()
    # print(engine.trades)