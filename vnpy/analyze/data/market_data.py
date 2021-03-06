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
    finance.STK_ML_QUOTA.day >= datetime(2019, 1, 1)
).order_by(finance.STK_ML_QUOTA.day.asc()).limit(1000))
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

# 获取大盘数据
ds = DataSource(mode='remote')
ds.save_bar_data('000001', 'XSHG', 50)  # 补上数据库中不存在数据
df_close = ds.load_bar_data('000001', 'XSHG', start_date=datetime(df.index[0].year, df.index[0].month, df.index[0].day),
                            end_data=datetime(df.index[-1].year, df.index[-1].month, df.index[-1].day))
df_close.set_index(['date'], inplace=True)
df = pd.concat([df, df_close['close']], axis=1)

fig, ax = plt.subplots(figsize=(16, 9))
ax.bar(df.index, df['change'], label='BUY')

volumeMin = 0
ax1v = ax.twinx()
ax1v.plot(df.index, df.close, '#faac58', label='SZ Index')

for xtick in ax.get_xticklabels():
    xtick.set_rotation(50)  # 旋转x轴

ax.legend()
ax1v.legend()
plt.show()

print('总流入金额:%s亿' % df['change'].sum())
