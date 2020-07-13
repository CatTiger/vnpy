import unittest

from vnpy.analyze.util.cal_returns import CalReturns
import pandas as pd
from sympy import *


class TestDict(unittest.TestCase):
    def test_cal_annual_returns(self):
        trades = {pd.Timestamp('2015-01-01'): 50000, pd.Timestamp('2016-01-01'): 50000, pd.Timestamp('2017-01-01'): 50000}
        end_dates = pd.Timestamp('2021-01-01')
        end_cash = 192000
        result = CalReturns.annual_returns(trades, end_dates, end_cash)
        print(result)

    def test_annual_returns(self):
        print('xxx')

    def test_dataframe(self):
        trade_date = [pd.Timestamp('2018-01-01'), pd.Timestamp('2018-05-01'), pd.Timestamp('2019-06-01')]
        invest = [1, 2, 4]
        trade_year = [date.year for date in trade_date]
        df = pd.DataFrame(columns=('date', 'invest'))
        df['date'] = trade_year
        df['invest'] = invest
        result = df.groupby('date').sum()
        print(result)

    def test_return(self):
        # 预期年化收益率=分红率/PE+(1-分红率)*PB/PE，分红率统一设定为25%
        # ROE * （1-d）+ 1/PE *d ,d为分红率
        # PE 45.0994  PB 5.68441
        hong = 0.25
        pe = 45.0994
        pb = 5.68441
        print(hong/pe + 0.75*pb/pe)

    def test_pos(self):
        # abs(2 - 10 * value_total) ** 1.618
        print(abs(2 - 10 * 0.15) ** 1.618)
        print(1.9 ** 1.618)