from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarData,
)
from datetime import datetime, timedelta


class AdvantageCal(CtaTemplate):

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super(AdvantageCal, self).__init__(
            cta_engine, strategy_name, vt_symbol, setting
        )
        # 此处按照比例注入入金时间列表
        self.in_trade_dates = setting['in_trade_dates']
        self.out_trade_dates = setting['out_trade_dates']

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_bar(self, bar: BarData):
        """
        根据参数选择不同的买入点，寻找买入点优势
        :param bar: 
        :return: 
        """
        # 买入点
        if self.in_trade_dates.__contains__(datetime.strftime(bar.datetime, '%Y%m%d')):
            self.buy(bar.close_price, 100)

        # 买入之后的n天后卖出
        if self.out_trade_dates.__contains__(datetime.strftime(bar.datetime, '%Y%m%d')):
            self.sell(bar.close_price, 100)
