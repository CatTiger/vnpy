from vnpy.app.cta_strategy import BarData


class CandleEngine:
    """
    蜡烛图分析引擎
    """

    def recognitionBar(self, bar: BarData):
        """
        识别单个bar数据
        :param bar:
        :return:
        """
        candle_chart = CandleChart(bar.open_price, bar.high_price, bar.low_price, bar.close_price)


class CandleChart:
    """蜡烛图"""

    def __init__(self, open: float, high: float, low: float, close: float):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        # 设置阴阳、上影线、下影线、实体
        self.type = 'yang' if open >= close else 'yin'
        self.upper_shadow = high - close if self.type == 'yang' else high - open
        self.lower_shadow = open - low if self.type == 'yang' else close - low
        self.body = close - open if self.type == 'yang' else open - close
        # 高低价差、实体占比、上影线比例、下影线比例
        self.max_spread = high - low
        self.body_ratio = self.body / self.max_spread
        self.upper_shadow_ratio = self.upper_shadow / self.body
        self.lower_shadow_ratio = self.lower_shadow / self.body
