import math

import matplotlib.dates as dates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker
from mplfinance.original_flavor import candlestick_ohlc
import vnpy.analyze.view.view_util as vutil
from vnpy.analyze.util.support_resistence import SupportResistanceLine


class MainView:

    def __init__(self, df):
        """
        required columns
        date,open,high,low,close
        :param df:
        """
        self.df = df

    def draw_main(self):
        df = self.df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].apply(lambda x: dates.date2num(x))

        days_reshape = df.reset_index()
        days_reshape.drop('volume', axis=1, inplace=True)
        days_reshape = days_reshape.reindex(columns=['date', 'open', 'high', 'low', 'close'])

        fig = plt.figure(figsize=(16, 9))
        ax = plt.subplot2grid((6, 4), (0, 0), rowspan=4, colspan=4)
        # 1、bar主图
        candlestick_ohlc(ax, days_reshape.values, width=.6, colorup='#db3f3f', colordown='#77d879')
        # ax.set_xticks([])
        plt.gca().axes.get_xaxis().set_visible(False)

        # 1.1、添加均线
        slow_ma, fast_ma = 10, 30
        short_rolling = days_reshape.close.rolling(window=slow_ma).mean()
        long_rolling = days_reshape.close.rolling(window=fast_ma).mean()
        ax.plot(days_reshape.date.values[slow_ma:-1], short_rolling[slow_ma:-1], '#ff9900',
                label=str(slow_ma) + 'SMA',
                linewidth=1)
        ax.plot(days_reshape.date.values[slow_ma:-1], long_rolling[slow_ma:-1], '#0000ff',
                label=str(fast_ma) + 'SMA',
                linewidth=1)

        # 1.2 支撑、阻力
        support_line = SupportResistanceLine(df.close, 'support')
        support_df = support_line.find_points()
        support_df['date'] = days_reshape.loc[support_df.x.tolist()]['date'].reset_index(drop=True)
        ax.scatter(support_df.date.values, support_df.y, marker='o', s=66, c='#0000ff', label='support point')
        resistance_line = SupportResistanceLine(df.close, 'resistance')
        resistance_df = resistance_line.find_points()
        resistance_df['date'] = days_reshape.loc[resistance_df.x.tolist()]['date'].reset_index(drop=True)
        ax.scatter(resistance_df.date.values, resistance_df.y, marker='x', s=66, c='#000000', label='resistance point')
        # TODO: 1.3 趋势
        ax.legend()

        # 2、成交量
        ax1v = ax.twinx()
        ax1v.fill_between(df.date.values, 0, df.volume.values, facecolor='#66ccff', alpha=.4)
        ax1v.axes.yaxis.set_ticklabels([])  # 取消共生y轴的取值单位
        ax1v.grid(False)
        ax1v.set_ylim(0, 3 * df.volume.values.max())  # 缩小成交量图中展示区间

        # 3、绘制MACD指标
        ax2 = plt.subplot2grid((6, 4), (4, 0), sharex=ax, rowspan=2, colspan=4)
        nslow, nfast, diff_dea = 26, 12, 9
        df_macd = vutil.macd(days_reshape, nfast, nslow, diff_dea)
        ax2.plot(days_reshape.date.values[nslow - 1: -1], df_macd['DIFF'][nslow - 1: -1], color='#ff9933', lw=2)
        ax2.plot(days_reshape.date.values[nslow + diff_dea - 2: -1], df_macd['DEA'][nslow + diff_dea - 2: -1],
                 color='#3366ff', lw=1)
        ax2.fill_between(days_reshape.date.values[nslow + diff_dea - 2: -1], df_macd['MACD'][nslow + diff_dea - 2: -1],
                         0,
                         where=(df_macd['MACD'][nslow + diff_dea - 2: -1] > 0),
                         alpha=0.5, facecolor='#cc3300', edgecolor='#cc3300')
        ax2.axhline(0, color='#003300', linestyle='-')
        ax2.fill_between(days_reshape.date.values[nslow + diff_dea - 2: -1], df_macd['MACD'][nslow + diff_dea - 2: -1],
                         0,
                         where=(df_macd['MACD'][nslow + diff_dea - 2: -1] < 0),
                         alpha=0.5, facecolor='#009933', edgecolor='#009933')
        for xtick in ax2.get_xticklabels():
            xtick.set_rotation(50)  # 旋转x轴
        ax2.xaxis.set_major_locator(ticker.MaxNLocator(math.floor(days_reshape.__len__() / 22)))  # x轴间隔，每月
        ax2.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))  # x轴样式
        plt.show()
