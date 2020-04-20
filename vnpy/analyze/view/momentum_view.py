import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import ticker
import vnpy.analyze.data.data_prepare as dp


def annual_return_cmp(benchmark, **kwargs):
    """

    :param benchmark: 基准价格数据
    :param kwargs: 各种需要对比数据
    :return:
    """
    benchmark_price = benchmark.close[0]
    benchmark['rate'] = benchmark.apply(lambda x: 100 * (x.close - benchmark_price) / benchmark_price, axis=1)

    sns.set(style='darkgrid', context='talk', palette='Dark2')

    fig, ax = plt.subplots(figsize=(benchmark.__len__() / 22 * 1.5, 8))
    benchmark['date'] = pd.to_datetime(benchmark['date'])
    benchmark['date'] = benchmark['date'].apply(lambda x: mdates.date2num(x))
    ax.plot(benchmark.date, benchmark.rate, label='benchmark rate')

    # 增加对比数据
    for key in kwargs:
        data = kwargs[key]
        data['date'] = pd.to_datetime(data['date'])
        data['date'] = data['date'].apply(lambda x: mdates.date2num(x))
        # 回报率计算
        init_price = data.close[0]
        data['rate'] = data.apply(lambda x: 100 * (x.close - init_price) / init_price, axis=1)
        ax.plot(data.date, data.rate, label=key)

    ax.legend(loc='best')
    ax.set_ylabel('Rate')
    # 设置x轴
    ax.xaxis.set_major_locator(ticker.MaxNLocator(12))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.show()


def draw_close_price(benchmark_data, **kwargs):
    """
    画出收盘价图形
    :param benchmark_data: 基准数据
    :param kwargs: k: 股票代码, v: data数据
    :return:
    """
    sns.set(style='darkgrid', context='talk', palette='Dark2')

    fig, ax = plt.subplots(figsize=(benchmark_data.__len__() / 22 * 1.5, 8))
    benchmark_data['date'] = pd.to_datetime(benchmark_data['date'])
    benchmark_data['date'] = benchmark_data['date'].apply(lambda x: mdates.date2num(x))
    ax.plot(benchmark_data.date, benchmark_data.close, label='benchmark Close Price')

    # 增加对比数据
    for key in kwargs:
        data = kwargs[key]
        data['date'] = pd.to_datetime(data['date'])
        data['date'] = data['date'].apply(lambda x: mdates.date2num(x))
        ax.plot(data.date, data.close, label=key)

    ax.legend(loc='best')
    ax.set_ylabel('Close Price')
    # 设置x轴
    ax.xaxis.set_major_locator(ticker.MaxNLocator(12))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.show()


if __name__ == "__main__":
    start = dt.datetime(2020, 1, 1)
    end = dt.datetime(2020, 4, 19)
    etf300 = dp.load_bar_data('510300', 'XSHG', start_date=start,
                              end_data=end)  # 沪深300
    kv = {}
    # etf500 = dp.load_bar_data('510500', 'XSHG', start_date=start,
    #                           end_data=end)  # 中证500
    # kv['ETF-500'] = etf500
    # etfcy = dp.load_bar_data('159915', 'XSHE', start_date=start,
    #                          end_data=end)  # 创业板
    # kv['ETF-cy'] = etfcy

    # etf159995 = dp.load_bar_data('159995', 'XSHG', start_date=start,
    #                           end_data=end)  # 中证500
    # kv['ETF-159995'] = etf159995
    # etf513050 = dp.load_bar_data('513050', 'XSHE', start_date=start,
    #                          end_data=end)  # 创业板
    # kv['ETF-513050'] = etf513050
    # etf512290 = dp.load_bar_data('512290', 'XSHE', start_date=start,
    #                          end_data=end)  # 创业板
    # kv['ETF-512290'] = etf512290
    # etf512660 = dp.load_bar_data('512660', 'XSHE', start_date=start,
    #                          end_data=end)  # 创业板
    # kv['ETF-512660'] = etf512660

    annual_return_cmp(etf300)
    # draw_close_price(etf300, **kv)
