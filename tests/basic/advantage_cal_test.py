from collections import namedtuple
from datetime import datetime

import vnpy.trader.constant as const
from tests.basic.extra_object import TradeProfit
from vnpy.app.cta_strategy import BacktestingEngine
from vnpy.trader import date_utility
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from collections import defaultdict


def get_date_pairs(in_dates, step):
    """
    入场点出场点数据
    :param in_dates: 所有入场日期
    :param step: 步长
    :return:
    """
    DatePair = namedtuple('DatePair', ['in_date', 'out_date'])
    date_pairs = []
    for in_date in in_dates:
        out_date = date_utility.date_cal(in_date, step)
        date_pairs.append(DatePair(in_date, out_date))

    return date_pairs


def get_trade_profit_item(date_pairs, h_data_map):
    """
    获取交易的利润项
    :param date_pairs: 入场出场匹配列表
    :param h_data_map: 日交易bar的map集合
    :return:
    """
    tp = TradeProfit(1, 0.0, 0.0, 1, 0)

    for date_pair in date_pairs:
        if date_pair.in_date in h_data_map and date_pair.out_date in h_data_map:
            tp.sample_size += 1
            in_price = h_data_map[date_pair.in_date].close_price
            out_price = h_data_map[date_pair.out_date].close_price
            change = out_price - in_price
            if change >= 0:
                tp.total_profit += change
            else:
                tp.total_loss += change

    tp.ratio = tp.total_profit / -tp.total_loss
    return tp


if __name__ == '__main__':
    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 定义合约代码
    symbol = '002594'
    exchange = 'SZSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2011, 7, 1), end=datetime(2020, 2, 24),
                          rate=0, slippage=0,
                          size=1,
                          pricetick=0.001, capital=3000)

    # 加载到history_data中
    engine.load_data()
    h_data = engine.history_data

    # 所有历史bar数据
    h_data_map = {}
    for data in h_data:
        h_data_map[data.datetime.strftime('%Y%m%d')] = data

    # 随机获取的开始入场点
    in_dates = date_utility.gen_random_date_str(datetime(2011, 8, 1), datetime(2020, 2, 24), 500)

    # 生成不同步长的TradeProfit
    tps = defaultdict(list)
    for step in range(1, 100):
        date_pairs = get_date_pairs(in_dates, step)
        tp = get_trade_profit_item(date_pairs, h_data_map)
        tps['step'].append(step)
        tps['ratio'].append(tp.ratio)
        # tps['sample'].append(tp.sample_size)

    tp_df = DataFrame.from_dict(tps).set_index('step')
    tp_df.plot()
    plt.show()
    # print(tp_df)

    # engine.run_backtesting()
    # engine.calculate_result()
    # engine.calculate_statistics()
    # engine.show_chart()
    # print(engine.trades)
