import datetime
from vnpy.trader.constant import IndexType
from vnpy.trader.constant import Exchange


class IndexInfo:
    """指数信息"""

    def __init__(self, index_code: str, desc: str, trace_code: str, start_date: datetime, type: IndexType,
                 cal_sr=True,
                 cal_close=True, cal_finance=True, rolling_gap_year=7):
        self.index_code = index_code
        self.symbol = index_code.split('.')[0]
        self.alias = index_code.split('.')[1]
        self.exchange = Exchange.get_exchange_by_alias(self.alias)
        self.desc = desc
        self.trace_code = trace_code
        self.start_date = start_date
        self.type = type
        self.cal_sr = cal_sr
        self.cal_close = cal_close
        self.cal_finance = cal_finance
        self.rolling_gap_year = rolling_gap_year
        if datetime.datetime.now() - start_date < datetime.timedelta(days=365 * rolling_gap_year):
            raise Exception("当前日期至指数成立时间小于滑动计算周期")
