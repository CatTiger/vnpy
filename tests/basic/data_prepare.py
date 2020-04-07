#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import tushare as ts

import vnpy.trader.constant as const
from vnpy.trader.object import BarData
from vnpy.trader.database import database_manager

if __name__ == "__main__":

    bars = []
    data = ts.get_hist_data(code='002594', start='2011-07-01', end='2017-08-28')
    for row in data.iterrows():
        date = row[0]
        data = row[1]

        bar = BarData(
            gateway_name='test',
            symbol='002594',
            exchange=const.Exchange.SZSE,
            datetime=datetime.strptime(date, '%Y-%m-%d'),
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
