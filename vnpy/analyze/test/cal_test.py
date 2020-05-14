import unittest

from vnpy.analyze.util.cal_returns import CalReturns
import pandas as pd
from sympy import *


class TestDict(unittest.TestCase):
    def test_cal_annual_returns(self):
        trades = {pd.Timestamp('2018-01-01'): 5000, pd.Timestamp('2018-05-01'): 5000}
        end_dates = pd.Timestamp('2019-01-01')
        end_cash = 15000
        expression = CalReturns.cal_annual_returns(trades, end_dates, end_cash)
        print(expression)
        x = Symbol('x')
        # TODO: 计算过于耗时，使用年化1% 迭代到 100%,尝试找出最合适的值
        print(solve(expression, x))

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