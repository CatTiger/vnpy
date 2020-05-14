from vnpy.trader.utility import round_to
import math


class CalReturns:

    @staticmethod
    def cal_annual_returns(trades: {}, end_date, end_cash):
        """计算年化收益，需要交易日、金额， 截止日：金额"""
        # cash1 * (1 + x / 100)^[(end_date - self.start_date)/365] + cash2 * (1 + x / 100)^[(end_date - self.start_date)/365] = end_val
        # trades, key: date, value: cash
        expression = ''
        for date, cash in trades.items():
            td = round_to((end_date - date).days / 365, 0.001)
            expression = expression + str(cash) + '*(1 + x) **' + str(td) + '+'
        expression = expression[:-1] + '-' + str(end_cash)
        return expression

    @staticmethod
    def annual_returns(trades: {}, end_date, end_cash):
        """
        此处只考虑正年化收益，且年化收益率到100%停止搜索
        :param trades: 字典，key: date, value: cash
        :param end_date: 最终统计日期
        :param end_cash: 最终资金
        :return:
        """
        # 最简单的改造效率方式，使用二分思想
        pre_result = 0
        result = 0
        for as_annual_return in range(1, 1001):
            cal_result = 0
            for date, cash in trades.items():
                td = round_to((end_date - date).days / 365, 0.001)
                cal_result = cal_result + cash * math.pow(1 + as_annual_return / 1000, td)
            if pre_result <= end_cash <= cal_result:
                # 找到最合适的
                result = as_annual_return
                break
            else:
                pre_result = cal_result
        return str(result/10) + '%'
