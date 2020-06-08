from jqdatasdk import finance
from jqdatasdk import *
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from vnpy.analyze.util.data_source import DataSource
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

auth('15802720411', 'Mm123456789')
df_ = finance.run_query(query(
    finance.STK_ML_QUOTA
).filter(
    finance.STK_ML_QUOTA.link_id.in_(('310001', '310002')),
    finance.STK_ML_QUOTA.day >= datetime(2020, 1, 1)
).order_by(finance.STK_ML_QUOTA.day.asc()).limit(100))
'''
310001	沪股通
310002	深股通
310003	港股通（沪）
310004	港股通（深）
'''
df = pd.DataFrame()

df1 = df_['buy_amount'].groupby(df_['day']).sum()
df2 = df_['sell_amount'].groupby(df_['day']).sum()

# 北向资金流入流出
df = pd.merge(df1, df2, how='left', on='day')
df['change'] = df['buy_amount'] - df['sell_amount']

# 获取大盘数据, 此处用沪深300替代
ds = DataSource(mode='remote')
df_close = ds.load_bar_data('000300', 'XSHG', start_date=datetime(df.index[0].year, df.index[0].month, df.index[0].day),
                            end_data=datetime(df.index[-1].year, df.index[-1].month, df.index[-1].day))
df_close.set_index(['date'], inplace=True)
df = pd.concat([df, df_close['close']], axis=1)

print(df)
fig, ax = plt.subplots()
ax.bar(df.index, df['change'], label='Men')

volumeMin = 0
ax1v = ax.twinx()
ax1v.plot(df.index, df.close, '#e1edf9', linewidth = 1.5)
plt.show()

# print(df[['day', 'link_id', 'buy_amount', 'sell_amount']])
