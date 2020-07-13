from vnpy.analyze.object import IndexInfo
from datetime import datetime
from vnpy.trader.constant import IndexType

etf_set = [
    IndexInfo('000016.XSHG', '上证50', '', datetime(2004, 1, 30), IndexType.WIDE_BASE),
    IndexInfo('000300.XSHG', '沪深300', '', datetime(2005, 2, 18), IndexType.WIDE_BASE),
    IndexInfo('000905.XSHG', '中证500', '', datetime(2004, 1, 30), IndexType.WIDE_BASE),
    IndexInfo('399006.XSHE', '创业板指', '', datetime(2010, 6, 1), IndexType.WIDE_BASE),
    IndexInfo('399330.XSHE', '深证100', '', datetime(2006, 1, 24), IndexType.WIDE_BASE),

    IndexInfo('000913.XSHG', '300医药', '512010', datetime(2007, 7, 2), IndexType.INDUSTRY),
    IndexInfo('000932.XSHG', '中证消费', '159928', datetime(2009, 7, 3), IndexType.INDUSTRY),
    IndexInfo('399437.XSHE', '国证证券行业指数', '512880', datetime(2014, 12, 30), IndexType.INDUSTRY, rolling_gap_year=5),
    IndexInfo('399967.XSHE', '中证军工', '512660', datetime(2013, 12, 26), IndexType.INDUSTRY, rolling_gap_year=6),
    IndexInfo('399986.XSHE', '中证银行指数', '512800', datetime(2004, 1, 30), IndexType.INDUSTRY),
    IndexInfo('000015.XSHG', '红利指数', '510880', datetime(2005, 1, 4), IndexType.INDUSTRY),
    IndexInfo('000018.XSHG', '180金融', '510230', datetime(2007, 12, 10), IndexType.INDUSTRY),
    IndexInfo('000021.XSHG', '180治理', '510010', datetime(2008, 9, 10), IndexType.INDUSTRY),
    IndexInfo('000042.XSHG', '上证央企', '510060', datetime(2009, 3, 20), IndexType.INDUSTRY),
    IndexInfo('000038.XSHG', '上证金融', '510650', datetime(2009, 1, 9), IndexType.INDUSTRY),
    IndexInfo('000029.XSHG', '180价值', '510030', datetime(2009, 1, 9), IndexType.INDUSTRY),
    IndexInfo('399393.XSHE', '国证地产', '512200', datetime(2012, 8, 20), IndexType.INDUSTRY),
    IndexInfo('399395.XSHE', '国证有色', '512400', datetime(2012, 10, 29), IndexType.INDUSTRY),
    IndexInfo('399971.XSHE', '中证传媒', '512980', datetime(2014, 4, 11), IndexType.INDUSTRY, rolling_gap_year=5),
    IndexInfo('000993.XSHG', '全指信息', '159939', datetime(2011, 8, 2), IndexType.INDUSTRY),
    IndexInfo('000991.XSHG', '全指医药', '159938', datetime(2011, 8, 2), IndexType.INDUSTRY),

    IndexInfo('000012.XSHG', '国债指数', '511010', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),

    IndexInfo('159920.XSHE', '恒生指数', '', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),
    IndexInfo('501050.XSHG', '50AH优选', '', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),
    IndexInfo('159916.XSHE', '基本面60', '', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),
    IndexInfo('513030.XSHG', '德国DAX', '', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),
    IndexInfo('513500.XSHG', '标普500', '', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),
    IndexInfo('513100.XSHG', '纳指100', '', datetime(2003, 1, 2), IndexType.OTHER, cal_finance=False),
]

#  159920
# 国企指数 510900 000056.XSHG	上证国企 000956.XSHG	国企200 0.9左右

#
# 000925.XSHG	基本面50
# 500低波
