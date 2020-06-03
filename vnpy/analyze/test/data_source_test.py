import unittest
from vnpy.analyze.util.data_source import DataSource
from datetime import datetime, timedelta
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
        # bar_datas = database_manager.load_bar_data('000300', const.Exchange.get_exchange_by_alias('XSHG'),
        #                                            const.Interval.DAILY, dt.datetime(2005, 1, 1),
        #                                            dt.datetime(2006, 1, 10))
        # trade_dates = []
        # for bar in bar_datas:
        #     trade_dates.append(bar.datetime)
        start_date = datetime.today() - timedelta(days=2)
        trade_dates = [(start_date + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0) for i in
                       range(1, 3)]
        ds.save_index_finance(trade_dates, '000300.XSHG')

    def test_init(self):
        symbol, alias = '000991', 'XSHG'
        ds = DataSource(mode='remote')
        ds.save_bar_data(symbol, alias)
        bar_datas = database_manager.load_bar_data(symbol, const.Exchange.get_exchange_by_alias(alias),
                                                   const.Interval.DAILY, datetime(2010, 1, 1),
                                                   datetime.now())
        finance_datas = []
        for bar in bar_datas:
            finance_data = ds.get_index_finance(bar.datetime, symbol + '.' + alias)
            finance_datas.append(finance_data)
            if len(finance_datas) == 50:
                database_manager.save_finance_data(finance_datas)
                finance_datas.clear()