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
        # end_date = dt.datetime(2020, 4, 1)
        # mean_reversion = MeanReversion(start_date, end_date, '399006.XSHE', 'broad')
        # mean_reversion.append_expected_profit(show=True)

    def test_append_pos(self):
        start_date = dt.datetime(2006, 1, 1)
        end_date = dt.datetime(2020, 4, 1)
        mean_reversion = MeanReversion(start_date, end_date, '000300.XSHG', 'broad')
        mean_reversion.append_pos(show=True)