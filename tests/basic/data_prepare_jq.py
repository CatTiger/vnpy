from jqdatasdk import *
import vnpy.trader.constant as const
from vnpy.trader.object import BarData
from vnpy.trader.database import database_manager
from datetime import datetime

if __name__ == "__main__":
    auth('13277099856', '1221gzcC')
    is_auth = is_auth()
    print(is_auth)
    data = get_bars('510050.XSHG', 5000, unit='1d',
             fields=['date', 'open', 'high', 'low', 'close', 'volume'],
             include_now=False, end_dt=None, fq_ref_date=None, df=True)
    bars = []
    for row in data.iterrows():
        data = row[1]

        bar = BarData(
            gateway_name='test',
            symbol='510050',
            exchange=const.Exchange.SSE,
            datetime=data.date,
            interval=const.Interval.DAILY,
            volume=data['volume'],
        )
        # open_interest: float = 0
        bar.open_price = data['open']
        bar.high_price = data['high']
        bar.low_price = data['low']
        bar.close_price = data['close']
        bars.append(bar)

    database_manager.save_bar_data(bars)
