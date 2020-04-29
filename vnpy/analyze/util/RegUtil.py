"""
拟合工具模块
"""
import math
import pandas as pd
import numpy as np
from sklearn import metrics
import datetime as dt
import vnpy.analyze.data.data_prepare as dp
import matplotlib.pyplot as plt
from statsmodels import api as sm, regression
import seaborn as sns


def valid_poly(y, poly=1):
    """
    大盘震荡程度判断
    1次拟合：大盘非常稳定
    2次拟合：大盘比较稳定
    3次拟合：大盘比较震荡
    4次拟合：大盘非常震荡
    :param y:
    :param poly:
    :return:
    """
    valid = False
    x = np.arange(0, len(y))
    # 对原始曲线y进行窗口均线计算
    rolling_window = int(math.ceil(len(y) / 4))
    # 计算均线值
    y_roll_mean = y.rolling(rolling_window, min_periods=1).mean()
    # 度量原始y值和均线y_roll_mean的距离distance_mean
    distance_mean = np.sqrt(metrics.mean_squared_error(y, y_roll_mean))

    # 多项式拟合
    polynomial = np.polynomial.Chebyshev.fit(x, y, poly)
    y_fit = polynomial(x)
    # 拟合的多项式与原始值的距离
    distance_fit = np.sqrt(metrics.mean_squared_error(y, y_fit))

    if distance_fit < distance_mean:
        valid = True
        print('valid')

    plt.style.use('fivethirtyeight')
    # plt.plot(x, y)
    # plt.plot(x, y_roll_mean)
    # plt.plot(x, y_fit)
    # plt.legend(['close', 'rolling window={}'.format(rolling_window), 'y_fit with poly:{}'.format(poly)])

    return valid


def is_up_trend(y):
    y_1 = y.copy()
    valid = valid_poly(y_1, poly=1)
    if valid:
        # 回归
        x = np.arange(0, len(y))
        # zoom:
        zoom_factor = x.max() / y.max()
        y = zoom_factor * y
        # mode:
        x = sm.add_constant(x)
        model = regression.linear_model.OLS(y, x).fit()

        intercept = model.params[0]
        rad = model.params[1]
        # y = kx + b, x取x[:, 1], 应为add_constant
        y_fit = x[:, 1] * rad + intercept
        print('rad:%s, deg:%s' % (rad, np.rad2deg(rad)))
        x_plot = x[:, -1]
        plt.plot(x_plot, y)
        plt.plot(x_plot, y_fit)
        # sns.regplot(x=x_plot, y = y)


if __name__ == '__main__':
    data = dp.load_bar_data('000300', 'XSHG', start_date=dt.datetime(2014, 11, 21), end_data=dt.datetime(2015, 3, 21))
    # data = dp.load_bar_data('510300', 'XSHG', start_date=dt.datetime(2018, 4, 1), end_data=dt.datetime(2019, 4, 16))
    y = data.close.copy()
    # valid_poly(y, 1)
    is_up_trend(y)
    plt.show()
