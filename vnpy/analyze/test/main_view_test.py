import unittest
from vnpy.analyze.view.main_view import MainView
import datetime as dt
from jqdatasdk import *
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
        df = dp.load_bar_data('000001', 'XSHG', start_date=dt.datetime(2019, 5, 23), end_data=dt.datetime(2020, 5, 23))
        mv = MainView(df)
        mv.draw_main()
