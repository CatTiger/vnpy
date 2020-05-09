import pandas as pd
import seaborn as sns
import vnpy.analyze.data.data_prepare as dp
import datetime as dt
import matplotlib.pyplot as plt


def earnings_demo():
    """收益率曲线示例"""
    df = dp.load_bar_data('000300', 'XSHG', start_date=dt.datetime(2015, 1, 1), end_data=dt.datetime(2020, 1, 1))
    returns = df.close.pct_change().dropna()
    sns.distplot(returns)
    plt.show()


def multi_stock_corr():
    """多只股票的相关性分析"""
    # 获取需要分析相关性股票数据
    start_date = dt.datetime(2014, 1, 1)
    end_date = dt.datetime(2016, 1, 1)
    kv = {'399001': 'XSHE', '399006': 'XSHE', '000300': 'XSHG', '399005': 'XSHE', '000016': 'XSHG'}
    df_benchmark = dp.load_bar_data('000001', 'XSHG', start_date=start_date, end_data=end_date)
    columns = [k + '.' + v for k, v in kv.items()]
    columns.append('date')

    df = pd.DataFrame(columns=tuple(columns))
    for symbol, alias in kv.items():
        data = dp.load_bar_data(symbol, alias, start_date=start_date, end_data=end_date)
        if len(df_benchmark) == len(data):
            df[symbol + '.' + alias] = data.close
        else:
            print('data not match, code:%s' % (symbol + '.' + alias))
    df['000001.XSHG'] = df_benchmark['close']
    df['date'] = df_benchmark['date']
    # 将date设置为索引
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名
    print(df.head())
    returns = df.pct_change().dropna()
    # 1、单标的收益分析
    # sns.distplot(returns.iloc[:, 0:1])
    # 2、小提琴图
    # sns.violinplot(data=returns, size=24)
    # 3、散点图
    # sns.pairplot(data=returns, diag_kind='kde', height=3)
    # 4、heatmap
    sns.heatmap(returns.corr(), cmap=sns.cm.rocket_r)
    # 5、聚类图
    # sns.clustermap(returns.corr())
    plt.show()


if __name__ == "__main__":
    # earnings_demo()
    multi_stock_corr()
