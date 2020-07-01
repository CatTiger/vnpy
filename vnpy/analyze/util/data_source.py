from jqdatasdk import *
from _datetime import datetime, timedelta
from vnpy.app.cta_strategy.base import (
    INTERVAL_DELTA_MAP
)
from vnpy.trader.object import FinanceData, BarData
from typing import Sequence
from vnpy.trader.database import database_manager
import vnpy.trader.constant as const
import pandas as pd


class DataSource:

    def __init__(self, mode='remote'):
        """
        初始化
        :param mode: 默认为本地模式，mode: remote远程模式
        """
        if mode == 'remote':
            # 15802720411/Mm123456789
            # auth('13277099856', '1221gzcC')
            auth('15802720411', 'Mm123456789')
            # auth('18502700256', 'LIjing218')

    def save_bar_data(self, symbol, alias, count=5000):
        """
        保存bar数据
        :param symbol:
        :param alias:
        :param count:
        :return:
        """
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
            bar.open_price = data['open']
            bar.high_price = data['high']
            bar.low_price = data['low']
            bar.close_price = data['close']
            bars.append(bar)
        database_manager.save_bar_data(bars)

    def load_bar_data(self, symbol, alias, start_date: datetime = None, end_data: datetime = None):
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

    def get_index_stock(self, date: datetime, index_code: str):
        """
        查找指数对应的成分股
        :param date: 日期
        :param index_code: 指数代码
        :return:
        """
        return get_index_stocks(index_code, date)

    def get_index_finance(self, date: datetime, index_code: str):
        """
        获取指数金融数据，PE（市值加权）、PB（市值加权）、PE（成分股中位数）、PB（成分股中位数）
        :param date: 默认为本地模式，mode: remote远程模式
        :param index_code: 默认为本地模式，mode: remote远程模式
        :return:
        """
        stocks = get_index_stocks(index_code, date)
        q = query(valuation).filter(valuation.code.in_(stocks))
        df = get_fundamentals(q, date)
        df_pe = df[df['pe_ratio'] > 0]
        df_pb = df[df['pe_ratio'] > 0]
        result = None
        if len(df_pe) > 0 and len(df_pb) > 0:
            pe = df['circulating_market_cap'].sum() / (df['circulating_market_cap'] / df['pe_ratio']).sum()
            pe_mid = df['pe_ratio'].median()
            pb = df['circulating_market_cap'].sum() / (df['circulating_market_cap'] / df['pb_ratio']).sum()
            pb_mid = df['pb_ratio'].median()
            result = FinanceData(index_code, date, pe, pb, pe_mid, pb_mid, '', 'normal')
        return result

    def save_index_finance(self, trade_dates: Sequence['datetime'], index_code: str):
        """
        保存指数金融相关信息
        :param trade_dates: 交易日
        :param index_code: 指数code
        :return:
        """
        finance_datas = []
        for date in trade_dates:
            finance_data = self.get_index_finance(date, index_code)
            if finance_data:
                finance_datas.append(finance_data)
        database_manager.save_finance_data(finance_datas)

    def init_index_base_data(self, index_code, count=5000):
        """
        初始化指数基础数据
        :param index_code: 指数代码
        :param count: 拉取数量
        :return:
        """
        print('初始化指数基础数据，code:%s' % index_code)
        ary = index_code.split('.')
        symbol = ary[0]
        exchange = const.Exchange.get_exchange_by_alias(ary[1])
        data = get_bars(index_code, count, unit='1d',
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
            bar.open_price = data['open']
            bar.high_price = data['high']
            bar.low_price = data['low']
            bar.close_price = data['close']
            bars.append(bar)
        database_manager.save_bar_data(bars)

    # def load_index_data(self, index_code: str):
    #     """
    #     拉取指数对应的数据（价格、财务信息）
    #     :param index_code: 指数代码
    #     :param start_date: 开始时间
    #     :param end_date: 结束时间
    #     :return:
    #     """
    #     ary = index_code.split('.')
    #     symbol = ary[0]
    #     exchange = const.Exchange.get_exchange_by_alias(ary[1])
    #     oldest_bar = database_manager.get_oldest_bar_data(symbol, exchange, const.Interval.DAILY)
    #     newest_bar = database_manager.get_newest_bar_data(symbol, exchange, const.Interval.DAILY)
    #     df_base = database_manager.load_bar_data(symbol, exchange, const.Interval.DAILY, oldest_bar.datetime,
    #                                              newest_bar.datetime)
    # for row in df_base:
