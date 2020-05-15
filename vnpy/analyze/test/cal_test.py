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

    def test_return(self):
        # 预期年化收益率=分红率/PE+(1-分红率)*PB/PE，分红率统一设定为25%
        # ROE * （1-d）+ 1/PE *d ,d为分红率
        # PE 45.0994  PB 5.68441
        hong = 0.25
        pe = 45.0994
        pb = 5.68441
        print(hong/pe + 0.75*pb/pe)