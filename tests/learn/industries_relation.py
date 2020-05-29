from jqdatasdk import *
import pandas as pd
import matplotlib.pyplot as plt


def industries_relation(show=False):
    """
    SW行业之间相关性调研
    :param show:
    :return:
    """
    auth('13277099856', '1221gzcC')
    # 国防军工I\采掘I\家用电器I\公用事业I
    df = pd.DataFrame(columns=(
    'date', '801190', '801780', '801790'))
    for code in ('801190', '801780', '801790'):
        df_tmp = finance.run_query(
            query(finance.SW1_DAILY_PRICE).filter(finance.SW1_DAILY_PRICE.code == code).order_by(
                finance.SW1_DAILY_PRICE.date.desc()).limit(2200))
        df['date'] = df_tmp['date']
        df[code] = df_tmp['close']
    df['date'] = pd.to_datetime(df['date'])  # 转换时间类型
    df.set_index(['date'], inplace=True)
    df.index.name = None  # 去掉索引列名
    if show:
        fig, ax = plt.subplots(1, figsize=(16, 9))
        df.plot(ax=ax, figsize=(16, 9))
        plt.show()
    print(df.head())


if __name__ == "__main__":
    industries_relation(show=True)
