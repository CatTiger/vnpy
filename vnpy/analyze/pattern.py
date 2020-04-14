from enum import Enum
from vnpy.analyze.candle_engine import CandleChart, CandleRefer
from collections import namedtuple

Candle = namedtuple('CandleChart',
                    ['name', 'body_ratio_below', 'body_ratio_upper',
                     'upper_shadow_ratio_below', 'upper_shadow_ratio_upper',
                     'lower_shadow_ratio_below', 'lower_shadow_ratio_upper'])


class CandlePattern(Enum):
    '''
    蜡烛图形态
    '''
    # 单蜡烛图形态：长腿十字线、墓碑十字线、捉腰带线、锤子\上吊线、倒锤子线、风高浪大线、流星线
    LONG_LEGGED_DOJI = Candle("长腿十字线", 0.1, 0.2, 0.3, 0.5, 0.3, 0.5)
    GRAVESTONE_DOJI = Candle("墓碑十字线", 0.1, 0.2, 0.3, 0.8, 0.0, 0.1)
    BELT_HOLD_LINE = Candle("捉腰带线", 0.7, 1, 0.0, 0.3, 0.0, 0.3)
    HAMMER_LINE = Candle("锤子线", 0.0, 0.3, 0.0, 0.1, 0.5, 1)
    HANGING_MAN_LINE = Candle("上吊线", 0.0, 0.3, 0.0, 0.1, 0.5, 1)
    INVERTED_HAMMER = Candle("倒锤子线", 0.0, 0.3, 0.5, 1, 0.0, 0.1)
    HIGH_WAVE_LINE = Candle("风高浪大线", 0.0, 0.3, 0.3, 1, 0.3, 1)
    SHOOTING_STAR = Candle("流星线", 0.0, 0.3, 0.5, 1, 0.0, 0.1)

    @staticmethod
    def basic_pattern_recognition(candle_chart: CandleChart):
        pattern_matched = set()
        for pattern in CandlePattern:
            if pattern.value.body_ratio_below < candle_chart.body_ratio < pattern.value.body_ratio_upper and \
                    pattern.value.upper_shadow_ratio_below < candle_chart.upper_shadow_ratio < pattern.value.upper_shadow_ratio_upper and \
                    pattern.value.lower_shadow_ratio_below < candle_chart.lower_shadow_ratio < pattern.value.lower_shadow_ratio_upper:
                pattern_matched.add(pattern)
                print('%s, %s' % (pattern.value.name, pattern.value.body_ratio_below))
        return pattern_matched


class TwoCandlePattern(Enum):
    # 双蜡烛图形态：反击线、乌云盖顶
    counterattack_lines = '反击线'
    dark_cloud_cover = '乌云盖顶'
    doji_star = '十字星线'
    engulfing_pattern = '吞没形态'
    harami = '孕线形态'
    harmi_cross = '十字孕线形态'
    in_neck_line = '切入线形态'
    on_neck_line = '待入线形态'
    piercing_pattern = '刺透形态'
    separating_lines = '分手线'
    side_by_side_white_lines = '并列阳线'
    star = '星线'
    thrusting_line = '插入线形态'
    tweezers_top_and_bottom = '平头顶部形态和平头底部形态'

    def is_counterattack_lines(self, ref_candle: CandleChart, cmp_candle: CandleChart):
        # TODO: 蜡烛body相对较大
        result = False
        ref = CandleRefer(ref_candle, cmp_candle)
        # 方向相反、body大小类似
        if ref.is_opposite() and ref.is_same_size(body_cmp=True, body_residual_ratio=0.2):
            if cmp_candle.type == 'yang':
                if cmp_candle.body_upper - ref_candle.body_lower >= 0:
                    result = True
        return result


if __name__ == "__main__":
    candle_chart = CandleChart(1, 1.1, 0.9, 1.01)
    CandlePattern.basic_pattern_recognition(candle_chart)
