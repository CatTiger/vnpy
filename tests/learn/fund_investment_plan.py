import numpy as np
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import seaborn as sns
import vnpy.analyze.data.data_prepare as dp
from jqdatasdk import *
from vnpy.trader.database import database_manager


def interval_show(df, forecast_start, forecast_end):
    """展示🐂顶周期"""
    plt.style.use('fivethirtyeight')
    # 1、拉取数据
    df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名

    df.close.plot(figsize=(14, 7))
    for top_date in ('2007-10-01', '2015-06-01'):
        plt.axvline(top_date, color='r', alpha=0.7)
    if forecast_start is not None and forecast_end is not None:
        # TODO: 向df中添加date数据
        # 添加预测时间到图形中
        date_span = pd.date_range(forecast_start, forecast_end)
        value_span = [df.close.max() for x in date_span]
        plt.fill_between(date_span, value_span, color='orange', alpha=0.8)

    plt.show()


def regplot_trend(df):
    """线性回归，看趋势"""
    df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名
    plt.figure(figsize=(14, 7))
    sns.regplot(x=np.arange(0, df.shape[0]), y=df.close.values)
    plt.show()


def forecast_bull_time():
    """简单预测下一次牛顶"""
    best_dates = [dt.datetime.strptime(best_date, '%Y-%m-%d').date() for best_date in
                  ('1993-02-01', '2001-06-01', '2007-10-01', '2015-06-01')]
    # 计算牛顶的平均时间
    gap_dates = [days.days for days in np.diff(best_dates)]
    print('牛顶平均间隔时间：', ['{} days'.format(day) for day in gap_dates])
    # 计算平均时间间隔
    mean_gap = np.mean(gap_dates)
    print('平均时间间隔{}天，既{}年'.format(round(mean_gap, 2), round(mean_gap / 365, 2)))
    # 再计算平均值偏差
    std_gap = np.std(gap_dates)
    print('平均时间偏差{}天，既{}年'.format(round(std_gap, 2), round(std_gap / 365, 2)))
    # 计算下一个牛市出现的合理时间区间
    early_date = best_dates[-1] + dt.timedelta(round(mean_gap - std_gap, 2))
    late_date = best_dates[-1] + dt.timedelta(round(mean_gap + std_gap, 2))
    print('下一次牛市时间预计区间 {} ~ {}'.format(early_date, late_date))
    return early_date, late_date


def model_1(df):
    """
    定投模型1
    1、每月第一个交易日定投1000
    2、不考虑买入的份额是否够一手，按照小数结算
    3、不考虑交易中的滑点和手续费相关
    """
    # 获取每个月第一个交易日
    pre_year = 0
    pre_month = 0
    first_day = []
    for index, row in df.iterrows():
        if index.year != pre_year or index.month != pre_month:
            first_day.append(index)
        pre_year = index.year
        pre_month = index.month
    index_df = df.loc[first_day]
    # 按照预定模型计算
    day_df = index_df.copy()
    day_df['pct_change'] = day_df.close.pct_change()
    day_df = day_df[['close', 'pct_change']]
    save_money = []  # 存入金额
    hold_money = []  # 拥有金额
    save_base = 1000  # 每次存入金额
    for i in range(len(day_df)):
        if i == 0:
            save_money.append(save_base)
            hold_money.append(save_base)
        else:
            save_money.append(save_money[-1] + save_base)
            hold_money.append(hold_money[-1] * (1 + day_df['pct_change'][i]) + save_base)
    day_df['save_money'] = save_money
    day_df['hold_money'] = hold_money
    day_df['return_money'] = day_df['hold_money'] - day_df['save_money']  # 累计收入
    day_df[['save_money', 'hold_money', 'return_money']].plot(figsize=(14, 7))
    plt.legend(['save_money', 'hold_money', 'return_money'])
    plt.show()
    # TODO: 增加复合年化利率计算


# 指定日期的指数PE(市值加权)
def get_index_pe_date(index_code, date):
    auth('13277099856', '1221gzcC')
    stocks = get_index_stocks(index_code, date)
    q = query(valuation).filter(valuation.code.in_(stocks))
    df = get_fundamentals(q, date)
    df = df[df['pe_ratio'] > 0]
    if len(df) > 0:
        # pe = len(df)/sum([1/p if p>0 else 0 for p in df.pe_ratio])
        # pe = df['pe_ratio'].size/(1/df['pe_ratio']).sum()
        pe = df['circulating_market_cap'].sum() / (df['circulating_market_cap'] / df['pe_ratio']).sum()
        return pe
    else:
        return float('NaN')


# 指定日期的指数PB(市值加权)
def get_index_pb_date(index_code, date):
    auth('13277099856', '1221gzcC')
    stocks = get_index_stocks(index_code, date)
    q = query(valuation).filter(valuation.code.in_(stocks))
    df = get_fundamentals(q, date)
    df = df[df['pb_ratio'] > 0]
    if len(df) > 0:
        # pb = len(df)/sum([1/p if p>0 else 0 for p in df.pb_ratio])
        # pb = df['pb_ratio'].size/(1/df['pb_ratio']).sum()
        pb = df['circulating_market_cap'].sum() / (df['circulating_market_cap'] / df['pb_ratio']).sum()
        return pb
    else:
        return float('NaN')


def draw_pe_pb(code, start_date, end_date):
    """画出pe、pb的趋势图"""
    datas = database_manager.load_finance_data(code, start_date, end_date)
    df = pd.DataFrame(columns=('code', 'datetime', 'pe', 'pb'))
    for data in datas:
        df = df.append({'code': data.code, 'datetime': data.datetime, 'pe': data.pe, 'pb': data.pb}, ignore_index=True)
    # 设置索引
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index(['datetime'], inplace=True)
    df[['pe', 'pb']].plot(figsize=(14, 7), subplots=True)
    # TODO: PE和close对比
    # df[['pe', 'pb']].plot(secondary_y=['pb'], alpha=.8)
    plt.show()


if __name__ == "__main__":
    # 获取数据
    # df = dp.load_bar_data('000300', 'XSHG', start_date=dt.datetime(2020, 1, 1),
    #                       end_data=dt.datetime(2020, 4, 1))
    # df['dt'] = df['date'].copy()
    # df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    # df.set_index(['date'], inplace=True)
    # draw_pe_pb(df, '000300.XSHG')
    # model_1(df)
    # forecast_start, forecast_end = forecast_bull_time()
    # interval_show(df, forecast_start, forecast_end)
    # regplot_trend(df)
    draw_pe_pb('000300.XSHG', dt.datetime(2020, 1, 1), dt.datetime(2020, 4, 1))
