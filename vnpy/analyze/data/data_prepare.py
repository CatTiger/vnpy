from datetime import datetime, timedelta
from jqdatasdk import *
import vnpy.trader.constant as const
from vnpy.app.cta_strategy.base import (
    INTERVAL_DELTA_MAP
)
from vnpy.trader.database import database_manager
from vnpy.trader.object import BarData
import pandas as pd


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
                 'volume': data.low_price}, ignore_index=True)

        progress += progress_delta / total_delta
        progress = min(progress, 1)
        progress_bar = "#" * int(progress * 10)
        print(f"加载进度：{progress_bar} [{progress:.0%}]")

        start = end + interval_delta
        end += (progress_delta + interval_delta)

    print(f"历史数据加载完成，数据量：{df.__len__()}")
    return df


if __name__ == "__main__":
    # print(const.Exchange.get_exchange_by_alias('XSHG'))
    # save_data_to_db('000001', 'XSHG', 1)
    load_bar_data('000001', 'XSHG', start_date=datetime(2010, 1, 1), end_data=datetime(2010, 5, 1))
