from datetime import datetime
import vnpy.analyze.data.data_prepare as dp
import pandas as pd
import matplotlib.pyplot as plt


class MeanReversion:
    """均值回复投资思路"""

    def __init__(self, start_date: datetime, end_date: datetime, code: str, subject_type: str):
        """
        初始化
        :param start_date: 开始时间
        :param end_date: 结束时间
        :param code: 标识，eg: 000300.XSHG
        :param subject_type: 标的类型，目前暂定（宽基指数（broad）、行业指数（Industry））
        """
        self.start_date = start_date
        self.end_date = end_date
        self.code = code
        self.subject_type = subject_type
        # 获取价格与财务数据
        code_sp = code.split('.')
        self.df = dp.load_bar_data(code_sp[0], code_sp[1], start_date=start_date, end_data=end_date)
        self.df_finance = dp.load_finance_data(code, start_date=start_date, end_date=end_date)
        if len(self.df) != len(self.df_finance):
            raise Exception("base and finance data not matching")
        self.df['pe'] = self.df_finance['pe']
        self.df['pb'] = self.df_finance['pb']
        # 设置data为index
        self.df['date'] = pd.to_datetime(self.df['date'])  # 转换时间类型
        self.df.set_index(['date'], inplace=True)
        self.df.index.name = None  # 去掉索引列名

    def close_finance_relation(self, show_pe_percentile=False, show_pb_border_line=False, column='pe',
                               start_date=None,
                               end_date=None):
        """
        收盘价与PE关系
        :param show_pe_percentile: 是否标记PE百分位
        :param show_pb_border_line: 是否展示pb的边界线，根据齐东平的大数投资，当沪深股市整体市净率低于2倍时开始配置
        :param column: 展示字段
        :param start_date: 开始时间，如不指定则使用对象设定时间
        :param end_date: 结束时间，如不指定则使用对象设定时间
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
        df['profit'] = (d / df['pe'] + (1 - d) * df['pb'] / df['pe']) * 100
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
        df['value_close'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        # 按照7年参考，计算滚动PB
        windows = int(7 * 244)  # 将时间取整数
        if len(df) < windows:
            raise Exception("当前数据小于滚动窗口设置，无法完成滚动分为计算")
        df['pb_rolling'] = df['pb'].rolling(windows).apply(lambda x: pd.Series(x).rank().iloc[-1] /
                                                                     pd.Series(x).shape[0], raw=True)
        df['pb_rolling'].fillna(0)
        df['pos'] = (df['value_close'] + 2 * df['pb_rolling']) / 3
        if show:
            fig, ax = plt.subplots(1, figsize=(16, 9))
            df[['close', 'pos']].plot(ax=ax, secondary_y=['pos'], figsize=(16, 9), colormap='coolwarm')
            plt.show()

    def append(self):
        # TODO:
        # 暂缺指标PE、PB中位数、换手率totalturnover=totalTV/totalLFLO、PEPB根据（0-100）取步长计算比例
        # A 申万28行业去趋势度、巴菲特指数数据、年度均线、收盘价拟合
        pass
