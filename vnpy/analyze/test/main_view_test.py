import unittest
from vnpy.analyze.view.main_view import MainView
import datetime as dt
from jqdatasdk import *
from vnpy.analyze.util.mean_reversion import MeanReversion
import vnpy.analyze.data.data_prepare as dp
import pandas as pd


class TestDict(unittest.TestCase):
    def test_main_jq(self):
        auth('13277099856', '1221gzcC')
        df = get_bars('000001.XSHG', 220, unit='1d',
                      fields=['date', 'open', 'high', 'low', 'close', 'volume'],
                      include_now=False, end_dt=None, fq_ref_date=None, df=True)
        mv = MainView(df)
        mv.draw_main()

    def test_main_local(self):
        now = dt.datetime(2020, 5, 26)
        start_date = now - dt.timedelta(days=365)
        df = dp.load_bar_data('000300', 'XSHG', start_date=start_date, end_data=now)
        mv = MainView(df)
        mv.draw_main()

    def test_show_price_only(self):
        symbol, alias = '399610', 'XSHE'
        now = dt.datetime(2020, 5, 28)
        start_date = dt.datetime(2010, 1, 1)
        mean_reversion = MeanReversion(start_date, now, symbol + "." + alias, 'broad', load_finance=False)
        mean_reversion.append_poly_line(show=True)

    def test_show_all(self):
        # symbol, alias = '000016', 'XSHG'
        # symbol, alias = '000913', 'XSHG'
        # symbol, alias = '000932', 'XSHG'
        # symbol, alias = '000018', 'XSHG'
        symbol, alias = '000015', 'XSHG'
        # symbol, alias = '000015', 'XSHG'
        # symbol, alias = '000016', 'XSHG'
        now = dt.datetime(2020, 5, 30)
        start_date = now - dt.timedelta(days=365)

    def test_annual_return(self):
        mean_reversion = MeanReversion(dt.datetime(2005, 1, 1), dt.datetime.now(), '000012.XSHG',
                                       load_finance=False)
        pre_date = ''
        pre_year = 0
        pre_close = 0
        for index, row in mean_reversion.df.iterrows():
            if pre_year == 0 and pre_close == 0:
                pre_year = index.year
                pre_close = row.close
                pre_date = dt.datetime.strftime(index, "%Y-%m-%d")
            if index.year != pre_year:
                cur_date = dt.datetime.strftime(index, "%Y-%m-%d")
                print('date:%s -> date:%s, rate:%s%s, pre:%s, cur:%s' % (
                    pre_date, cur_date, round(100 * (row.close - pre_close) / pre_close, 3), '%', round(pre_close, 3),
                    round(row.close, 3)))
                pre_year = index.year
                pre_close = row.close
                pre_date = cur_date