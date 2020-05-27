import vnpy.analyze.data.data_prepare as dp
import numpy as np
import pandas as pd
import datetime as dt
import time
import matplotlib.pyplot as plt
import seaborn as sns
import vnpy.analyze.data.data_prepare as dp
from jqdatasdk import *
from vnpy.trader.database import database_manager


def dashboard_0(start_date, end_date):
    """
        沪深300的收盘价与PE对比
        根据相关性对比沪深300与上证指数的收盘价相关系数接近1.0
    """
    df = pd.DataFrame(columns=['date', 'close', 'pe'])
    df_bar = dp.load_bar_data('000016', 'XSHG', start_date=start_date, end_data=end_date)
    df_finance = dp.load_finance_data('000016.XSHG', start_date=start_date, end_date=end_date)
    if len(df_bar) == len(df_finance):
        print('yes!!!')
    df.date = df_bar['date']
    df.close = df_bar['close']
    df.pe = df_finance['pe']
    print(df.head())
    df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名
    plt.style.use('seaborn-white')
    df[['close', 'pe']].plot(secondary_y=['pe'], alpha=.8)
    plt.show()


def dashboard_1(start_date, end_date):
    """大盘基础走势对比图"""
    kv = {'399001': 'XSHE', '399006': 'XSHE', '000300': 'XSHG', '399005': 'XSHE', '000016': 'XSHG'}

    df = dp.load_bar_data('000001', 'XSHG', start_date=start_date, end_data=end_date)
    columns = [k + '.' + v for k, v in kv.items()]
    columns.append('date')

    df_combine = pd.DataFrame(columns=tuple(columns))
    for symbol, alias in kv.items():
        data = dp.load_bar_data(symbol, alias, start_date=start_date, end_data=end_date)
        if len(df) == len(data):
            df_combine[symbol + '.' + alias] = data.close
        else:
            print('data not match, code:%s' % (symbol + '.' + alias))
    df_combine['benchmark'] = df.close
    df_combine['date'] = df['date']
    # print(df_combine.head())
    df_combine['date'] = pd.to_datetime(df_combine['date'])  # 转换时间类型
    df_combine.set_index(['date'], inplace=True)
    df_combine.index.name = None  # 去掉索引列名
    plt.style.use('seaborn-white')
    _, axs = plt.subplots(nrows=3, ncols=2, figsize=(14, 7))
    df_combine[['399001.XSHE', 'benchmark']].plot(secondary_y=['benchmark'], ax=axs[0][0], alpha=.8)
    df_combine[['399006.XSHE', 'benchmark']].plot(secondary_y=['benchmark'], ax=axs[0][1], alpha=.8)
    df_combine[['000300.XSHG', 'benchmark']].plot(secondary_y=['benchmark'], ax=axs[1][0], alpha=.8)
    df_combine[['399005.XSHE', 'benchmark']].plot(secondary_y=['benchmark'], ax=axs[1][1], alpha=.8)
    df_combine[['000016.XSHG', 'benchmark']].plot(secondary_y=['benchmark'], ax=axs[2][0], alpha=.8)
    plt.show()


def dashboard_2(start_date, end_date):
    """大盘与其对应的PE数据进行对比"""
    """大盘基础走势对比图"""
    kv = {'399001': 'XSHE', '399006': 'XSHE', '000300': 'XSHG', '399005': 'XSHE', '000016': 'XSHG'}

    columns = []
    close = [k + '.' + v + '.close' for k, v in kv.items()]
    pe = [k + '.' + v + '.pe' for k, v in kv.items()]
    columns.extend(close)
    columns.extend(pe)
    columns.append('date')

    df_combine = pd.DataFrame(columns=tuple(columns))
    for symbol, alias in kv.items():
        code = symbol + '.' + alias
        df = dp.load_bar_data(symbol, alias, start_date=start_date, end_data=end_date)
        df_finance = dp.load_finance_data(code, start_date=start_date, end_date=end_date)
        # 第一个遍历到的设置交易日期
        if len(df_combine['date']) == 0:
            df_combine.date = df.date
        if len(df) == len(df_finance):
            df_combine[code + '.close'] = df.close
            df_combine[code + '.pe'] = df_finance.pe
        else:
            print('data not match, code:%s' % (symbol + '.' + alias))
    # print(df_combine.head())
    df_combine['date'] = pd.to_datetime(df_combine['date'])  # 转换时间类型
    df_combine.set_index(['date'], inplace=True)
    df_combine.index.name = None  # 去掉索引列名
    plt.style.use('seaborn-white')
    _, axs = plt.subplots(nrows=3, ncols=2, figsize=(14, 7))
    df_combine[['399001.XSHE.close', '399001.XSHE.pe']].plot(secondary_y=['399001.XSHE.pe'], ax=axs[0][0], alpha=.8)
    df_combine[['399006.XSHE.close', '399006.XSHE.pe']].plot(secondary_y=['399006.XSHE.pe'], ax=axs[0][1], alpha=.8)
    df_combine[['000300.XSHG.close', '000300.XSHG.pe']].plot(secondary_y=['000300.XSHG.pe'], ax=axs[1][0], alpha=.8)
    df_combine[['399005.XSHE.close', '399005.XSHE.pe']].plot(secondary_y=['399005.XSHE.pe'], ax=axs[1][1], alpha=.8)
    df_combine[['000016.XSHG.close', '000016.XSHG.pe']].plot(secondary_y=['000016.XSHG.pe'], ax=axs[2][0], alpha=.8)
    plt.show()


def dashboard_3():
    """
    选取以下三个标的对比之间关系
    沪深300 000300.XSHE （从价格的相关系数上看与上证指数、深圳成指相关系数基本一致）
    创业板 399006.XSHE（从价格的相关系数上看与中小板指相关系数基本一致）
    上证50 000016.XSHG（）
    1、PE与价格关系
    2、滚动PE百分位与价格关系
    :return:
    """


def relation_view(index_code, etf_code, days=220):
    """
    :param index_code: 指数code
    :param etf_code: etfcode
    :param days: 对比时长
    查看相关性
    :return:
    """
    auth('13277099856', '1221gzcC')
    df = get_bars(index_code, days, unit='1d',
                  fields=['date', 'close'],
                  include_now=False, end_dt=None, fq_ref_date=None, df=True)
    df_etf = get_bars(etf_code, days, unit='1d',
                      fields=['date', 'close'],
                      include_now=False, end_dt=None, fq_ref_date=None, df=True)
    df['close-etf'] = df_etf['close']
    sns.jointplot(df['close'], df['close-etf'], kind='reg', height=9)
    fig, ax = plt.subplots(1, figsize=(16, 9))
    df[['close', 'close-etf']].plot(ax=ax, secondary_y=['close-etf'], figsize=(16, 9))
    print(df[['close', 'close-etf']].corr())
    plt.show()


if __name__ == "__main__":
    """
    上证指数（1991-12-31，SH:000001）('000001', 'XSHG')
    深证成指（1994-12-30，SZ:399001）('399001', 'XSHE')
    
    创业板指（2010-6-30，SZ:399006）('399006', 'XSHE')
    沪深300(2005-2-18, SH:000300)('000300', 'XSHG') （大盘股）
    
    中小板指(2006-1-25，SZ:399005)('399005', 'XSHE')
    上证50(2004-1-30，SH:000016)('000016', 'XSHG')
    
    中证500 000905.XSHG 159922 （中小盘） 
    
    宽基
    沪深300(2005-2-18, SH:000300)('000300', 'XSHG')
    创业板指（2010-6-30，SZ:399006）('399006', 'XSHE')
    上证50(2004-1-30，SH:000016)('000016', 'XSHG')
    中证500 000905.XSHG（中小盘）159922 
    
    行业
    300医药 000913.XSHG 512010
    中证消费 000932.XSHG 159928
    国证证券行业指数 399437.XSHE 512880
    中证军工 399967.XSHE 512660
    中证银行指数 399986.XSHE 512800
    红利指数 000015.XSHG 510880
    180金融 000018.XSHG 510230 (一般)
    
    国证新能源汽车指数 399417.XSHE 515030 （不匹配）
    国证通信 399389.XSHE 515880（不匹配）
    科技100 399339.XSHE 515000（不匹配）
    """
    # 准备数据
    # start_date = dt.datetime(2006, 1, 1)
    # end_date = dt.datetime(2020, 5, 1)
    # dashboard_0(start_date, end_date)
    # relation_view('000913.XSHG', '512010.XSHG')
    # relation_view('000932.XSHG', '159928.XSHE')
    # relation_view('399437.XSHE', '512880.XSHG')
    # relation_view('399967.XSHE', '512660.XSHG')
    # relation_view('399986.XSHE', '512800.XSHG')
    # relation_view('000018.XSHG', '510230.XSHG')
    # relation_view('399417.XSHE', '515030.XSHG', 50)
    # relation_view('000015.XSHG', '510880.XSHG')
