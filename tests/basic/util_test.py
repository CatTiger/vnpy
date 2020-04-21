from pandas import DataFrame
import math


def normalize(numbers):
    total = sum(numbers)
    result = []
    for value in result:
        percent = 100 * value / total
        result.append(percent)
    return result


def read(data_path):
    with open(data_path) as f:
        for line in f:
            yield int(line)


def normalize_func(it):
    total = sum(it())
    result = []
    for value in it():
        percent = 100 * value / total
        result.append(percent)
    return result


dfcvs = DataFrame([
    ["2018/09/17-21:34", 3646, 3650, 3644, 3650],
    ["2018/09/17-21:35", 3650, 3650, 3648, 3648],
    ["2018/09/17-21:36", 3650, 3650, 3648, 3650],
    ["2018/09/17-21:37", 3652, 3654, 3648, 3652]])
# data_mat = dfcvs.as_matrix()
# print(data_mat)


if __name__ == "__main__":
    # 目标 1000w，，；求每周因存款金额
    annual_rate = 1.12  # 预计年化12%
    total_years = 1  # 定投年限：20
    weekly_amount = 2500  # 每月投入
    # 求周利率
    weekly_rate = math.pow(math.e, math.log(annual_rate) / 48)  # 按照每年48周，计算每周利率
    # 按照每月四周，每年48周计算，20年为48*20
    total_amount = 0 # 最终收益
    for i in range(1, 48 * total_years + 1):
        total_amount = total_amount + weekly_amount * math.pow(weekly_rate, 48 * total_years + 1 - i)
    print(total_amount)