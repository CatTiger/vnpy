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
        self.type = 'yang' if close >= open else 'yin'
        self.upper_shadow = high - close if self.type == 'yang' else high - open
        self.lower_shadow = open - low if self.type == 'yang' else close - low
        self.body = close - open if self.type == 'yang' else open - close
        # body的上下边界价格
        self.body_upper = close if self.type == 'yang' else open
        self.body_lower = open if self.type == 'yang' else close
        # 高低价差、实体占比、上影线比例、下影线比例
        self.max_spread = high - low
        if self.max_spread == 0:
            self.body_ratio = 1
            self.upper_shadow_ratio = 1
            self.lower_shadow_ratio = 1
        else:
            self.body_ratio = self.body / self.max_spread
            self.upper_shadow_ratio = self.upper_shadow / self.max_spread
            self.lower_shadow_ratio = self.lower_shadow / self.max_spread


class CandleRefer:
    """两根蜡烛对比"""

    def __init__(self, ref_candle: CandleChart, cmp_candle: CandleChart):
        # 参照蜡烛图相对大小
        self.h_high = cmp_candle.high - ref_candle.high
        self.h_body_upper = cmp_candle.high - ref_candle.body_upper
        self.h_body_lower = cmp_candle.high - ref_candle.body_lower
        self.h_low = cmp_candle.high - ref_candle.low

        self.bu_high = cmp_candle.body_upper - ref_candle.high
        self.bu_body_upper = cmp_candle.body_upper - ref_candle.body_upper
        self.bu_body_lower = cmp_candle.body_upper - ref_candle.body_lower
        self.bu_low = cmp_candle.body_upper - ref_candle.low

        self.bl_high = cmp_candle.body_lower - ref_candle.high
        self.bl_body_upper = cmp_candle.body_lower - ref_candle.body_upper
        self.bl_body_lower = cmp_candle.body_lower - ref_candle.body_lower
        self.bl_low = cmp_candle.body_lower - ref_candle.low

        self.l_high = cmp_candle.low - ref_candle.high
        self.l_body_upper = cmp_candle.low - ref_candle.body_upper
        self.l_body_lower = cmp_candle.low - ref_candle.body_lower
        self.l_low = cmp_candle.low - ref_candle.low

        # 各区包含位置计算
        self.low_upper_match, self.low_body_match, self.low_lower_match = CandleRefer._segment_intersection(
            self.ref_candle.low, self.ref_candle.body_lower, self.cmp_candle)
        self.body_upper_match, self.body_body_match, self.body_lower_match = CandleRefer._segment_intersection(
            self.ref_candle.body_lower, self.ref_candle.body_upper, self.cmp_candle)
        self.high_upper_match, self.high_body_match, self.high_lower_match = CandleRefer._segment_intersection(
            self.ref_candle.body_upper, self.ref_candle.high, self.cmp_candle)

        self.cmp_candle = cmp_candle
        self.ref_candle = ref_candle

    def is_opposite(self):
        """方向是否相反"""
        return self.cmp_candle.type == self.ref_candle.type

    def is_same_size(self, entire_cmp=False, entire_residual_ratio=0.1,
                     body_cmp=False, body_residual_ratio=0.1, upper_cmp=False, upper_residual_ratio=0.2,
                     lower_cmp=False, lower_residual_ratio=0.1):
        """是否为相同尺寸"""
        result = False
        if entire_cmp:
            # 整体是否相同
            residual = self.ref_candle.max_spread * entire_residual_ratio
            result = self.ref_candle.max_spread - residual < self.cmp_candle.max_spread < self.ref_candle.max_spread + residual
        if body_cmp:
            # body是否大小相同
            residual = self.ref_candle.body * body_residual_ratio
            result = self.ref_candle.body - residual < self.cmp_candle.body < self.ref_candle.body + residual
        if upper_cmp:
            # 上影线是否相同
            residual = self.ref_candle.upper_shadow * upper_residual_ratio
            result = self.ref_candle.upper_shadow - residual < self.cmp_candle.upper_shadow < self.ref_candle.upper_shadow + residual
        if lower_cmp:
            # 下影线是否相同
            residual = self.ref_candle.lower_shadow * lower_residual_ratio
            result = self.ref_candle.lower_shadow - residual < self.cmp_candle.lower_shadow < self.ref_candle.lower_shadow + residual
        return result

    @staticmethod
    def _segment_intersection(low_price, high_price, match_candle: CandleChart):
        """各段价格区间交集, 上影线匹配、body匹配、下影线匹配"""
        # 上影线交集
        upper_shadow_match = CandleRefer._price_range(low_price, high_price, match_candle.body_upper, match_candle.high)
        # body部分交集
        body_match = CandleRefer._price_range(low_price, high_price, match_candle.body_lower, match_candle.body_upper)
        # 下影线交集
        lower_shadow_match = CandleRefer._price_range(low_price, high_price, match_candle.low, match_candle.body_lower)
        return upper_shadow_match, body_match, lower_shadow_match

    @staticmethod
    def _price_range(low_price, high_price, cmp_low, cmp_high):
        result = 0
        if cmp_low < low_price < cmp_high < high_price:
            result = cmp_high - low_price
        if low_price < cmp_low < cmp_high < high_price:
            result = cmp_high - cmp_low
        if cmp_low < high_price < cmp_high:
            result = high_price - cmp_low
        return result
