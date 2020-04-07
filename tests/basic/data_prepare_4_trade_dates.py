#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tushare as ts
from vnpy.trader.constant import Exchange
from vnpy.trader.object import TradeDate
from vnpy.trader.database import database_manager

def save_all():
    pro = ts.pro_api('b730ba51af2da59c857f33c67a26ee33da96fe6007134ffce53b4141')
    td_df = pro.trade_cal(exchange='', start_date='20100101', end_date='20200228')

    trade_dates = []
    for index, row in td_df.iterrows():
        trade_date = TradeDate(
            exchange=Exchange(row['exchange']),
            cal_date=row['cal_date'],
            is_open=row['is_open'],
        )
        trade_dates.append(trade_date)

    print(trade_dates)
    database_manager.save_trade_date(trade_dates)

if __name__ == "__main__":
    tds = database_manager.load_trade_dates()
    print(tds)





