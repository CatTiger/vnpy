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
        # 大盘
        # save_data_to_db('000300', 'XSHG')  # 沪深300 DONE
        # save_data_to_db('399006', 'XSHE')  # 创业板指 DONE
        # save_data_to_db('000016', 'XSHG')  # 上证50 DONE
        # save_data_to_db('000905', 'XSHG')  # 中证500 DONE
        # 行业
        # save_data_to_db('000913', 'XSHG')  # 300医药 2007-07-02 DONE 512010
        # save_data_to_db('000932', 'XSHG')  # 中证消费 2009-07-03 DONE 159928
        # save_data_to_db('399437', 'XSHE')  # 国证证券行业指数 2014-12-30 DONE 512880
        # save_data_to_db('399967', 'XSHE')  # 中证军工 2013-12-26 DONE 512660
        # save_data_to_db('399986', 'XSHE')  # 中证银行指数 2014-12-30 DONE 512800
        # save_data_to_db('000015', 'XSHG')  # 红利指数 2005-01-04 DONE 510880
        # save_data_to_db('000018', 'XSHG')  # 180金融 2007-12-10 DONE 510230

        # 国债
        # save_data_to_db('000012', 'XSHG')  # 国债指数 2003-01-02

        symbol, alias = '000905', 'XSHG'
        ds = DataSource(mode='remote')
        bar_datas = database_manager.load_bar_data(symbol, const.Exchange.get_exchange_by_alias(alias),
                                                   const.Interval.DAILY, datetime(2010, 1, 1),
                                                   datetime(2011, 1, 10))
        trade_dates = []
        for bar in bar_datas:
            trade_dates.append(bar.datetime)
        ds.save_index_finance(trade_dates, symbol + '.' + alias)

    def test_filling_recent(self):
        # symbol, alias = '000018', 'XSHG'
        # symbol, alias = '000015', 'XSHG'
        symbol, alias = '000016', 'XSHG'
        recent_days = 22
        dp.save_data_to_db(symbol, alias, recent_days)
        ds = DataSource(mode='remote')
        now = datetime.today()
        bar_datas = database_manager.load_bar_data(symbol, const.Exchange.get_exchange_by_alias(alias),
                                                   const.Interval.DAILY, now - dt.timedelta(days=recent_days),
                                                   now)
        trade_dates = []
        for bar in bar_datas:
            trade_dates.append(bar.datetime)
        ds.save_index_finance(trade_dates, symbol + '.' + alias)
