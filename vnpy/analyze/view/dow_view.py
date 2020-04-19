import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import ticker
import vnpy.analyze.data.data_prepare as dp


def draw(data1, data2):
    data1['date'] = pd.to_datetime(data1['date'])
    data1['date'] = data1['date'].apply(lambda x: mdates.date2num(x))

    data2['date'] = pd.to_datetime(data2['date'])
    data2['date'] = data2['date'].apply(lambda x: mdates.date2num(x))

    sns.set(style='darkgrid', context='talk', palette='Dark2')

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.plot(data1.date, data1.close, label='SH Close Price')
    ax.plot(data2.date, data2.close, label='SZ Close Price')

    ax.legend(loc='best')
    ax.set_ylabel('Price')
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
    benchmark = dp.load_bar_data('510300', 'XSHG', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 12, 1))

    kv = {}
    etf159915 = dp.load_bar_data('159915', 'XSHE', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 12, 1))
    kv['ETF-159915'] = etf159915
    etf510500 = dp.load_bar_data('510500', 'XSHG', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 12, 1))
    kv['ETF-510500'] = etf510500
    etf510880 = dp.load_bar_data('510880', 'XSHG', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 12, 1))
    kv['ETF-510880'] = etf510880
    etf518880 = dp.load_bar_data('518880', 'XSHG', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 12, 1))
    kv['ETF-518880'] = etf518880
    etf159928 = dp.load_bar_data('159928', 'XSHE', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 12, 1))
    kv['ETF-159928'] = etf159928

    draw_close_price(benchmark, **kv)
    # draw(benchmark, etf159928)
    # data2 = dp.load_bar_data('399005', 'XSHE', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 1, 1))
    # print(data1.close.mean())
    # draw(data1, data2)
    # draw_close_price(data1)
