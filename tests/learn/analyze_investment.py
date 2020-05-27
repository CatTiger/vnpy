import numpy as np
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import seaborn as sns
import vnpy.analyze.data.data_prepare as dp
from jqdatasdk import *
from vnpy.trader.database import database_manager
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
import matplotlib.dates as dates
from matplotlib import ticker
import math
from vnpy.analyze.util.cal_returns import CalReturns


def step1_draw_close(data, show=False):
    """画出收盘价的价格曲线"""
    df = data.copy()
    if show:
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df.close.plot(ax=ax, figsize=(16, 9), colormap='coolwarm')
        plt.show()


def step2_pe_pb(data, show=False):
    """画出PE、PB之间的关系"""
    df = data.copy()
    print('PE\PB的相关系数如下:\n %s' % (df[['pe', 'pb']].corr()))
    if show:
        sns.jointplot(df['pe'], df['pe'], kind='reg', height=9)
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[['pe', 'pb']].plot(ax=ax, secondary_y=['pb'], figsize=(16, 9), colormap='coolwarm')
        plt.show()


def step3_close_pe(data, pe_percentile_blow=0.4, pe_percentile_upper=0.6, show=False):
    """close与PE之间关系"""
    df = data.copy()
    print('CLOSE\PE的相关系数如下:\n %s' % (df[['close', 'pe']].corr()))
    percentile_blow = df['pe'].quantile(pe_percentile_blow)  # 4分位
    percentile_upper = df['pe'].quantile(pe_percentile_upper)  # 6分位
    print('下分为使用%s，PE值:%s, 上分为使用%s，PE值:%s' % (
        pe_percentile_blow, percentile_upper, pe_percentile_upper, percentile_upper))
    if show:
        sns.jointplot(df['close'], df['pe'], kind='reg', height=9)
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[['close', 'pe']].plot(ax=ax, secondary_y=['pe'], figsize=(16, 9), colormap='coolwarm')
        plt.axhline(y=percentile_blow, color='g', linestyle='-')
        plt.axhline(y=percentile_upper, color='r', linestyle='-')
        plt.show()


def step4_close_percentile_pe(data, n=7, show=False, show_p_hist=False):
    """
        close与PE百分位之间关系
        不同时期之间的PE对比已经发生巨大变化，根据一个周期内百分位对比更有价值
    """
    df = data.copy()
    # 这里的计算按一年244个交易日计算
    windows = int(n * 244)  # 将时间取整数
    if len(data) < windows:
        print('当前数据小于滚动窗口设置，无法完成滚动分为计算')
        return

    column = 'percentile_' + str(n) + 'Y'
    df[column] = df['pe'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                           pd.Series(x).shape[0], raw=True)
    if show:
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[['close', column]].plot(ax=ax, secondary_y=[column], figsize=(16, 9), colormap='coolwarm')
        plt.show()
    if show_p_hist:
        """动态百分位分布，直方图"""
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[column].hist(ax=ax, figsize=(16, 9))
        plt.show()
    return df


def first_trade_date_in_month(df):
    """找到每个月第一个交易日"""
    month_first_date = set()
    pre_year, pre_month = 0, 0
    for index, row in df.iterrows():
        if pre_year != index.year or pre_month != index.month:
            month_first_date.add(index)
        pre_year = index.year
        pre_month = index.month
    return month_first_date


def trade_model(data, column='percentile_7Y', show=False, show_annual_invest=True):
    """
    交易模型：
    1、低估：买入、适中：保持不变、高估：卖出
    """
    df = data.copy()
    # 去除无滚动百分位数据
    df.dropna(inplace=True)
    # 找每个月第一个交易日
    month_first_date = first_trade_date_in_month(df)
    # 假设每个月第一个交易日增加5000元可支配
    month_invest_const = 5000
    available_cash = 0  # 可用资金
    stock_q = 0  # 股票数量（为计算方便，可以使用小数表示）
    # 图形展示数据：累计投入、当前持有股票资产、变现回报
    trade_date = []
    invest_cash = []
    stock_assets = []
    return_cash = []

    # 买入记录
    trades = {}
    df_return = pd.DataFrame(columns=('date', 'invest', 'stock', 'return'))
    for index, row in df.iterrows():
        # 首先还是遵守标准定投思想，投还是不投，不考虑投多少问题。卖出的资产直接入袋为安，不参与定投
        trade_date.append(index)
        if month_first_date.__contains__(index):
            # available_cash = available_cash + month_invest_const
            # 当月不投下月自动清空
            available_cash = month_invest_const
        if row[column] < 0.4 and available_cash > 0:
            # 较低估值区间, 买入
            afford_q = available_cash / row['close']
            stock_q += afford_q
            invest_cash.append(available_cash)
            trades[index] = available_cash  # 加入买入记录
            available_cash = 0
            return_cash.append(0)
        elif row[column] > 0.6 and stock_q > 0:
            # 过高估值区间, 卖出
            selled_p = month_invest_const / row['close']  # 卖掉份数
            stock_q = stock_q - selled_p
            invest_cash.append(0)
            return_cash.append(month_invest_const)
        else:
            # 不做任何操作
            invest_cash.append(0)
            return_cash.append(0)
        stock_assets.append(stock_q * row['close'])
    df_return['date'] = trade_date
    df_return['invest'] = invest_cash
    df_return['stock'] = stock_assets
    df_return['return'] = return_cash
    df_return['invest_cumsum'] = df_return['invest'].cumsum()
    df_return['return_cumsum'] = df_return['return'].cumsum()
    df_return['hold'] = df_return['return_cumsum'] + df_return['stock']
    # 设置data为index
    df_return['date'] = pd.to_datetime(df_return['date'])  # 转换时间类型
    df_return.set_index(['date'], inplace=True)
    df_return.index.name = None  # 去掉索引列名
    df_return['close'] = df['close']
    print(df_return.head())
    # 计算年化收益
    earings = CalReturns.annual_returns(trades, df_return.index[-1], df_return['hold'][-1])
    print('年化收益率：%s' % earings)
    if show:
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df_return[['invest_cumsum', 'hold', 'close']].plot(ax=ax, secondary_y=['close'], figsize=(16, 9),
                                                           colormap='coolwarm')
        plt.show()
    if show_annual_invest:
        """展示年度投入与收益, 📊柱状图 （年度投入、年度剩余））"""
        trade_year = [date.year for date in trade_date]
        df_g = pd.DataFrame(columns=('date', 'invest'))
        df_g['date'] = trade_year
        df_g['invest'] = invest_cash
        df_view = df_g.groupby('date').sum()  # group by
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df_view[['invest']].plot(ax=ax, figsize=(16, 9), kind='bar')
        plt.show()


if __name__ == "__main__":
    # 选取沪深300开始分析
    start_date = dt.datetime(2005, 5, 1)
    end_date = dt.datetime(2020, 5, 1)
    df = dp.load_bar_data('000300', 'XSHG', start_date=start_date, end_data=end_date)
    df_finance = dp.load_finance_data('000300.XSHG', start_date=start_date, end_date=end_date)
    if len(df) == len(df_finance):
        print('load data success, len:%s' % len(df))
    df['pe'] = df_finance['pe']
    df['pb'] = df_finance['pb']
    # 设置data为index
    df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名
    # step1_draw_close(df, show=True)
    # step2_pe_pb(df, show=True)  # PE\PB相关系数接近1，选取其中一个即可
    # step3_close_pe(df, show=True)  # 拉长时间周期看来,无法固定确定的PE低估值，考虑使用PE历史百分位进行
    df_q = step4_close_percentile_pe(df, show=True, show_p_hist=True)
    trade_model(df_q, show=True, show_annual_invest=True)
