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


def search_best_poly(y, poly_min=1, poly_max=100, show=False):
    """
    寻找最接近的拟合次数
    :param y:
    :param poly_min:
    :param poly_max:
    :param show:
    :return:
    """
    x = np.arange(0, len(y))
    # 对原始曲线y进行窗口均线计算
    rolling_window = int(math.ceil(len(y) / 30))
    # 计算均线值
    y_roll_mean = y.rolling(rolling_window, min_periods=1).mean()
    # 度量原始y值和均线y_roll_mean的距离distance_mean
    distance_mean = np.sqrt(metrics.mean_squared_error(y, y_roll_mean))

    poly = poly_min
    while poly < poly_max:
        # 多项式拟合
        polynomial = np.polynomial.Chebyshev.fit(x, y, poly)
        y_fit = polynomial(x)
        # 拟合的多项式与原始值的距离
        distance_fit = np.sqrt(metrics.mean_squared_error(y, y_fit))
        if distance_fit < distance_mean:
            if show:
                # 原始曲线y，均线，以及拟合曲线可视化
                df = pd.DataFrame(columns=('x', 'y', 'y_roll', 'y_fit'))
                fig, ax = plt.subplots(1, figsize=(16, 9))
                df.x = x
                df.y = y
                df.y_roll = y_roll_mean
                df.y_fit = y_fit
                df.set_index(['x'], inplace=True)
                df.index.name = None  # 去掉索引列名
                df[['y', 'y_roll', 'y_fit']].plot(ax=ax, alpha=.8)
                plt.show()
            break
        poly += 1
    return poly


def search_extreme_pos(y, poly=1, show=False):
    x = np.arange(0, len(y))
    p = np.polynomial.Chebyshev.fit(x, y, poly)

    # 求导函数的根
    extreme_pos = [int(round(_.real)) for _ in p.deriv().roots()]
    extreme_pos = [_ for _ in extreme_pos if _ > 0 and _ < len(y)]

    # 通过二阶导数分拣极大值和极小值
    second_deriv = p.deriv(2)
    min_extreme_pos = []
    max_extreme_pos = []
    for pos in extreme_pos:
        if second_deriv(pos) > 0:
            min_extreme_pos.append(pos)
        elif second_deriv(pos) < 0:
            max_extreme_pos.append(pos)
    if show:
        df = pd.DataFrame(columns=('x', 'y', 'y_fit'))
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df.x = x
        df.y = y
        df.y_fit = p(x)
        df.set_index(['x'], inplace=True)
        df.index.name = None  # 去掉索引列名
        df[['y', 'y_fit']].plot(ax=ax, alpha=.8)
        ax.scatter(min_extreme_pos, [p(_) for _ in min_extreme_pos], s=50, c='g')
        ax.scatter(max_extreme_pos, [p(_) for _ in max_extreme_pos], s=50, c='r')
        plt.show()
    return min_extreme_pos, max_extreme_pos




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
    data = dp.load_bar_data('000300', 'XSHG', start_date=dt.datetime(2019, 5, 1), end_data=dt.datetime(2020, 5, 1))
    best_poly = search_best_poly(y=data.close, show=True)
    print(best_poly)
    search_extreme_pos(y=data.close, poly=best_poly, show=True)
    # data = dp.load_bar_data('510300', 'XSHG', start_date=dt.datetime(2018, 4, 1), end_data=dt.datetime(2019, 4, 16))
    # y = data.close.copy()
    # valid_poly(y, 1)
    # is_up_trend(y)
    # plt.show()
