import unittest
from vnpy.analyze.util.mean_reversion import MeanReversion
import datetime as dt


class TestDict(unittest.TestCase):
    def test_rolling_pe_percentile(self):
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.rolling_pe_percentile(show=True, show_p_hist=True)

    def test_multi_rolling_pe_percentile(self):
        """
        000300.XSHG
        399006.XSHE
        000016.XSHG
        """
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion_300 = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion_300.rolling_pe_percentile(show=True, show_p_hist=True)
        mean_reversion_50 = MeanReversion(start_date, end_date, '000016.XSHG', 'broad')
        mean_reversion_50.rolling_pe_percentile(show=True, show_p_hist=True)
        mean_reversion_cy = MeanReversion(start_date, end_date, '399006.XSHE', 'broad')
        mean_reversion_cy.rolling_pe_percentile(show=True, show_p_hist=True)

    def test_close_pe_relation(self):
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion_cy = MeanReversion(start_date, end_date, '399006.XSHE', 'broad')
        mean_reversion_cy.close_finance_relation(show_pe_percentile=True)

    def test_close_pb_relation(self):
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.close_finance_relation(show_pb_border_line=True, column='pb')

    def test_append_expected_profit(self):
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.append_expected_profit(show=True)

    def test_append_poly_line(self):
        start_date = dt.datetime(2010, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.append_poly_line(show=True)

    def test_ema(self):
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.__append_ema(show=True)

    def test_append_finance(self):
        start_date = dt.datetime(2015, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.append_finance(n=1, show_pe=True, show_pb=True)

    def test_append_pos(self):
        start_date = dt.datetime(2015, 1, 1)
        end_date = dt.datetime(2016, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.append_finance(n=1)
        mean_reversion.append_pos(show=True)

    def test_all(self):
        start_date = dt.datetime(2010, 1, 1)
        end_date = dt.datetime(2020, 5, 21)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        # 财务相关
        mean_reversion.append_expected_profit()
        mean_reversion.append_finance(n=7)
        mean_reversion.append_pos(show=False)
        # 价格相关
        mean_reversion.append_poly_line()
        mean_reversion.print_detail()
        mean_reversion.draw_reference()
        # mean_reversion.draw_attribution_analyze()

    def test_poly(self):
        # start_date = dt.datetime(2005, 1, 1)
        # end_date = dt.datetime(2020, 5, 22)
        # mean_reversion = MeanReversion(start_date, end_date, '000001.XSHG', 'broad', load_finance=False)
        # mean_reversion.append_poly_line(show=True)
        start_date = dt.datetime(2016, 1, 1)
        end_date = dt.datetime(2020, 5, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', load_finance=False)
        mean_reversion.append_poly_line(show=True)

    def test_foo(self):
        a = abs(2 - 10 * 0.187)
        print(a, a ** 1.618)
