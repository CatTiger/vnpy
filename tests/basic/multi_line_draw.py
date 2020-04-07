from datetime import datetime
from vnpy.trader.object import BarData
from jqdatasdk import *
import vnpy.trader.constant as const
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def code_bar_data(code, start_date=None, end_date=None):
    # TODO 获取bardata
    auth('13277099856', '1221gzcC')
    datas = get_bars(code, 10, unit='1d', fields=['date', 'open', 'high', 'low', 'close', 'volume']
                     , include_now=True, end_dt=datetime.now(), fq_ref_date=None, df=True)
    bars = []
    for row in datas.iterrows():
        data = row[1]

        bar = BarData(
            gateway_name='test',
            symbol=code,
            exchange=const.Exchange.SSE,
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
    return bars


def norm_bar_data(bars, score):
    """标准化bar中的价格数据"""
    if len(bars) < 1:
        raise KeyError('can not null bar data')

    res = []
    for bar in bars:
        norm_bar = BarData(
            gateway_name=bar.gateway_name,
            symbol=bar.symbol,
            exchange=bar.exchange,
            datetime=bar.datetime,
            interval=bar.interval,
            volume=bar.volume,
        )
        ratio = score / bar.close_price
        norm_bar.open_price = bar.open_price * ratio
        norm_bar.high_price = bar.high_price * ratio
        norm_bar.low_price = bar.low_price * ratio
        norm_bar.close_price = bar.close_price * ratio
        res.append(norm_bar)
    return res


def norm_bar_close_data(bars, score):
    """标准化bar中的价格数据"""
    if len(bars) < 1:
        raise KeyError('can not null bar data')

    res = []
    for bar in bars:
        ratio = score / bar.close_price
        res.append(bar.close_price * ratio)
    return res


def draw_line(start_date: datetime, end_date: datetime, etf_codes):
    pass


def code_norm_df_close(code, days, refer=10000):
    auth('13277099856', '1221gzcC')
    df = get_bars(code, days, unit='1d', fields=['date', 'open', 'high', 'low', 'close', 'volume']
                  , include_now=True, end_dt=datetime.now(), fq_ref_date=None, df=True)
    ratio = refer / df.close.iloc[0]
    df.close = df.close.apply(
        lambda price: price * ratio)
    return df


if __name__ == "__main__":
    """
    '000001.XSHG' 上证指数
    '515750.XSHG' 科技50
    '510300.XSHG' 300etf -
    '510050.XSHG' 50etf
    ‘515000.XSHG’ 科技ETF
    ‘512880.XSHG’ 证券etf
    
    '159949.XSHE' 创业板50
    '159939.XSHE' 信息技术
    
    医药类etf
    
    """
    # bars = code_bar_data('510050.XSHG')
    # print(bars)
    auth('13277099856', '1221gzcC')

    codes = ['510300.XSHG', '512880.XSHG', '512010.XSHG', '159938.XSHE']
    days = 200
    refer = 10000

    df_codes = ['date', '000001.XSHG']
    df_codes.extend(codes)
    df = pd.DataFrame(columns=(df_codes))
    auth('13277099856', '1221gzcC')
    df_1 = get_bars('000001.XSHG', days, unit='1d', fields=['date', 'open', 'high', 'low', 'close', 'volume']
                    , include_now=True, end_dt=datetime.now(), fq_ref_date=None, df=True)
    ratio = refer / df_1.close.iloc[0]
    df['000001.XSHG'] = df_1.close.apply(
        lambda price: price * ratio)
    df.date = df_1.date
    df.set_index('date', inplace=True)
    for code in codes:
        price = []
        for row in code_norm_df_close(code, days).iterrows():
            price.append(row[1].close)
        df[code] = price

    df.plot()
    plt.show()
