#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import tushare as ts

import vnpy.trader.constant as const
from vnpy.trader.object import BarData
from vnpy.trader.database import database_manager

if __name__ == "__main__":

    bars = []
    pro = ts.pro_api('b730ba51af2da59c857f33c67a26ee33da96fe6007134ffce53b4141')
    # 20200224
    data = pro.daily(ts_code='002594.SZ', start_date='20110701', end_date='20200224')
    for row in data.iterrows():
        data = row[1]

        bar = BarData(
            gateway_name='test',
            symbol='002594',
            exchange=const.Exchange.SZSE,
            datetime=datetime.strptime(data['trade_date'], '%Y%m%d'),
            interval=const.Interval.DAILY,
            volume=data['vol'],
        )
        # open_interest: float = 0
        bar.open_price = data['open']
        bar.high_price = data['high']
        bar.low_price = data['low']
        bar.close_price = data['close']
        bars.append(bar)

    database_manager.save_bar_data(bars)