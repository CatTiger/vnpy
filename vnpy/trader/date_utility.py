"""
日期工具类
"""

import random
from datetime import datetime, timedelta

from vnpy.trader.database import database_manager


def all_trade_dates(fmt='%Y%m%d') -> []:
    """获取所有交易日信息"""
    result = []
    for row in database_manager.load_trade_dates():
        if row.is_open == 1:
            dt = datetime.strptime(row.cal_date, '%Y-%m-%d %H:%M:%S')
            result.append(dt.strftime(fmt))

    return result


def _random_date_str(start_ts, end_ts):
    """
    生产随机的日期字符串
    :param start_ts:
    :param end_ts:
    :return:
    """
    ts = random.randint(start_ts, end_ts)
    dt_from_ts = datetime.fromtimestamp(ts)
    return dt_from_ts.strftime('%Y%m%d')


def gen_random_date_str(start_date: datetime, end_date: datetime,
                        fetch_size=10, need_sort=True, trade_date=True) -> []:
    """
    随机生成日期字符串
    :param start_date: 开始日期
    :param end_date: 结束日期
    :param fetch_size: 随机生成的数量
    :param need_sort: 日期是否需要排序
    :param trade_date: 是否为交易日
    :return: 日期格式："%Y%m%d
    """
    starttime = start_date.timestamp()  # 生成开始时间戳
    endtime = end_date.timestamp()  # 生成结束时间戳

    trade_dates = []
    if trade_date:
        trade_dates = all_trade_dates()
    trade_dates_set = set(trade_dates)

    result = []

    counter = 0
    while counter < fetch_size:
        dt_str = _random_date_str(starttime, endtime)
        if dt_str not in trade_dates_set:
            continue
        result.append(dt_str)
        counter += 1

    if need_sort:
        result = sorted(result)
    return result


def date_cal(start_date: str, day_delta: int, fmt='%Y%m%d') -> str:
    """
    日期计算
    :param start_date: 传入日期,
    :param day_delta: 需要计算的日期
    :param fmt: 格式化
    :return:
    """
    cal_date = datetime.strptime(start_date, fmt) + timedelta(days=day_delta)
    return cal_date.strftime(fmt)

# print(all_trade_dates())
# print(date_cal('20200229', 1))
# print(gen_random_date_str(datetime(2015, 4, 19, 12, 20), datetime(2017, 4, 19, 12, 20), 10, True))
# print(len(all_trade_dates()))
# a = ['1', '2', '3']
# print(type(set(a)))
