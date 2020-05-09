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


def model2(symbol, alias, start_date, end_date):
    """
    定投模型2：
    1、PE处于适中估值，不做任何操作，每月定投资金放入现金池
    2、PE处于低估，持续定投
    3、PE高于适中估值，卖出并且放入现金池中
    """
    # 获取交易日价格和金融数据
    df = dp.load_bar_data(symbol, alias, start_date=start_date, end_data=end_date)
    datas = database_manager.load_finance_data(symbol + '.' + alias, start_date, end_date)
    df_finance = pd.DataFrame(columns=('code', 'datetime', 'pe', 'pb'))
    for data in datas:
        df_finance = df_finance.append({'code': data.code, 'datetime': data.datetime, 'pe': data.pe, 'pb': data.pb},
                                       ignore_index=True)
    if len(df) == len(df_finance):
        df['pe'] = df_finance['pe'].copy()
        df['pb'] = df_finance['pb'].copy()
    df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名
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
    day_df = index_df.copy()
    day_df['pct_change'] = day_df.close.pct_change()

    # day_df = day_df[['close', 'pb', 'pe' 'pct_change']]
    # print(day_df.head(10))
    miden_estimation = (12.17798, 12.93906)
    save_money = []  # 每月定存
    back_money = []  # 回收资金
    hold_money = []  # 持仓资金
    base_money = 1000  # 定投基准
    for i in range(len(day_df)):
        pe = day_df['pe'][i]  # 估值位
        print(pe)
        if i == 0:  # 初始买入
            # 1.计算买入金额
            save_money.append(base_money)
            # 2. 计算回收金额
            back_money.append(0)
            # 3. 计算持仓变化
            hold_money.append(base_money)
            continue

        if pe <= miden_estimation[0]:  # 执行买入计算
            # 1.计算买入金额
            save_money.append(base_money)
            # 2. 计算回收金额
            back_money.append(0)
            # 3. 计算持仓变化
            hold_money.append(hold_money[-1] * (1 + day_df['pct_change'][i]) + base_money)
        elif pe >= miden_estimation[-1]:  # 执行卖出计算
            # 1. 计算买入金额
            save_money.append(0)
            # 2. 计算回收金额
            back_money.append(base_money)
            # 3. 计算持仓变化
            hold_money.append(hold_money[-1] * (1 + day_df['pct_change'][i]) - base_money)
        else:
            # 1.计算买入金额
            save_money.append(0)
            # 2. 计算回收金额
            back_money.append(0)
            # 3. 计算持仓变化
            hold_money.append(hold_money[-1] * (1 + day_df['pct_change'][i]))

    day_df['save_money'] = save_money  # 定投金额
    day_df['save_money_cumsum'] = day_df['save_money'].cumsum()  # 定投累计金额
    day_df['hold_money'] = hold_money  # 持仓金额
    day_df['back_money'] = back_money  # 回收金额
    day_df['back_money_cumsum'] = day_df['back_money'].cumsum()  # 累计回收金额
    day_df['total_money'] = day_df['hold_money'] + day_df['back_money_cumsum']  # 总资金
    day_df['return_money'] = day_df['total_money'] - day_df['save_money_cumsum']  # 持续收益
    day_df['return_rate'] = (day_df['total_money'] / day_df['save_money_cumsum']) - 1  # 持续收益率
    day_df[['save_money_cumsum', 'total_money', 'back_money_cumsum', 'return_money']].plot(figsize=(14, 7))
    plt.legend(['save_money_cumsum', 'total_money', 'back_money_cumsum', 'return_money'])
    plt.show()

    print('累计投入: {}元'.format(day_df['save_money_cumsum'][-1]))
    print('累计收益: {}元'.format(day_df['return_money'][-1]))
    print('最终本息累积: {}元'.format(day_df['total_money'][-1]))
    print('绝对收益率为: {}%'.format((day_df['return_money'][-1] / day_df['save_money_cumsum'][-1]) * 100))


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


def draw_price_pe(symbol, alias, start_date, end_date):
    """画出价格与pe关系"""
    df = dp.load_bar_data(symbol, alias, start_date=start_date, end_data=end_date)
    datas = database_manager.load_finance_data(symbol + '.' + alias, start_date, end_date)
    df_finance = pd.DataFrame(columns=('code', 'datetime', 'pe', 'pb'))
    for data in datas:
        df_finance = df_finance.append({'code': data.code, 'datetime': data.datetime, 'pe': data.pe, 'pb': data.pb},
                                       ignore_index=True)
    if len(df) == len(df_finance):
        df['pe'] = df_finance['pe'].copy()
        df['pb'] = df_finance['pb'].copy()
    df['date'] = pd.to_datetime(df['date'])
    df.set_index(['date'], inplace=True)
    _, axs = plt.subplots(ncols=2, figsize=(14, 5))
    df[['close', 'pe']].plot(secondary_y=['pe'], ax=axs[0], alpha=.8)
    df[['close', 'pb']].plot(secondary_y=['pb'], ax=axs[1], alpha=.8)
    plt.show()


def analyze_pe_pb_dis(symbol, alias, start_date, end_date):
    """分析PE\PB分布"""
    datas = database_manager.load_finance_data(symbol + '.' + alias, start_date, end_date)
    df_finance = pd.DataFrame(columns=('code', 'datetime', 'pe', 'pb'))
    for data in datas:
        df_finance = df_finance.append({'code': data.code, 'datetime': data.datetime, 'pe': data.pe, 'pb': data.pb},
                                       ignore_index=True)

    _, axs = plt.subplots(nrows=2, ncols=2, figsize=(14, 7))
    sns.distplot(df_finance.pe, ax=axs[0][0])
    sns.boxplot(df_finance.pe, ax=axs[0][1])
    sns.distplot(df_finance.pb, ax=axs[1][0])
    sns.boxplot(df_finance.pb, ax=axs[1][1])
    # 展示PE/PB关系
    sns.jointplot(x='pb', y='pe', data=df_finance, height=7)
    # 将PE分成十个分位，查看各个分位PE数量
    pe_array = df_finance.pe.values
    value_counts = pd.cut(pe_array, 10).value_counts()
    print(value_counts)
    low = value_counts[0:4].sum()
    medin = value_counts[4:6].sum()
    high = value_counts[6:10].sum()
    print('比值({}：{}：{})'.format(low, medin, high))
    plt.figure(figsize=(14, 4))
    sns.barplot(x=np.arange(0, len(value_counts)), y=value_counts.values)
    plt.show()


def show_quantile(symbol, alias, start_date, end_date):
    """展示分位区间"""
    datas = database_manager.load_finance_data(symbol + '.' + alias, start_date, end_date)
    df_finance = pd.DataFrame(columns=('code', 'datetime', 'pe', 'pb'))
    for data in datas:
        df_finance = df_finance.append({'code': data.code, 'datetime': data.datetime, 'pe': data.pe, 'pb': data.pb},
                                       ignore_index=True)

    _df = pd.DataFrame()
    df = df_finance.copy()
    df.index.name = None
    _df['pe'] = df.pe
    _df = _df
    p_high = [_df.pe.quantile(i / 10) for i in [4, 5, 6]]
    for p_h, i in zip(p_high, [4, 5, 6]):
        _df[str(i / 10 * 100) + '%'] = p_h

    print(_df.head(10))
    _df['datetime'] = df_finance.datetime.copy()
    _df['datetime'] = pd.to_datetime(_df['datetime'])  # 转换时间类型
    _df.set_index(['datetime'], inplace=True)

    _df.plot(figsize=(14, 7))
    plt.show()


def dym_quantile(n):
    """
        动态分位图
        当前投资已5年内历史数据计算百分位，价格合适购入
    """
    # 这里的计算按一年244个交易日计算
    windows = int(n * 244)  # 将时间取整数
    start_date = dt.datetime(2006, 1, 1)
    end_date = dt.datetime(2020, 4, 1)
    df = dp.load_bar_data('000300', 'XSHG', start_date=start_date, end_data=end_date)
    df_finance = dp.load_finance_data('000300.XSHG', start_date=start_date, end_date=end_date)
    if len(df) == len(df_finance):
        print('yes!!!, len:%s' % len(df))
        df['pe'] = df_finance['pe']
    df['quantile'] = df_finance['pe'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                                       pd.Series(x).shape[0], raw=True)
    # df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    # df.set_index(['date'], inplace=True)
    # df.index.name = None  # 去掉索引列名
    df.dropna(inplace=True)

    # 画出适中估值区间

    # plt.figure()
    # 创建第一个画板
    fig = plt.figure(figsize=(16, 9))

    host = HostAxes(fig, [0.15, 0.1, 0.65, 0.8])
    par1 = ParasiteAxes(host, sharex=host)
    par2 = ParasiteAxes(host, sharex=host)
    host.parasites.append(par1)
    host.parasites.append(par2)

    host.set_xlabel('Date')
    host.set_ylabel('Close')
    host.axis['right'].set_visible(False)

    par1.axis['right'].set_visible(True)
    par1.set_ylabel('%sY Rolling quantile' % n)
    par1.axis['right'].major_ticklabels.set_visible(True)
    par1.axis['right'].label.set_visible(True)

    par2.set_ylabel('PE')
    new_axisline = par2.get_grid_helper().new_fixed_axis  # "_grid_helper"与"get_grid_helper()"等价，可以代替
    par2.axis['right2'] = new_axisline(loc='right', axes=par2, offset=(45, 0))

    fig.add_axes(host)

    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(lambda x: dates.date2num(x))
    p1, = host.plot(df['date'], df['close'], label="Close")
    p2, = par1.plot(df['date'], df['quantile'], label="Quantile")
    p3, = par2.plot(df['date'], df['pe'], label="PE")

    host.legend()
    # 轴名称，刻度值的颜色
    host.axis['left'].label.set_color(p1.get_color())
    host.xaxis.set_major_locator(ticker.MaxNLocator(math.floor(len(df) / 100)))
    host.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m'))
    par1.axis['right'].label.set_color(p2.get_color())
    par2.axis['right2'].label.set_color(p3.get_color())
    par2.axis['right2'].major_ticklabels.set_color(p3.get_color())  # 刻度值颜色
    par2.axis['right2'].set_axisline_style('-|>', size=1.5)  # 轴的形状色
    par2.axis['right2'].line.set_color(p3.get_color())  # 轴的颜色
    # ax.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d'))

    # df[['quantile', 'close']].plot(secondary_y=['quantile'], figsize=(14, 10), alpha=.8)
    # plt.fill_between(df.index, y1=0.4, y2=0.6, color='blue', alpha=0.7)
    # plt.fill_between(df.index, y1=0.8, y2=1, color='red', alpha=0.7)
    # plt.fill_between(df.index, y1=0.0, y2=0.2, color='green', alpha=0.7)
    # plt.annotate('reasonable zone', (df.index[-1], 0.5))
    # 画出固定PE与收盘价的曲线
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
    # draw_pe_pb('000300.XSHG', dt.datetime(2020, 1, 1), dt.datetime(2020, 4, 1))
    # draw_price_pe('000300', 'XSHG', dt.datetime(2014, 1, 2), dt.datetime(2020, 4, 1))
    # analyze_pe_pb_dis('000300', 'XSHG', dt.datetime(2014, 1, 2), dt.datetime(2020, 4, 1))
    # show_quantile('000300', 'XSHG', dt.datetime(2014, 1, 2), dt.datetime(2020, 4, 1))
    # model2('000300', 'XSHG', dt.datetime(2014, 1, 2), dt.datetime(2020, 4, 1))
    dym_quantile(7.5)