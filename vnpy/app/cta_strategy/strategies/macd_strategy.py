from typing import Any
import math
from vnpy.app.cta_strategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)
from vnpy.trader.constant import Direction


class MacdStrategy(CtaTemplate):
    hist0 = 0.0
    hist1 = 0.0

    available_balance = 100000
    force_loss_price = 0.0

    def __init__(self, cta_engine: Any, strategy_name: str, vt_symbol: str, setting: dict):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.his_data_dict = setting['his_data_dict']
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)

        if not am.inited:
            return
        # macd strategy
        macd, signal, hist = am.macd(12, 26, 9, array=True)  # DIF/DEA/(DIF-DEA)
        self.hist0 = hist[-1]
        self.hist1 = hist[-2]

        cross_over = self.hist0 > 0 > self.hist1
        cross_below = self.hist0 < 0 <= self.hist1

        # 第二天的开盘价，说明：引入未来指标，只为了当日发出的买入、卖出只能在第二天结算时能够正常确认
        next_day_open_price = self.his_data_dict.get(bar.datetime.strftime('%Y-%m-%d'), -1)
        if next_day_open_price == -1:
            return

        # TODO: 添加止损策略
        metric_atr = am.atr(14)
        if bar.close_price < self.force_loss_price and self.pos > 0:
            self.sell(next_day_open_price, self.pos)

        if cross_over:
            burden_pos = math.floor(self.available_balance / next_day_open_price)
            self.buy(next_day_open_price, burden_pos)
            self.force_loss_price = next_day_open_price - metric_atr * 2

        if cross_below and self.pos > 0:
            self.sell(next_day_open_price, self.pos)

    def on_trade(self, trade: TradeData):
        if Direction.LONG == trade.direction:
            self.available_balance = self.available_balance - trade.price * trade.volume
        if Direction.SHORT == trade.direction:
            self.available_balance = self.available_balance + trade.price * trade.volume
        if Direction.NET == trade.direction:
            print('error, unknown trade status')
