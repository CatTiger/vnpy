from jqdatasdk import *
import pandas as pd
import matplotlib.pyplot as plt

auth('15802720411', 'Mm123456789')
df = get_bars('511010.XSHG', 2450, unit='1d',
              fields=['date', 'close'],
              include_now=False, end_dt=None, fq_ref_date=None, df=True)

df['earn_ratio'] = df['close'].rolling(245).apply(
    lambda x: 100 * (pd.Series(x).iloc[-1] - pd.Series(x).iloc[0]) / pd.Series(x).iloc[0])

df.set_index(['date'], inplace=True)
fig, ax = plt.subplots(1, figsize=(16, 9))
df['earn_ratio'].plot(ax=ax, figsize=(16, 9))
plt.show()
