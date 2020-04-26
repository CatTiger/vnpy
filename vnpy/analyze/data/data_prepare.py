from datetime import datetime, timedelta
from jqdatasdk import *
import vnpy.trader.constant as const
from vnpy.app.cta_strategy.base import (
    INTERVAL_DELTA_MAP
)
from vnpy.trader.database import database_manager
from vnpy.trader.object import BarData, FinanceData
import pandas as pd
from typing import Sequence


def save_data_to_db(symbol, alias, count=5000):
    """数据入库"""
    auth('13277099856', '1221gzcC')
    exchange = const.Exchange.get_exchange_by_alias(alias)
    data = get_bars(symbol + '.' + alias, count, unit='1d',
                    fields=['date', 'open', 'high', 'low', 'close', 'volume'],
                    include_now=False, end_dt=None, fq_ref_date=None, df=True)
    bars = []
    for row in data.iterrows():
        data = row[1]

        bar = BarData(
            gateway_name='test',
            symbol=symbol,
            exchange=exchange,
            datetime=data.date,
            interval=const.Interval.DAILY,
            volume=data['volume'],
        )
        # open_interest: float = 0
        bar.open_price = data['open']
        bar.high_price = data['high']
        bar.low_price = data['low']
        bar.close_price = data['close']
        bars.append(bar)

    database_manager.save_bar_data(bars)


def load_bar_data(symbol, alias, start_date: datetime = None, end_data: datetime = None):
    """取出bar数据"""
    exchange = const.Exchange.get_exchange_by_alias(alias)
    interval = const.Interval.DAILY
    progress_delta = timedelta(days=30)
    total_delta = end_data - start_date
    interval_delta = INTERVAL_DELTA_MAP[interval]

    start = start_date
    end = start_date + progress_delta
    progress = 0

    df = pd.DataFrame(columns=('date', 'open', 'high', 'low', 'close', 'volume'))
    while start < end_data:
        end = min(end, end_data)  # Make sure end time stays within set range

        datas = database_manager.load_bar_data(symbol, exchange, interval, start, end)
        # data转为dataframe数据
        for i, data in enumerate(datas):
            df = df.append(
                {'date': data.datetime, 'open': data.open_price, 'high': data.high_price, 'low': data.low_price,
                 'close': data.close_price,
                 'volume': data.volume}, ignore_index=True)

        progress += progress_delta / total_delta
        progress = min(progress, 1)
        progress_bar = "#" * int(progress * 10)
        print(f"加载进度：{progress_bar} [{progress:.0%}]")

        start = end + interval_delta
        end += (progress_delta + interval_delta)

    print(f"历史数据加载完成，数据量：{df.__len__()}")
    return df


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


def save_pe_pb(df, code):
    """保存PE、PB数据"""
    finance_datas = []
    for index, row in df.iterrows():
        dt = datetime(row['date'].year, row['date'].month, row['date'].day)
        pe = get_index_pe_date(code, dt)
        pb = get_index_pb_date(code, dt)
        finance_datas.append(FinanceData(code, dt, pe, pb, 'normal'))
    database_manager.save_finance_data(finance_datas)


if __name__ == "__main__":
    # 保存pe\pb数据
    df = load_bar_data('000300', 'XSHG', start_date=datetime(2018, 1, 1), end_data=datetime(2020, 4, 1))
    save_pe_pb(df, '000300.XSHG')
    # print(const.Exchange.get_exchange_by_alias('XSHG'))
    # save_data_to_db('000001', 'XSHG', 1)
    # load_bar_data('000001', 'XSHG', start_date=datetime(2010, 1, 1), end_data=datetime(2010, 5, 1))
    # save_data_to_db('159915', 'XSHE')  # 创业板
    # save_data_to_db('510300', 'XSHG')  # 沪深300
    # save_data_to_db('510500', 'XSHG')  # 中证500
    # save_data_to_db('159901', 'XSHE')  # 深证100
    # save_data_to_db('510880', 'XSHG')  # 红利ETF
    # save_data_to_db('511010', 'XSHG')  # 国债ETF
    # save_data_to_db('518880', 'XSHG')  # 黄金ETF
    # save_data_to_db('159928', 'XSHE')  # 消费ETF
    # save_data_to_db('501018', 'XSHG')  # 原油ETF
    # save_data_to_db('513100', 'XSHG')  # 纳斯达克ETF
    # save_data_to_db('000300', 'XSHG')  #

    # df = df.append({'vol': 123}, ignore_index=True)
    # df = df.append({'vol': 123}, ignore_index=True)
    # print(df.__len__())
    # df = df.drop(0, axis=0)
    # print(df.__len__())
    # datas = load_bar_data('000001', 'XSHG', start_date=datetime(2010, 1, 1), end_data=datetime(2011, 4, 1))
    # df = pd.DataFrame()
    # emotion_p = 0
    # for index, data in datas.iterrows():
    #     df = df.append({'vol': data.volume}, ignore_index=True)
    #     # 当前量 < 6天均值 ，连续6天
    #     if df.__len__() > 6:
    #         if data.volume/df.vol.mean() - 1 < 0:
    #             emotion_p = emotion_p + 1
    #         else:
    #             emotion_p = 0
    #         df = df.drop(0, axis=0)
    #     if emotion_p > 6:
    #         print(data.date.strftime("%Y-%m-%d") + '连续5天低于平均值')
