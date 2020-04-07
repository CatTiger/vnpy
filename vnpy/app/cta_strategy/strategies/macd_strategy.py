from typing import Any

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


class MacdStrategy(CtaTemplate):
    hist0 = 0.0
    hist1 = 0.0

    buy_count = 0
    sell_count = 0

    total_buy = 0.0

    last_buy_price = 0.0
    last_buy_atr = 0.0
    allow_loss_point = 2

    up_cnt = 0
    flag = True
    times = 0
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

        ma_60 = am.sma(60)
        if bar.close_price > ma_60:
            self.up_cnt += 1
            if self.flag:
                self.times += 1
                print(bar.datetime.strftime('%Y-%m-%d'), self.up_cnt)
                self.flag = False
        else:
            self.flag = True
        print(self.times)


        # 添加止损策略, ATR
        # if self.pos == 100 and (bar.close_price < self.last_buy_price - self.allow_loss_point * self.last_buy_atr):
        #     self.sell_count += 1
        #     print('loss sell: day:%s, price:%s, pos:%s, cnt:%s' % (
        #         bar.datetime.strftime('%Y-%m-%d'), self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')], self.pos,
        #         self.sell_count))
        #     self.sell(self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')], self.pos)
        #     return
        # # 添加顺势加仓策略
        #
        # macd, signal, hist = am.macd(12, 26, 9, array=True)  # DIF/DEA/(DIF-DEA)
        # self.hist0 = hist[-1]
        # self.hist1 = hist[-2]
        #
        # cross_over = self.hist0 >= 0 and self.hist1 < 0
        # cross_below = (self.hist0 < 0 and self.hist1 >= 0)
        #
        # if cross_over and self.pos == 0:
        #     self.buy_count += 1
        #     self.last_buy_atr = am.atr(14)
        #     self.last_buy_price = self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')]
        #     print('buy: day:%s, price:%s, pos:%s, cnt:%s, atr:%s, lower price: %s' % (
        #         bar.datetime.strftime('%Y-%m-%d'), self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')],
        #         self.pos, self.buy_count, self.last_buy_atr,
        #         self.last_buy_price - self.allow_loss_point * self.last_buy_atr))
        #     self.buy(self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')], 100)
        #
        # if cross_below and self.pos == 100 and bar.close_price > self.last_buy_price:
        #     self.sell_count += 1
        #     print('sell: day:%s, price:%s, pos:%s, cnt:%s' % (
        #         bar.datetime.strftime('%Y-%m-%d'), self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')], self.pos,
        #         self.sell_count))
        #     self.sell(self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')], self.pos)

        # if cross_over:

        # print('macd: %s, signal: %s, hist: %s' % (macd, signal, hist))

    def strategy_no_sell(self, bar):
        cross_over = self.hist0 >= 0 and self.hist1 < 0
        if cross_over:
            self.buy_count += 1
            self.total_buy += self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')]
            print(self.total_buy)
            print('buy: day:%s, price:%s, pos:%s, cnt:%s' % (
                bar.datetime.strftime('%Y-%m-%d'), bar.close_price, self.pos, self.buy_count))
            self.buy(self.his_data_dict[bar.datetime.strftime('%Y-%m-%d')], 1)
            self.current_action = 'long'
