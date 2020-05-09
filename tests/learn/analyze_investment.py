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


def step4_close_percentile_pe(data, n=7, show=False):
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

    column = 'percentile_' + str(windows) + 'Y'
    df[column] = df['pe'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                                   pd.Series(x).shape[0], raw=True)
    if show:
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[['close', column]].plot(ax=ax, secondary_y=[column], figsize=(16, 9), colormap='coolwarm')
        plt.show()


if __name__ == "__main__":
    # 选取沪深300开始分析
    start_date = dt.datetime(2006, 1, 1)
    end_date = dt.datetime(2020, 4, 1)
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
    step4_close_percentile_pe(df, show=True)
