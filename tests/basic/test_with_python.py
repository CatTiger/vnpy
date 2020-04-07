from vnpy.app.cta_strategy import BacktestingEngine
import vnpy.trader.constant as const
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # 创建回测引擎实例
    engine = BacktestingEngine()

    # 定义合约代码
    symbol = '002594'
    exchange = 'SZSE'
    vtSymbol = '.'.join([symbol, exchange])
    engine.set_parameters(vtSymbol, const.Interval.DAILY, start=datetime(2011, 7, 1), end=datetime(2020, 2, 24),
                          rate=15 / 100000, slippage=0,
                          size=1,
                          pricetick=0.001, capital=10000)

    engine.load_data()

    # list 转 dataframe
    bar_dict_list = []
    bar_list = engine.history_data
    for bar in bar_list:
        bar_dict_list.append(bar.__dict__)

    df = pd.DataFrame(bar_dict_list)
    df['change'] = df['close_price'] - df['close_price'].shift(1)
    df['ma5'] = df['close_price'].rolling(window=5, center=False).mean()
    df['ma20'] = df['close_price'].rolling(window=20, center=False).mean()

    df = df.dropna()
    df['pos'] = 0
    df['pos'][df['ma5'] >= df['ma20']] = 10000
    df['pos'][df['ma5'] < df['ma20']] = 0
    df['pos'] = df['pos'].shift(1).fillna(0)

    df['pnl'] = 0  # 利润
    df['pnl'] = df['pos'] * df['change']
    df['fee'] = 0  # 手续费
    df['fee'][df['pos'] != df['pos'].shift(1)] = df['close_price'] * 20000 * 16 / 100000
    df['netpnl'] = df['pnl'] - df['fee']
    df['cumsum'] = df['netpnl'].cumsum()

    # dateparse = lambda dates: pd.datetime.strftime(dates, '%Y-%m-%d')
    # df['trade_date'] = df['datetime'].map(dateparse)

    df.index = df['datetime']
    print(df[{'close_price','change','cumsum','pnl','fee', 'pos'}].head(100))
    plt.plot(df['datetime'], df['cumsum'])
    plt.show()

