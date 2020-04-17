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


def draw_close_price(data1):
    data1['date'] = pd.to_datetime(data1['date'])
    data1['date'] = data1['date'].apply(lambda x: mdates.date2num(x))

    sns.set(style='darkgrid', context='talk', palette='Dark2')

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.plot(data1.date, data1.close, label='SH Close Price')

    ax.legend(loc='best')
    ax.set_ylabel('Price')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(12))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.show()


if __name__ == "__main__":
    str = '4e4d6e845ab91851e3ada13781d1f24c'
    print(str[26] + str[28] + str[24] + str[5] + str[17] + str[19] + str[22] + str[23])
    # data1 = dp.load_bar_data('000001', 'XSHG', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 6, 1))
    # data2 = dp.load_bar_data('399005', 'XSHE', start_date=dt.datetime(2016, 1, 1), end_data=dt.datetime(2017, 1, 1))
    # print(data1.close.mean())
    # draw(data1, data2)
    # draw_close_price(data1)

