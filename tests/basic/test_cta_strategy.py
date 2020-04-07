from vnpy.app.cta_strategy import BacktestingEngine
from vnpy.app.cta_strategy.strategies.double_ma_strategy import DoubleMaStrategy
import vnpy.app.cta_strategy.backtesting as backtesting
import vnpy.trader.constant as const
from datetime import datetime

if __name__ == '__main__':
    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 定义合约代码
    symbol = '002594'
    exchange = 'SZSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2011, 7, 1), end=datetime(2020, 2, 24), rate=15 / 10000, slippage=0,
                          size=1,
                          pricetick=0.001, capital=10000)

    # 添加策略
    engine.add_strategy(DoubleMaStrategy, {})

    # backtesting.load_bar_data(symbol, const.Exchange.SSE, const.Interval.DAILY, datetime(2018, 1, 1),
    #                           datetime(2019, 1, 1))

    # 加载到history_data中
    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    # engine.show_chart()
    # print(engine.trades)
