from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.strategies.macd_strategy import MacdStrategy
import vnpy.app.cta_strategy.backtesting as backtesting
import vnpy.trader.constant as const
from datetime import datetime
import vnpy.analyze.view.k_view as kview

if __name__ == '__main__':
    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 定义合约代码
    symbol = '000001'
    exchange = const.Exchange.SSE.value
    vtSymbol = '.'.join([symbol, exchange])
    engine.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2010, 1, 1), end=datetime(2020, 1, 1),
                          rate=5 / 10000, slippage=0,
                          size=1,
                          pricetick=0.001, capital=100000)

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
    engine.add_strategy(MacdStrategy, {'his_data_dict': his_data_dict})

    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    # 过滤器：1、支撑阻力(boll)，2、超买、超卖(KDJ)，3、成交量，4、周期性（趋势确认），5、蜡烛图形态, 6、背离
    # engine.show_chart()
    # kview.draw_backtesting(engine.history_data, engine.trades)