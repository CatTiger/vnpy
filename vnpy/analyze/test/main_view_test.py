import unittest
from vnpy.analyze.view.main_view import MainView
import datetime as dt
from jqdatasdk import *
from vnpy.analyze.util.mean_reversion import MeanReversion
import vnpy.analyze.data.data_prepare as dp


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

    def test_show_all(self):
        # 沪深300为标的
        now = dt.datetime(2020, 5, 26)
        start_date = now - dt.timedelta(days=365)
        # 1、最近1年的k线数据
        df = dp.load_bar_data('000300', 'XSHG', start_date=start_date, end_data=now)
        mv = MainView(df)
        mv.draw_main()
        # 2、历史数据分析
        start_date = dt.datetime(2010, 1, 1)
        mean_reversion = MeanReversion(start_date, now, '000300.XSHG', 'broad')
        # 财务相关
        mean_reversion.append_expected_profit()
        mean_reversion.append_finance(n=7)
        mean_reversion.append_pos(show=False)
        # 价格相关
        mean_reversion.append_poly_line()
        mean_reversion.print_detail()
        mean_reversion.draw_reference()
