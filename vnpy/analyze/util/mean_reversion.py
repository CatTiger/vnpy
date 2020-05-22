from datetime import datetime
import vnpy.analyze.data.data_prepare as dp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as dates
import talib as ta
import seaborn as sns


class MeanReversion:
    """均值回复投资思路"""

    def __init__(self, start_date: datetime, end_date: datetime, code: str, subject_type: str, load_finance=True):
        """
        初始化
        :param start_date: 开始时间
        :param end_date: 结束时间
        :param code: 标识，eg: 000300.XSHG
        :param subject_type: 标的类型，目前暂定（宽基指数（broad）、行业指数（Industry））
        :param load_finance: 是否拉取金融数据
        """
        self.start_date = start_date
        self.end_date = end_date
        self.code = code
        self.subject_type = subject_type
        # 获取价格与财务数据
        code_sp = code.split('.')
        self.df = dp.load_bar_data(code_sp[0], code_sp[1], start_date=start_date, end_data=end_date)
        if load_finance:
            self.df_finance = dp.load_finance_data(code, start_date=start_date, end_date=end_date)
            if len(self.df) != len(self.df_finance):
                raise Exception("base and finance data not matching")
            self.df['pe'] = self.df_finance['pe']
            self.df['pb'] = self.df_finance['pb']
            self.df['pe_mid'] = self.df_finance['pe_mid']
            self.df['pb_mid'] = self.df_finance['pb_mid']
        # 设置data为index
        self.df['date'] = pd.to_datetime(self.df['date'])  # 转换时间类型
        self.df.set_index(['date'], inplace=True)
        self.df.index.name = None  # 去掉索引列名

    def close_finance_relation(self, show_pe_percentile=False, show_pb_border_line=False, column='pe'):
        """
        收盘价与PE关系
        :param show_pe_percentile: 是否标记PE百分位
        :param show_pb_border_line: 是否展示pb的边界线，根据齐东平的大数投资，当沪深股市整体市净率低于2倍时开始配置
        :param column: 展示字段
        :return:
        """
        df = self.df
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[['close', column]].plot(ax=ax, secondary_y=[column], figsize=(16, 9), colormap='coolwarm')
        if show_pe_percentile:
            percentile_blow = df[column].quantile(0.4)  # 4分位
            percentile_upper = df[column].quantile(0.6)  # 6分位
            print('四分位，PE值:%s, 六分位，PE值:%s' % (percentile_upper, percentile_upper))
            plt.axhline(y=percentile_blow, color='g', linestyle='-')
            plt.axhline(y=percentile_upper, color='r', linestyle='-')
        if show_pb_border_line:
            plt.axhline(y=2, color='b', linestyle='-')
        plt.show()

    def append_finance(self, n=7, show_pe=False, show_pb=False):
        """
        增加财务信息
        :param n: 历史年份， 默认7年
        :param show_pe: 是否展示PE曲线
        :param show_pb: 是否展示PB曲线
        :return:
        """
        df = self.df
        # 这里的计算按一年244个交易日计算
        windows = int(n * 244)  # 将时间取整数
        if len(df) < windows:
            raise Exception("当前数据小于滚动窗口设置，无法完成滚动分为计算")
        # PE
        df['pe_0.8'] = df['pe'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.8), raw=True)
        df['pe_0.2'] = df['pe'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.2), raw=True)
        df['pe_r'] = df['pe'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                               pd.Series(x).shape[0], raw=True)
        # PE mid
        df['pe_mid_0.8'] = df['pe_mid'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.8), raw=True)
        df['pe_mid_0.2'] = df['pe_mid'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.2), raw=True)
        df['pe_mid_r'] = df['pe_mid'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                                       pd.Series(x).shape[0], raw=True)
        # PE mid
        df['pb_0.8'] = df['pb'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.8), raw=True)
        df['pb_0.2'] = df['pb'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.2), raw=True)
        df['pb_r'] = df['pb'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                               pd.Series(x).shape[0], raw=True)
        # PE mid
        df['pb_mid_0.8'] = df['pb_mid'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.8), raw=True)
        df['pb_mid_0.2'] = df['pb_mid'].rolling(windows).apply(lambda x: pd.Series(x).quantile(0.2), raw=True)
        df['pb_mid_r'] = df['pb_mid'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                                       pd.Series(x).shape[0], raw=True)
        if show_pe:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 7))
            df[['pe', 'pe_r', 'pe_0.8', 'pe_0.2']].plot(secondary_y=['pe_r'], ax=ax1, alpha=.8)
            df[['pe_mid', 'pe_mid_r', 'pe_mid_0.8', 'pe_mid_0.2']].plot(secondary_y=['pe_mid_r'], ax=ax2, alpha=.8)
            plt.show()
        if show_pb:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 7))
            df[['pb', 'pb_r', 'pb_0.8', 'pb_0.2']].plot(secondary_y=['pb_r'], ax=ax1, alpha=.8)
            df[['pb_mid', 'pb_mid_r', 'pb_mid_0.8', 'pb_mid_0.2']].plot(secondary_y=['pb_mid_r'], ax=ax2, alpha=.8)
            plt.show()

    def rolling_pe_percentile(self, n=7, show=False, show_p_hist=False):
        """
        滚动PE百分位
        :param n: 年份间隔， 默认7年
        :param show: 是否展示图形
        :param show_p_hist: pe分布百分位图
        :return:
        """
        df = self.df
        # 这里的计算按一年244个交易日计算
        windows = int(n * 244)  # 将时间取整数
        if len(df) < windows:
            raise Exception("当前数据小于滚动窗口设置，无法完成滚动分为计算")

        column = 'percentile_' + str(n) + 'Y'
        df[column] = df['pe'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                               pd.Series(x).shape[0], raw=True)
        if show:
            fig, ax = plt.subplots(1, figsize=(16, 9))
            df[['close', column]].plot(ax=ax, secondary_y=[column], figsize=(16, 9), colormap='coolwarm')
            plt.show()
        if show_p_hist:
            """动态百分位分布，直方图"""
            fig, ax = plt.subplots(1, figsize=(16, 9))
            df[column].hist(ax=ax, figsize=(16, 9))
            plt.show()
        return df

    def append_expected_profit(self, show=False):
        """
        预期年化收益
        :return:
        """
        df = self.df
        # 预期年化收益率=分红率/PE+(1-分红率)*PB/PE，分红率统一设定为25%
        d = 0.25
        df['profit'] = (d / df['pe'] + (1 - d) * df['pb'] / df['pe'])
        if show:
            fig, ax = plt.subplots(1, figsize=(16, 9))
            df[['close', 'profit']].plot(ax=ax, secondary_y=['profit'], figsize=(16, 9), colormap='coolwarm')
            plt.show()

    def append_pos(self, show=False):
        """
        增加仓位管理计算
        :return:
        """
        df = self.df
        # part1: 仓位信息计算
        # 需要先调用append_finance方法，计算滚动PB
        df['pb_r'].fillna(0)
        df['pb_mid_r'].fillna(0)
        df['value_close'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        # p = 1- 综合百分位，百分位越低，折扣越大，赢的概率越大
        # radical_pos（激进仓位）= 2p - 1，conservative（保守仓位）= (2p - 1)/2
        df['value_total'] = (df['value_close'] + 2 * df['pb_mid_r'] + df['pb_r']) / 4
        df['radical_pos'] = 2 * (1 - df['value_total']) - 1
        df['conservative_pos'] = df['radical_pos'] / 2
        # part2: 定投比例计算
        df['invest_per'] = df['value_total'].apply(lambda x: 100 + 100 * (abs(2 - 10 * x) ** 1.618) if x <= 0.2 else 0)
        if show:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 18))
            df[['close', 'radical_pos']].plot(ax=ax1, secondary_y=['radical_pos'], figsize=(16, 9), alpha=.8)
            df[['close', 'invest_per']].plot(ax=ax2, secondary_y=['invest_per'], figsize=(16, 9), alpha=.8)
            plt.show()

    def append_poly_line(self, poly=1, show=False):
        """
        增加拟合线（一次拟合）
        :param poly: 默认使用一次拟合
        :param show:
        :return:
        """
        df = self.df
        df['date'] = df.index
        x = df['date'].apply(lambda x: dates.date2num(x))
        x_zero = x[0]
        x = x - x_zero
        polynomial = np.polynomial.Chebyshev.fit(x, df.close, poly)
        # 收盘价标准差
        close_std = 0.9 * np.std(df.close)
        df['poly_1'] = polynomial(x)
        df['upper'] = polynomial(x) + close_std
        df['lower'] = polynomial(x) - close_std
        if show:
            fig, ax = plt.subplots(1, figsize=(16, 9))
            ax.set_title('%s close price trend \n close:%s, lower:%s, mean:%s, high:%s' % (
                self.code, round(df['close'][-1], 0), round(df['lower'][-1], 0), round(df['poly_1'][-1], 0),
                round(df['upper'][-1], 0)))
            df[['close', 'poly_1', 'upper', 'lower']].plot(ax=ax, figsize=(16, 9), colormap='coolwarm')
            # plt.axhline(df['close'][-1], color='b', linestyle='-.')
            # plt.axhline(df['lower'][-1], color='g', linestyle='-.')
            plt.show()

    def __append_ema(self, fast=1200, mid=1800, slow=2400, show=False):
        """
        添加均线
        :param fast: 快线 5年
        :param mid: 中值 7.5年
        :param slow: 慢线 10年
        :param show:
        :return:
        """
        df = self.df
        df['EMA' + str(fast)] = ta.EMA(df.close.values, fast)
        df['EMA' + str(mid)] = ta.EMA(df.close.values, mid)
        df['EMA' + str(slow)] = ta.EMA(df.close.values, slow)
        if show:
            fig, ax = plt.subplots(1, figsize=(16, 9))
            df[['close', 'EMA' + str(fast), 'EMA' + str(mid), 'EMA' + str(slow)]].plot(ax=ax, figsize=(16, 9))
            plt.show()

    def print_detail(self):
        """
        打印所有的买入参考
        :return:
        """
        df = self.df
        df = df.dropna()
        for index, row in df.iterrows():
            output = 'CODE:%s ,日期:%s \n' % (self.code, str(pd.to_datetime(index, unit='d')))
            output += '时间域百分位:%s \n' % str(row.value_close * 100)
            output += '市值加权法，中位数PE:%s, 当前百分比:%s; 中位数PB:%s, 当前百分比:%s \n' % (
                row.pe, str(row.pe_r * 100) + '%', row.pb, str(row.pb_r * 100) + '%')
            output += '中位数法，中位数PE:%s, 当前百分比:%s; 中位数PB:%s, 当前百分比:%s \n' % (
                row.pe_mid, str(row.pe_mid_r * 100) + '%', row.pb_mid, str(row.pb_mid_r * 100) + '%')
            output += '综合估值百分位PB: %s \n' % (str(row.value_total * 100) + '%')
            output += '当前买入预计年化收益: %s \n' % (str(row.profit * 100) + '%')
            output += '仓位2p-1(激进): %s \n' % (str(row.radical_pos * 100) + '%')
            output += '仓位(2p-1)/2(保守): %s \n' % (str(row.conservative_pos * 100) + '%')
            output += '定投比例: %s \n\n' % (str(row.invest_per) + '%')
            print(output)

    def draw_reference(self, fast=1200, mid=1800, slow=2400):
        """画出参考图"""
        df = self.df
        # 1、财务参考：PE、PB百分位
        _, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 9))
        df[['pe', 'pe_r', 'pe_0.8', 'pe_0.2']].plot(secondary_y=['pe_r'], ax=axs[0][0], alpha=.8)
        df[['pe_mid', 'pe_mid_r', 'pe_mid_0.8', 'pe_mid_0.2']].plot(secondary_y=['pe_mid_r'], ax=axs[0][1], alpha=.8)
        df[['pb', 'pb_r', 'pb_0.8', 'pb_0.2']].plot(secondary_y=['pb_r'], ax=axs[1][0], alpha=.8)
        df[['pb_mid', 'pb_mid_r', 'pb_mid_0.8', 'pb_mid_0.2']].plot(secondary_y=['pb_mid_r'], ax=axs[1][1], alpha=.8)
        plt.show()
        # 2、收盘价参考
        self.__append_ema(fast, mid, slow)
        fig, ax = plt.subplots(1, figsize=(16, 9))
        ax.set_title('last close:%s, lower:%s, mean:%s, high:%s \n EMA%s:%s, EMA%s:%s, EMA%s:%s' % (
            round(df['close'][-1], 0), round(df['lower'][-1], 0), round(df['poly_1'][-1], 0),
            round(df['upper'][-1], 0),
            fast, round(df['EMA' + str(fast)][-1], 0),
            mid, round(df['EMA' + str(mid)][-1], 0),
            slow, round(df['EMA' + str(slow)][-1], 0)))
        df[['close', 'poly_1', 'upper', 'lower', 'EMA' + str(fast), 'EMA' + str(mid), 'EMA' + str(slow)]] \
            .plot(ax=ax, figsize=(16, 9))
        plt.axhline(df['close'][-1], color='#808080', linestyle='-.')
        plt.show()

    def draw_attribution_analyze(self):
        """画出归因分析"""
        df = self.df
        # 1、收盘价与PE、PB对比图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 18))
        df[['close', 'pe']].plot(ax=ax1, secondary_y=['pe'], figsize=(16, 9), alpha=.8)
        df[['close', 'pb']].plot(ax=ax2, secondary_y=['pb'], figsize=(16, 9), alpha=.8)
        plt.show()
        # 2、PE、PB相关性分析
        sns.jointplot(df['pe'], df['pe'], kind='reg', height=9)
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df[['pe', 'pb']].plot(ax=ax, secondary_y=['pb'], figsize=(16, 9))
        plt.show()
        # TODO：PE、PB的一次拟合，是否持续走低？
        # 3、PE、PB滚动百分位直方图

    def append(self):
        # TODO:
        # 暂缺指标PE、PB中位数、换手率totalturnover=totalTV/totalLFLO、PEPB根据（0-100）取步长计算比例
        # A 申万28行业去趋势度、巴菲特指数数据、年度均线、收盘价拟合
        pass
