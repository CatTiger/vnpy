import unittest
from vnpy.analyze.util.data_source import DataSource
import datetime as dt
import vnpy.trader.constant as const
from vnpy.trader.database import database_manager
import vnpy.analyze.data.data_prepare as dp
import numpy as np


class TestDataSource(unittest.TestCase):

    def test_index_stock(self):
        """指数成分股"""
        ds = DataSource(mode='remote')
        # stocks = ds.get_index_stock(dt.datetime(2020, 5, 18), '000300.XSHG')
        # print(stocks)

    def test_pe_pb(self):
        ds = DataSource(mode='remote')
        # result = ds.get_index_finance(dt.datetime(2020, 5, 18), '000300.XSHG')
        # print(result)

    def test_save_finance(self):
        # 初始化沪深300所有数据
        ds = DataSource(mode='remote')
        bar_datas = database_manager.load_bar_data('000300', const.Exchange.get_exchange_by_alias('XSHG'),
                                                   const.Interval.DAILY, dt.datetime(2010, 1, 1),
                                                   dt.datetime(2011, 1, 10))
        trade_dates = []
        for bar in bar_datas:
            trade_dates.append(bar.datetime)
        ds.save_index_finance(trade_dates, '000300.XSHG')