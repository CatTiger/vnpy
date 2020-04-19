import datetime as dt

import matplotlib.dates as dates
import matplotlib.pyplot as plt
import pandas as pd
import pylab
from matplotlib import ticker
from mplfinance.original_flavor import candlestick_ohlc
from pandas import DataFrame

import vnpy.analyze.data.data_prepare as dp
import vnpy.analyze.view.view_util as vutil
from vnpy.trader.constant import Direction
from vnpy.trader.utility import round_to
import math

slow_ma = 5
fast_ma = 10


def draw(days: DataFrame, trades=None):
    """作图"""
    days['date'] = pd.to_datetime(days['date'])
    days['date'] = days['date'].apply(lambda x: dates.date2num(x))

    # drop the date index from the dataframe & make a copy
    days_reshape = days.reset_index()
    days_reshape.drop('volume', axis=1, inplace=True)

    days_reshape = days_reshape.reindex(columns=['date', 'open', 'high', 'low', 'close'])

    fig = plt.figure(facecolor='#07000d', figsize=(days.__len__() * 0.1, 10))

    ax = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4)
    ax.set_facecolor('#07000d')
    candlestick_ohlc(ax, days_reshape.values, width=.6, colorup='#ff1717', colordown='#53c156')

    # 添加均线
    short_rolling = days_reshape.close.rolling(window=slow_ma).mean()
    long_rolling = days_reshape.close.rolling(window=fast_ma).mean()
    SP = len(days_reshape.date.values[fast_ma - 1:])
    ax.plot(days_reshape.date.values[-SP:], short_rolling[-SP:], '#e1edf9', label=str(slow_ma) + 'SMA', linewidth=1.5)
    ax.plot(days_reshape.date.values[-SP:], long_rolling[-SP:], '#4ee6fd', label=str(fast_ma) + 'SMA', linewidth=1.5)

    # 样式设置
    ax.grid(True, color='w')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(math.floor(days_reshape.__len__() / 22)))
    ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))
    ax.yaxis.label.set_color("w")
    ax.spines['bottom'].set_color("#5998ff")
    ax.spines['top'].set_color("#5998ff")
    ax.spines['left'].set_color("#5998ff")
    ax.spines['right'].set_color("#5998ff")
    ax.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(prune='upper'))
    ax.tick_params(axis='x', colors='w')
    ax.set_ylabel('Stock price and Volume')

    # 1、绘制成交量
    volumeMin = 0
    ax1v = ax.twinx()
    ax1v.fill_between(days.date.values, volumeMin, days.volume.values, facecolor='#00ffe8',
                      alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    # Edit this to 3, so it's a bit larger
    ax1v.set_ylim(0, 3 * days.volume.values.max())
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

    # 2、绘制RSI
    maLeg = plt.legend(loc=9, ncol=2, prop={'size': 7},
                       fancybox=True, borderaxespad=0.)
    maLeg.get_frame().set_alpha(0.4)
    textEd = pylab.gca().get_legend().get_texts()
    pylab.setp(textEd[0:5], color='w')

    ax0 = plt.subplot2grid((6, 4), (0, 0), sharex=ax, rowspan=1, colspan=4)
    ax0.set_facecolor('#07000d')

    rsi = vutil.relative_strength_index(days_reshape, 5)['RSI_5']
    rsiCol = '#c1f9f7'
    posCol = '#386d13'
    negCol = '#8f2020'

    ax0.plot(days_reshape.date.values[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
    ax0.axhline(70, color=negCol)
    ax0.axhline(30, color=posCol)
    ax0.fill_between(days_reshape.date.values[-SP:], rsi[-SP:], 70, where=(rsi[-SP:] >= 70), facecolor=negCol,
                     edgecolor=negCol, alpha=0.5)
    ax0.fill_between(days_reshape.date.values[-SP:], rsi[-SP:], 30, where=(rsi[-SP:] <= 30), facecolor=posCol,
                     edgecolor=posCol, alpha=0.5)
    ax0.set_yticks([30, 70])
    ax0.yaxis.label.set_color("w")
    ax0.spines['bottom'].set_color("#5998ff")
    ax0.spines['top'].set_color("#5998ff")
    ax0.spines['left'].set_color("#5998ff")
    ax0.spines['right'].set_color("#5998ff")
    ax0.tick_params(axis='y', colors='w')
    ax0.tick_params(axis='x', colors='w')
    ax0.set_ylabel('RSI')

    # 2、绘制MACD
    ax2 = plt.subplot2grid((6, 4), (5, 0), sharex=ax, rowspan=1, colspan=4)
    ax2.set_facecolor('#07000d')
    fillcolor = '#00ffe8'
    nslow = 26
    nfast = 12
    nema = 9
    df = vutil.macd(days_reshape, 12, 26)
    ema9 = df['MACDsign_12_26']
    macd = df['MACD_12_26']
    ax2.plot(days_reshape.date.values[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
    ax2.plot(days_reshape.date.values[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
    # 红色填充大于0区域、绿色填充小于0区域
    ax2.fill_between(days_reshape.date.values[-SP:], macd[-SP:] - ema9[-SP:], 0, where=(macd[-SP:] - ema9[-SP:] > 0),
                     alpha=0.5, facecolor=negCol,
                     edgecolor=negCol)
    ax2.fill_between(days_reshape.date.values[-SP:], macd[-SP:] - ema9[-SP:], 0, where=(macd[-SP:] - ema9[-SP:] < 0),
                     alpha=0.5, facecolor=posCol,
                     edgecolor=posCol)
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(prune='upper'))
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')
    plt.ylabel('MACD', color='w')
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(nbins=5, prune='upper'))
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax2.set_ylabel('MACD')

    # 增加提示点
    plt.suptitle('000001.XSHG', color='w')
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax.get_xticklabels(), visible=False)

    # buy and sell annotate
    # TODO: 箭头的长度可以根据ATR确定
    if trades is not None:
        for trade in trades.values():
            info = '%s,%s,%s' % (trade.datetime.strftime("%Y/%m/%d"), round_to(trade.price, 0.01), trade.volume)
            if Direction.LONG == trade.direction:
                ax.annotate(info, xy=(dates.date2num(trade.datetime), trade.price), xycoords='data', color='yellow',
                            bbox=dict(boxstyle="round", fc="none", ec="yellow"),
                            xytext=(0, -40), textcoords='offset points', ha='center',
                            arrowprops=dict(color='yellow', arrowstyle="->"))
            if Direction.SHORT == trade.direction:
                ax.annotate(info, xy=(dates.date2num(trade.datetime), trade.price), xycoords='data', color='green',
                            bbox=dict(boxstyle="round", fc="none", ec="green"),
                            xytext=(0, 40), textcoords='offset points', ha='center',
                            arrowprops=dict(color='green', arrowstyle="->"))

    plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
    plt.show()


def draw_backtesting(his_data, trades=None):
    # his_data转dataframe
    df = pd.DataFrame(columns=('date', 'open', 'high', 'low', 'close', 'volume'))
    for data in his_data:
        df = df.append(
            {'date': data.datetime, 'open': data.open_price, 'high': data.high_price, 'low': data.low_price,
             'close': data.close_price,
             'volume': data.low_price}, ignore_index=True)
    draw(df, trades)


if __name__ == "__main__":
    # 集合竞价 get_call_auction('002594.XSHE', "2020-04-07", "2020-04-08", fields=None)
    days = dp.load_bar_data('000001', 'XSHG', start_date=dt.datetime(2013, 1, 1), end_data=dt.datetime(2020, 1, 1))
    draw(days)
