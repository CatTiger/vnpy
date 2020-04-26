from datetime import datetime

from vnpy.app.portfolio_strategy import BacktestingEngine
from vnpy.app.portfolio_strategy.strategies.trend_following_strategy import TrendFollowingStrategy
from vnpy.trader.constant import Interval

if __name__ == '__main__':
    # 创建回测引擎实例
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbols=["000001.SSE", "510050.SSE"],
        interval=Interval.DAILY,
        start=datetime(2019, 2, 1),
        end=datetime(2020, 4, 30),
        rates={"000001.SSE": 0.3 / 10000, "510050.SSE": 0.3 / 10000},
        slippages={"000001.SSE": 0.2, "510050.SSE": 0.2},
        sizes={"000001.SSE": 300, "510050.SSE": 300},
        priceticks={"000001.SSE": 0.2, "510050.SSE": 0.2},
        capital=1_000_000,
    )
    engine.add_strategy(TrendFollowingStrategy, {})
    engine.load_data()
    engine.run_backtesting()
    df = engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()
