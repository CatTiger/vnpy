# 导入包


import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import talib as ta
import time
from CAL.PyCAL import *
import matplotlib.colors as colors
import matplotlib.cm as cmx
import random as rd


def get_trends(series):
    series = series.dropna()
    wu = len(series[series == 1])
    wd = len(series[series == 0])
    return 1.0 * (wu - wd) / (wu + wd)


def delextremum(array):
    '''
    去极值
    '''
    array = np.array(array)
    for i in range(1, 5):
        sigma = array.std()
        mu = array.mean()
        array[array > mu + 3 * sigma] = mu + 3 * sigma
        array[array < mu - 3 * sigma] = mu - 3 * sigma
    return array


def value(index_index, index_name, time_index, time_name):
    # 获取指数的估值数据

    # 处理文件相关
    # 文件名
    path_name = "%s.csv" % index_index
    old_data = None
    # 读缓存文件
    try:
        old_data = pd.read_csv(path_name, index_col=0)
    except Exception as e:
        print(e)
        print('第一次运行时间较长')
        pass

        # 建立空的数据结构
    mypb = []
    mype = []
    mypepb = []
    totalmypb = []
    totalmype = []
    totalmypepb = []
    myclose = []
    indexatart = DataAPI.IdxGet(secID=u"", ticker=time_index, field=u"baseDate", pandas="1")
    start_date = indexatart.iloc[0, 0]
    # print(start_date)
    # start_date='20180101'

    if old_data is not None:
        # 缓存数据回滚两个也就是两周时间，好统一处理
        old_data = old_data[:-2]
        old_end_date = old_data.index.values[-1].replace('-', '')
        print('数据缓存日期:' + old_end_date)
        # 文件记录最后日期的下一个日期
        start_date = (datetime.strptime(old_end_date, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
    # 获取日期
    mydate = DataAPI.TradeCalGet(exchangeCD=u"XSHG,XSHE", beginDate=u"", endDate=datetime.today().strftime('%Y%m%d'),
                                 field=u"isOpen,prevTradeDate", pandas="1")
    # 获取日期是否开盘
    isopen = mydate.iloc[-1]['isOpen']
    if isopen == 1:
        if int(datetime.now().strftime("%H")) >= 22:  # 如果现在时间超过晚上十点，取当天数据
            end_date = datetime.today().strftime('%Y-%m-%d')
        else:  # 否则取昨天数据
            end_date = mydate.iloc[-1]['prevTradeDate']
    else:
        end_date = mydate.iloc[-1]['prevTradeDate']

    data = DataAPI.TradeCalGet(exchangeCD=u"XSHG", beginDate=start_date, endDate=end_date,
                               field=u"calendarDate,isWeekEnd", pandas="1")
    data = data[data['isWeekEnd'] == 1]  # 取周末的日期

    Dates = map(lambda x: x, data['calendarDate'].values.tolist())

    # 检查最后一天是否交易日，如果是的话，加入列表。周五会重复多加一天，不影响结果
    edata = DataAPI.TradeCalGet(exchangeCD=u"XSHG", beginDate=end_date, endDate=end_date, field=u"calendarDate,isOpen",
                                pandas="1")
    edata = edata[edata['isOpen'] == 1]

    if edata.empty == 0:
        if end_date != Dates[-1]:
            Dates.append(end_date)
    print('最新日期:' + Dates[-1])
    if index_index == 'A':
        # 此处日期根据缓存情况分别处理，如果是全部市场指数情况
        if old_data is None:
            myDates = Dates
        else:
            mydata = old_data.index.tolist()
            myDates = mydata + Dates

        # 申万28个行业的趋势度数据处理
        index_symbol = \
        DataAPI.IndustryGet(industryVersion=u"SW", industryVersionCD=u"", industryLevel=u"1", isNew=u"1", field=u"",
                            pandas="1")['indexSymbol'].tolist()
        index_symbol = [str(item) for item in index_symbol]
        df_daily_industry_symbol = DataAPI.MktIdxdGet(tradeDate=u"", indexID=u"", ticker=index_symbol, beginDate=u"",
                                                      endDate=u"", field=u"ticker,tradeDate,closeIndex", pandas="1")
        df_daily_industry_unstack = df_daily_industry_symbol.set_index(['tradeDate', 'ticker']).unstack()['closeIndex']
        df_weekly_industry_unstack = df_daily_industry_unstack.ix[myDates]

        df_weekly_DEA = df_weekly_industry_unstack.apply(lambda x: ta.MACD(x.values)[1], axis=0)
        df_weekly_flag = df_weekly_DEA[:]
        df_weekly_flag[df_weekly_flag > 0] = 1
        df_weekly_flag[df_weekly_flag < 0] = 0
        df_weekly_flag = df_weekly_flag.dropna(axis=0, how='all')

        trends_series = df_weekly_flag.apply(lambda x: get_trends(x), axis=1)
        trends_series = pd.DataFrame(trends_series).rename(columns={0: 'trends'})
        trends_series['tradeDate'] = trends_series.index
        trends_series['tradeDate'] = trends_series['tradeDate'].map(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        trends_series = trends_series.drop('tradeDate', 1)
        # GDP数据，处理
        GDP = [219439, 270232, 319516, 349081, 413030, 489301, 540367, 595244, 643974, 689052, 743586, 827122, 900300,
               900300]
        trends_series.loc[:'2006-12-29', 'GDP'] = GDP[0]
        trends_series.loc['2006-12-29':'2007-12-28', 'GDP'] = GDP[1]
        trends_series.loc['2007-12-28':'2008-12-31', 'GDP'] = GDP[2]
        trends_series.loc['2008-12-31':'2009-12-31', 'GDP'] = GDP[3]
        trends_series.loc['2009-12-31':'2010-12-31', 'GDP'] = GDP[4]
        trends_series.loc['2010-12-31':'2011-12-30', 'GDP'] = GDP[5]
        trends_series.loc['2011-12-30':'2012-12-28', 'GDP'] = GDP[6]
        trends_series.loc['2012-12-28':'2013-12-27', 'GDP'] = GDP[7]
        trends_series.loc['2013-12-27':'2014-12-31', 'GDP'] = GDP[8]
        trends_series.loc['2014-12-31':'2015-12-31', 'GDP'] = GDP[9]
        trends_series.loc['2015-12-31':'2016-12-30', 'GDP'] = GDP[10]
        trends_series.loc['2016-12-30':'2017-12-29', 'GDP'] = GDP[11]
        trends_series.loc['2017-12-29':'2018-12-28', 'GDP'] = GDP[12]
        trends_series.loc['2018-12-28':, 'GDP'] = GDP[13]
        # print(trends_series)

    mylen = []
    progress = []

    # 建立数据结构
    pepbdata = pd.DataFrame(
        {"close": None, "exchange": None, "pb": 0, "totalpb": 0, "pe": 0, "totalpe": 0, "trends": None,
         "buffett_LAP": None, "buffett_LFLO": None}, index=Dates)
    print(index_name + u'进度:'),
    # 每天计算数据
    for date in Dates:
        # 取指数收盘数据
        close = DataAPI.MktIdxdGet(indexID=u"", ticker=time_index, tradeDate=date, beginDate=u"", endDate=u"",
                                   exchangeCD=u"XSHE,XSHG", field=u"closeIndex", pandas="1")
        # 有时优矿数据更新不及时，容错处理
        if close.empty:
            if date > '2007-01-04':
                print(' close error')
            continue
        pepbdata.loc[date, 'close'] = close.iloc[0, 0]
        # 取每天的指数成分股的u"ticker,LCAP,PE,PB,TVMA20,LFLO"
        data_temp = DataAPI.MktStockFactorsOneDayGet(tradeDate=date, secID=set_universe(index_index, date),
                                                     field=u"ticker,LCAP,PE,PB,TVMA20,LFLO", pandas="1").dropna(axis=0,
                                                                                                                how='any')
        # 有时优矿数据更新不及时，容错处理
        if data_temp.empty:
            if date > '2007-01-04':
                print(date)
                print(' data error')
            continue

        # 按照市值从大到小排序，并重建索引
        data_temp = data_temp.sort_values('LCAP', ascending=False)
        data_temp = data_temp.reset_index(drop=True)
        # '000852.ZICN'中证1000指数，优矿的数据不全。程序重建指数，取市值800到1000的成分股数据。
        if index_index == '000852.ZICN':
            if len(data_temp) > 1000:
                data_temp = data_temp.iloc[800:(min(1800, len(data_temp)) - 1), :]

        data_temp = data_temp.reset_index(drop=True)
        mylen.append(len(data_temp))

        totalLAP = 0
        totalTV = 0
        totalB = 0
        totalE = 0
        totalLFLO = 0
        # 指数的每个成分股数据处理
        for i in range(0, len(data_temp)):
            # 成分股的市值，净资产，盈利加总。优矿的数据是对数数值，还原为正常数值，再相加
            totalLAP += np.e ** data_temp['LCAP'][i]
            totalTV += data_temp['TVMA20'][i]
            totalB += np.e ** data_temp['LCAP'][i] / data_temp['PB'][i]
            totalE += np.e ** data_temp['LCAP'][i] / data_temp['PE'][i]
            totalLFLO += np.e ** data_temp['LFLO'][i]
        # 整体换手率，市净率，市盈率
        totalturnover = totalTV / totalLFLO
        totalPB = totalLAP / totalB
        totalPE = totalLAP / totalE

        pepbdata.loc[date, 'exchange'] = totalturnover * 100000000000
        # 中位数市净率，市盈率
        pepbdata.loc[date, 'pb'] = data_temp.PB.median()
        pepbdata.loc[date, 'pe'] = data_temp.PE.median()
        # 整体法市净率，市盈率
        pepbdata.loc[date, 'totalpb'] = totalPB
        pepbdata.loc[date, 'totalpe'] = totalPE

        # 把市盈率按照<0,0-5,5-10,20-20,20-30,....分别计算所占比率
        pepbdata.loc[date, 'PE0-5'] = len(data_temp[(data_temp['PE'] >= 0) & (data_temp['PE'] < 5)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PE5-10'] = len(data_temp[(data_temp['PE'] >= 5) & (data_temp['PE'] < 10)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PE10-20'] = len(data_temp[(data_temp['PE'] >= 10) & (data_temp['PE'] < 20)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PE20-30'] = len(data_temp[(data_temp['PE'] >= 20) & (data_temp['PE'] < 30)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PE30-50'] = len(data_temp[(data_temp['PE'] >= 30) & (data_temp['PE'] < 50)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PE50-100'] = len(data_temp[(data_temp['PE'] >= 50) & (data_temp['PE'] < 100)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PE100+'] = len(data_temp[(data_temp['PE'] >= 100)]) / float(len(data_temp))
        pepbdata.loc[date, 'PE<0'] = len(data_temp[(data_temp['PE'] < 0)]) / float(len(data_temp))

        # 把市净率按照<0,0-1,1-2，2-3,3-4,....分别计算所占比率
        pepbdata.loc[date, 'PB0-1'] = len(data_temp[(data_temp['PB'] >= 0) & (data_temp['PB'] < 1)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PB1-2'] = len(data_temp[(data_temp['PB'] >= 1) & (data_temp['PB'] < 2)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PB2-3'] = len(data_temp[(data_temp['PB'] >= 2) & (data_temp['PB'] < 3)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PB3-4'] = len(data_temp[(data_temp['PB'] >= 3) & (data_temp['PB'] < 4)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PB4-6'] = len(data_temp[(data_temp['PB'] >= 4) & (data_temp['PB'] < 6)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PB6-10'] = len(data_temp[(data_temp['PB'] >= 6) & (data_temp['PB'] < 10)]) / float(
            len(data_temp))
        pepbdata.loc[date, 'PB10+'] = len(data_temp[(data_temp['PB'] >= 10)]) / float(len(data_temp))
        pepbdata.loc[date, 'PB<0'] = len(data_temp[(data_temp['PB'] < 0)]) / float(len(data_temp))

        if index_index == 'A':
            # 如果是全部市场情况，获取申万28个行业趋势度，巴菲特指标数据
            if date in trends_series.index.tolist():
                pepbdata.loc[date, 'trends'] = trends_series.loc[date, 'trends'] * 1.5 + 7
                pepbdata.loc[date, 'buffett_LAP'] = totalLAP / (trends_series.loc[date, 'GDP'] * 1000000)
                pepbdata.loc[date, 'buffett_LFLO'] = totalLFLO / (trends_series.loc[date, 'GDP'] * 1000000)

        # 进度条处理
        if (len(Dates) > 10):
            if progress != Dates.index(date) / int(len(Dates) / 10):
                print
                10 * Dates.index(date) / int(len(Dates) / 10),
                progress = Dates.index(date) / int(len(Dates) / 10)

    print
    ''

    # 指数收盘点位数据处理，去掉空数据，收盘数据取对数，去极值
    pepbdata = pepbdata.dropna(subset=['close'])
    pepbdata['close'] = [math.log1p(x) for x in pepbdata['close']]
    pepbdata['close'] = delextremum(pepbdata.loc[:, 'close'].values)

    # 把新的数据和老数据合并处理
    if old_data is not None:
        data = pd.concat([old_data, pepbdata])
        pepbdata = data

    # 计算5年均线，7.5年均线，10年均线
    pepbdata['EMA1200'] = ta.EMA(pepbdata.close.values, 250)
    pepbdata['EMA1800'] = ta.EMA(pepbdata.close.values, 375)
    pepbdata['EMA2400'] = ta.EMA(pepbdata.close.values, 500)
    # 0.9倍收盘数据方差
    close_var = 0.9 * np.std(pepbdata['close'])
    # 收盘数据直线拟合
    x = np.linspace(0, 1, len(pepbdata))
    cof = np.polyfit(x, pepbdata['close'], 1)
    p = np.poly1d(cof)
    # 直线拟合数据和方差一起产生上下顶底数据
    pepbdata['up'] = p(x) + close_var
    pepbdata['middle'] = p(x)
    pepbdata['down'] = p(x) - close_var
    pepbdata['middle_down'] = p(x) - 0.3 * close_var
    pepbdata['auto_invest'] = (pepbdata['middle_down'] + pepbdata['EMA1200']) / 2
    # 存储数据到缓存，并返回
    pepbdata.to_csv(path_name)
    return (pepbdata, end_date)


# 计时开始
starttime = datetime.now()
result = []

# 数据列表['估值指数的数据代码',u'估值指数名称',"指数收盘数据代码",u'指数收盘数据名称','on：显示图表，off：不显示图表'],
myset = [
    ['A', u'沪深A股', "000902", u'中证流通', 'on'],
    ['000016.ZICN', u'上证50', '000016', u'上证50', 'on'],
    ['000300.ZICN', u'沪深300', '000300', u'沪深300', 'on'],
    ['000905.ZICN', u'中证500', '000905', u'中证500', 'on'],
    ['000852.ZICN', u'中证1000', '000852', u'中证1000', 'on'],
    ['801193.ZICN', u'证券', '801193', u'证券', 'on'],
    # ['801162.ZICN',u'环保','801162',u'环保','on'],
    # ['801180.ZICN',u'房地产','801180',u'房地产','on'],
    # ['801150.ZICN',u'医药生物','801150',u'医药生物','on'],
    ['801080.ZICN', u'电子', '801080', u'电子', 'on'],
    ['801192.ZICN', u'银行', '801192', u'银行', 'on'],
    ['801120.ZICN', u'食品饮料', '801120', u'食品饮料', 'on'],
    # ['801040.ZICN',u'钢铁','801040',u'钢铁','off'],
    # ['801010.ZICN',u'农林牧渔','801010',u'农林牧渔','off'],
    # ['801020.ZICN',u'采掘','801020',u'采掘','off'],
    # ['801030.ZICN',u'化工','801030',u'化工','off'],
    # ['801050.ZICN',u'有色金属','801050',u'有色金属','off'],
    # ['801110.ZICN',u'家用电器','801110',u'家用电器','off'],
    # ['801130.ZICN',u'纺织服装','801130',u'纺织服装','off'],
    # ['801140.ZICN',u'轻工制造','801140',u'轻工制造','off'],
    # ['801160.ZICN',u'公用事业','801160',u'公用事业','off'],
    # ['801170.ZICN',u'交通运输','801170',u'交通运输','off'],
    # ['801200.ZICN',u'商业贸易','801200',u'商业贸易','off'],
    # ['801210.ZICN',u'休闲服务','801210',u'休闲服务','off'],
    # ['801230.ZICN',u'综合','801230',u'综合','off'],
    ['399321.ZICN', u'国证红利', '399321', u'国证红利', 'on'],
    # ['000015.ZICN',u'上证红利','000015',u'上证红利','off'],
]
myset = np.array(myset)

myset_dfpb = pd.DataFrame()
myset_dfpe = pd.DataFrame()
dfpb = pd.DataFrame()
dfpe = pd.DataFrame()
dfpepb = pd.DataFrame()
totaldfpe = pd.DataFrame()
myset_totaldfpb = pd.DataFrame()
myset_totaldfpe = pd.DataFrame()
totaldfpepb = pd.DataFrame()
totalvalue = pd.DataFrame(columns=['Valuation', 'Holding'])
myindex = []
mytotalvalue = []
mytotalholding = []
mytotalvalue_pre = []
mytotalholding_pre = []

for i in range(0, len(myset)):
    (result, end_date) = value(myset[i, 0], myset[i, 1], myset[i, 2], myset[i, 3])
    location = result[(result.pb > 0) & (result.totalpb > 0)].index.tolist()
    # 从返回的数据分段，好方便处理
    dfpb = result.loc[location, ['pb', 'totalpb']]
    dfpe = result.loc[location, ['pe', 'totalpe']]

    dfpearea = result.loc[location, ['PE0-5', 'PE5-10', 'PE10-20', 'PE20-30', 'PE30-50', 'PE50-100', 'PE100+', 'PE<0']]
    dfpbarea = result.loc[location, ['PB0-1', 'PB1-2', 'PB2-3', 'PB3-4', 'PB4-6', 'PB6-10', 'PB10+', 'PB<0']]
    # 去极值
    dfpb['delextremum_pb'] = delextremum(dfpb.loc[:, 'pb'].values)
    dfpb['delextremum_totalpb'] = delextremum(dfpb.loc[:, 'totalpb'].values)

    dfpe['delextremum_pe'] = delextremum(dfpe.loc[:, 'pe'].values)
    dfpe['delextremum_totalpe'] = delextremum(dfpe.loc[:, 'totalpe'].values)

    myset_dfpb[myset[i, 1]] = dfpb['delextremum_pb']
    myset_totaldfpb[myset[i, 1]] = dfpb['delextremum_totalpb']

    myset_dfpe[myset[i, 1]] = dfpe['delextremum_pe']
    myset_totaldfpe[myset[i, 1]] = dfpe['delextremum_totalpe']
    myindex.append(myset[i, 1])

    # 收盘点位处于拟合的上下沿顶底的位置，作为时间域百分位
    value_close = (result['close'][-1] - result['down'][-1]) / (result['up'][-1] - result['down'][-1])
    value_close_pre = (result['close'][-5] - result['down'][-5]) / (result['up'][-5] - result['down'][-5])
    if myset[i, 4] == 'on':
        print('时间域百分位: %d%%(上月:%d%%)' % (100 * value_close, 100 * value_close_pre))

    # 巴菲特指标不能自动更新，暂时去掉
    # if myset[i,4]=='on':
    #     if myset[i,0]=='A':
    #         print myset[i,1],
    #         buffet=result['buffett_LAP'][-1]
    #         #print(result['buffett_LAP'])
    #         print( '巴菲特指标: %d%%(上月:%d%%)' %(buffet,result['buffett_LAP'][-5]))

    # 七年时间
    mn = 350
    # 中位数市净率百分位
    # value_PB=len([x for x in dfpb['delextremum_pb'] if x < dfpb['delextremum_pb'][-1]])/float(len(dfpb['delextremum_pb']))
    # value_PB_pre=len([x for x in dfpb['delextremum_pb'] if x < dfpb['delextremum_pb'][-5]])/float(len(dfpb['delextremum_pb']))
    # 最近七年百分位
    value_PB = len(
        [x for x in dfpb[len(dfpb) - mn:len(dfpb)]['delextremum_pb'] if x < dfpb['delextremum_pb'][-1]]) / float(mn)
    value_PB_pre = len([x for x in dfpb[len(dfpb) - mn - 5:len(dfpb) - 5]['delextremum_pb'] if
                        x < dfpb['delextremum_pb'][-5]]) / float(mn)

    if myset[i, 4] == 'on':
        print
        myset[i, 1],
        print('当前中位数PB: %.1f(上月:%.1f)' % (dfpb['delextremum_pb'][-1], dfpb['delextremum_pb'][-5])),
        print('   中位数PB百分位:%d%%(上月:%d%%)' % (100 * value_PB, 100 * value_PB_pre))
        time_value_PB = len([x for x in dfpb['delextremum_pb'] if x < dfpb['delextremum_pb'][-1]])

    # 整体法最近七年市净率百分位
    # value_totalPB=len([x for x in dfpb['delextremum_totalpb'] if x < dfpb['delextremum_totalpb'][-1]])/float(len(dfpb['delextremum_totalpb']))
    # value_totalPB_pre=len([x for x in dfpb['delextremum_totalpb'] if x < dfpb['delextremum_totalpb'][-5]])/float(len(dfpb['delextremum_totalpb']))
    value_totalPB = len([x for x in dfpb[len(dfpb) - mn:len(dfpb)]['delextremum_totalpb'] if
                         x < dfpb['delextremum_totalpb'][-1]]) / float(mn)
    value_totalPB_pre = len([x for x in dfpb[len(dfpb) - mn - 5:len(dfpb) - 5]['delextremum_totalpb'] if
                             x < dfpb['delextremum_totalpb'][-5]]) / float(mn)
    if myset[i, 4] == 'on':
        print
        myset[i, 1],
        print('当前整体法PB:%.1f(上月:%.1f)' % (dfpb['delextremum_totalpb'][-1], dfpb['delextremum_totalpb'][-5])),
        print('      整体法PB百分位:%d%%(上月:%d%%)' % (100 * value_totalPB, 100 * value_totalPB_pre))
        time_value_totalPB = len([x for x in dfpb['delextremum_totalpb'] if x < dfpb['delextremum_totalpb'][-1]])
        print('低于当前PB时间(月):%.1f' % ((time_value_totalPB + time_value_PB) / float(8)))

    # 两份中位数市净率百分位，一份整体法市净率百分位，一份时间域百分位作为权重分配，来产生综合百分位
    value_total = (value_close + 2 * value_PB + value_totalPB) / 4
    value_total_pre = (value_close_pre + 2 * value_PB_pre + value_totalPB_pre) / 4
    if myset[i, 4] == 'on':
        print
        myset[i, 1],
        print('综合估值百分位（PB，时间）:%d%%(上月:%d%%)' % (100 * value_total, 100 * value_total_pre))

    # 根据市盈率和市净率产生预期年化收益率。预期年化收益率=分红率/PE+(1-分红率)*PB/PE，分红率统一设定为25%
    if myset[i, 4] == 'on':
        print('当前整体法PE:%.1f(上月:%.1f)' % (dfpe['delextremum_totalpe'][-1], dfpe['delextremum_totalpe'][-5]))
        myyield = 25 / dfpe['delextremum_totalpe'][-1] + 75 * dfpb['delextremum_totalpb'][-1] / \
                  dfpe['delextremum_totalpe'][-1]
        myyield_pre = 25 / dfpe['delextremum_totalpe'][-5] + 75 * dfpb['delextremum_totalpb'][-5] / \
                      dfpe['delextremum_totalpe'][-5]
        print('当前买入预期年化收益率（不考虑估值变化）:%.1f%%(上月:%.1f%%)' % (myyield, myyield_pre))

    # p=(1-综合百分位)做为投资赢得概率，百分位越小，赢得概率越大
    # 2p-1作为激进仓位，（2p-1）/2作为保守仓位。次投资仓位原理来自齐东平的大数投资。当估值百分位是0的时候，激进仓位是100%，保守仓位是50%
    p = 1 - value_total
    p_pre = 1 - value_total_pre
    invest_holding = (2 * p - 1) / 2
    invest_holding_pre = (2 * p_pre - 1) / 2
    if invest_holding <= 0:
        invest_holding = 0
    if invest_holding_pre <= 0:
        invest_holding_pre = 0
    if myset[i, 4] == 'on':
        print('仓位2P-1（激进）:%d%%(上月:%d%%)' % (100 * (2 * p - 1), 100 * (2 * p_pre - 1)))
        print('仓位(2P-1)/2(保守):%d%%(上月:%d%%)' % (100 * (2 * p - 1) / 2, 100 * (2 * p_pre - 1) / 2))

    # 每月定投份额计算，估值低于20%开始定投，估值越低，定投数额越大
    auto_invest_delta = abs(2 - 10 * value_total) ** 1.618
    auto_invest_delta_pre = abs(2 - 10 * value_total_pre) ** 1.618
    if value_total <= 0.2:
        auto_invest_per = 100 + 100 * auto_invest_delta
    else:
        auto_invest_per = 0

    if value_total_pre <= 0.2:
        auto_invest_per_pre = 100 + 100 * auto_invest_delta_pre
    else:
        auto_invest_per_pre = 0

    if myset[i, 4] == 'on':
        print
        myset[i, 1],
        print('定投比例:%d%%(上月:%d%%)' % (auto_invest_per, auto_invest_per_pre))

    print(' ')

    if myset[i, 4] == 'on':
        # 从数据作图
        plt.figure(figsize=(20, 5))
        plt.subplot(121)
        dfpb['delextremum_pb'].plot()

        dfpb['delextremum_pb_10'] = None
        dfpb['delextremum_pb_20'] = None
        dfpb['delextremum_pb_50'] = None
        dfpb['delextremum_pb_80'] = None
        dfpb['delextremum_pb_90'] = None

        dfpb['delextremum_totalpb_10'] = None
        dfpb['delextremum_totalpb_20'] = None
        dfpb['delextremum_totalpb_50'] = None
        dfpb['delextremum_totalpb_80'] = None
        dfpb['delextremum_totalpb_90'] = None

        # 最近7年数据求百分位：10%，20%，50%，80%，90%
        # mn=350
        for k in range(mn, len(dfpb)):
            dfpb.iloc[k, 4] = np.percentile(dfpb[k - mn:k]['delextremum_pb'], 10)
            dfpb.iloc[k, 5] = np.percentile(dfpb[k - mn:k]['delextremum_pb'], 20)
            dfpb.iloc[k, 6] = np.percentile(dfpb[k - mn:k]['delextremum_pb'], 50)
            dfpb.iloc[k, 7] = np.percentile(dfpb[k - mn:k]['delextremum_pb'], 80)
            dfpb.iloc[k, 8] = np.percentile(dfpb[k - mn:k]['delextremum_pb'], 90)

            dfpb.iloc[k, 9] = np.percentile(dfpb[k - mn:k]['delextremum_totalpb'], 10)
            dfpb.iloc[k, 10] = np.percentile(dfpb[k - mn:k]['delextremum_totalpb'], 20)
            dfpb.iloc[k, 11] = np.percentile(dfpb[k - mn:k]['delextremum_totalpb'], 50)
            dfpb.iloc[k, 12] = np.percentile(dfpb[k - mn:k]['delextremum_totalpb'], 80)
            dfpb.iloc[k, 13] = np.percentile(dfpb[k - mn:k]['delextremum_totalpb'], 90)

        plt.title(myset[i, 1] + u" PB(中位数):" + str(round(dfpb['delextremum_pb'][-1], 1)) + u"；  百分位：" + str(
            round(100 * value_PB, 1)), fontproperties=font, fontsize=16)
        xmin, xmax = plt.xlim()
        # plt.hlines(np.percentile(dfpb['delextremum_pb'],10),xmin,xmax,color=u'g')
        dfpb['delextremum_pb_10'].plot(color=u'g')
        dfpb['delextremum_pb_20'].plot(color=u'g')
        dfpb['delextremum_pb_50'].plot(color=u'y')
        dfpb['delextremum_pb_80'].plot(color=u'r')
        dfpb['delextremum_pb_90'].plot(color=u'r')

        plt.hlines(dfpb['delextremum_pb'][-1], xmin, xmax, color='#808080', linestyle='-.')
        # plt.hlines(np.percentile(dfpb['delextremum_pb'],50),xmin,xmax,color=u'y')
        # plt.hlines(np.percentile(dfpb['delextremum_pb'],80),xmin,xmax,color=u'r')
        # plt.hlines(np.percentile(dfpb['delextremum_pb'],20),xmin,xmax,color=u'g')
        # plt.hlines(np.percentile(dfpb['delextremum_pb'],90),xmin,xmax,color=u'r')
        plt.legend(['PB', '10-20%', 'Current', '50%', '80-90%'], fontsize='small', loc='best')

        plt.subplot(122)
        dfpb['delextremum_totalpb'].plot()
        plt.title(myset[i, 1] + u" PB(整体法):" + str(round(dfpb['delextremum_totalpb'][-1], 1)) + u"；  百分位：" + str(
            round(100 * value_totalPB, 1)), fontproperties=font, fontsize=16)
        xmin, xmax = plt.xlim()

        dfpb['delextremum_totalpb_10'].plot(color=u'g')
        dfpb['delextremum_totalpb_20'].plot(color=u'g')
        dfpb['delextremum_totalpb_50'].plot(color=u'y')
        dfpb['delextremum_totalpb_80'].plot(color=u'r')
        dfpb['delextremum_totalpb_90'].plot(color=u'r')

        # plt.hlines(np.percentile(dfpb['delextremum_totalpb'],10),xmin,xmax,color=u'g')
        plt.hlines(dfpb['delextremum_totalpb'][-1], xmin, xmax, color='#808080', linestyle='-.')
        # plt.hlines(np.percentile(dfpb['delextremum_totalpb'],50),xmin,xmax,color=u'y')
        # plt.hlines(np.percentile(dfpb['delextremum_totalpb'],80),xmin,xmax,color=u'r')
        # plt.hlines(np.percentile(dfpb['delextremum_totalpb'],20),xmin,xmax,color=u'g')
        # plt.hlines(np.percentile(dfpb['delextremum_totalpb'],90),xmin,xmax,color=u'r')
        plt.legend(['PB', '10-20%', 'Current', '50%', '80-90%'], fontsize='small', loc='best')

        plt.figure(figsize=(20, 10))
        result['close'].plot()
        result['EMA1200'].plot()
        result['EMA1800'].plot()
        result['EMA2400'].plot()
        result['up'].plot()
        result['middle'].plot()
        result['down'].plot()
        result['auto_invest'].plot(color='red', linewidth=3)

        if myset[i, 0] == 'A':
            result['trends'].plot(color='red', linestyle='-.')
            plt.axhline(result['trends'][-1], color='red', linestyle='-.')

        plt.axhline(result['close'][-1], color='#808080', linestyle='-.')
        plt.legend(['close', 'EMA1200', 'EMA1800', 'EMA2400'], fontsize='small', loc='best')
        result['exchange'].plot(secondary_y=True, color='#808080', linestyle='-.')
        plt.axhline(result['exchange'][-1], color='#808080', linestyle='-.')
        plt.title(myset[i, 3] + u" 时间域百分位:" + str(round(100 * value_close, 1)) + u"；   综合百分位:" + str(
            round(100 * value_total, 1)), fontproperties=font, fontsize=16)
        plt.grid(True)

        if myset[i, 0] == '000905.ZICN':
            # 生成历次牛市数据
            # result['close']=[math.expm1(x) for x in result['close']]
            # print(result['close'])
            plt.figure(figsize=(20, 10))
            first = result['close']['2005-07-15':'2008-01-11'] - result['close']['2005-07-15']
            second = result['close']['2008-11-07':'2011-03-25'] - result['close']['2008-11-07']
            third = result['close']['2012-11-30':'2015-06-12'] - result['close']['2012-11-30']
            fourth = result['close']['2018-10-19':] - result['close']['2018-10-19']
            fourth = result['close']['2018-10-19':] - result['close']['2018-10-19']
            first.plot(linewidth=1)
            second.plot(linewidth=3)
            third.plot(linewidth=5)
            fourth.plot(linewidth=9)
            plt.title(u'历次牛市进度。线条从细到粗分别是：07年牛市，09-10年牛市，15年牛市，最近牛市', fontproperties=font, fontsize=16)

        if myset[i, 0] == 'A':
            # 巴菲特指标暂时去掉
            #             plt.figure(figsize=(20, 10))
            #             result['buffett_LAP'].plot(color= 'blue')
            #             plt.axhline(result['buffett_LAP'][-1], color= 'blue',linestyle= '-.')
            #             plt.axhline(100, color= 'red')
            #             plt.axhline(80, color= 'yellow')
            #             plt.axhline(60, color= 'yellow')
            #             plt.axhline(40, color= 'green')
            #             plt.title(u'巴菲特指标（全部A股总市值除以当年GDP）',fontproperties=font,fontsize=16)

            # 读取国债历史数据
            try:
                old_data = pd.read_csv("10Ybond.csv", index_col=0)
            except Exception as e:
                print(e)
                print('缺少历史国债收益率文件')
                pass
            else:
                # 从优矿获取最新国债收益率数据
                new_data = DataAPI.BondCmYieldCurveGet(beginDate=u"20191202", endDate=end_date.replace('-', ''),
                                                       curveCD=u"01", curveTypeCD=u"1", maturity="10.0", field=u"",
                                                       pandas="1")
                # 数据处理
                del new_data['curveName']
                del new_data['maturity']
                del new_data['curveType']
                # 数据首尾对调
                new_data = new_data.sort_index(ascending=0)
                new_data = new_data.reset_index(drop=True)
                # 最新数据日期改为当天日期。此处理属于无奈之举，因为优矿国债数据更新不及时。不过这样处理不影响模糊的正确
                new_data.iloc[-1, 0] = end_date
                # 历史数据和最新数据合并
                tenY_bond = pd.concat([old_data, new_data])
                tenY_bond = tenY_bond.reset_index(drop=True)
                tenY_bond = tenY_bond.set_index(['tradeDate'])
                # 国债数据以天为周期，估值数据以周为周期。所以国债数据和估值数据采取并“AND”操作，改变国债数据周期为周
                result1 = pd.concat([result, tenY_bond], axis=1, join='inner')
                # 1/PE为中位数市盈率收益率
                result1['pe'] = 100 / result1['pe']
                # 作图
                plt.figure(figsize=(20, 10))
                result1['yield'].plot(color='red', linewidth=2)
                result1['pe'].plot(color='blue', linewidth=2)
                result1['close'] = 2 * (result1['close'] - 5.5)
                result1['close'].plot(color='#808080', linestyle='-.')
                plt.title(u'中位数PE收益率（1/PE）和10年国债收益率比较    红颜色10年国债收益率，蓝颜色中位数PE收益率，灰颜色中证流通收盘', fontproperties=font,
                          fontsize=16)

            zzlt_min = int(min(result['close']))
            result['close1'] = result['close'] - zzlt_min
            zzlt_max = math.ceil(max(result['close1']))
            result['close1'] = result['close1'] / zzlt_max - 1
            zzlt_close = result[49:]

            dfpearea = -dfpearea

            dfpearea.plot.area(figsize=(20, 10), grid=(True));

            zzlt_close['close1'].plot(color='black', linewidth=2)

            plt.yticks(np.arange(-1, 0.2, 0.2), ('1', '0.8', '0.6', '0.4', '0.2', '0', ''))

            xmin, xmax = plt.xlim()
            plt.title(myset[i, 1] + u'PE分布图' + u'，叠加中证流通K线', fontproperties=font, fontsize=16)
            plt.grid(axis='y', color='skyblue', linestyle='--', linewidth=2)
            plt.legend(loc='best', ncol=8)
            plt.hlines(-0.8, xmin, xmax, color='skyblue')
            plt.hlines(-0.6, xmin, xmax, color='skyblue')
            plt.hlines(-0.4, xmin, xmax, color='skyblue')
            plt.hlines(-0.2, xmin, xmax, color='skyblue')

            dfpbarea = -dfpbarea
            dfpbarea.plot.area(figsize=(20, 10), grid=(True));

            zzlt_close['close1'].plot(color='black', linewidth=2)
            plt.yticks(np.arange(-1, 0.2, 0.2), ('1', '0.8', '0.6', '0.4', '0.2', '0', ''))
            xmin, xmax = plt.xlim()
            plt.title(myset[i, 1] + u'PB分布图' + u'，叠加中证流通K线', fontproperties=font, fontsize=16)
            plt.grid(axis='y', color='skyblue', linestyle='--', linewidth=2)
            plt.legend(loc='best', ncol=8)
            plt.hlines(-0.8, xmin, xmax, color='skyblue')
            plt.hlines(-0.6, xmin, xmax, color='skyblue')
            plt.hlines(-0.4, xmin, xmax, color='skyblue')
            plt.hlines(-0.2, xmin, xmax, color='skyblue')

    mytotalvalue.append(100 * value_total)
    mytotalholding.append(100 * invest_holding)
    mytotalvalue_pre.append(100 * value_total_pre)
    mytotalholding_pre.append(100 * invest_holding_pre)

total = pd.DataFrame({u"Valuation": mytotalvalue, "Holding": mytotalholding, u"Valuation_pre": mytotalvalue_pre,
                      "Holding_pre": mytotalholding_pre}, index=myindex)
total = total.sort_values('Holding', ascending=False)

num = np.linspace(1, len(myset), len(myset))

myset_pe = []
myset_totalpe = []
myset_pb = []
myset_totalpb = []
myset_gain = []

for i in range(len(myset)):
    myset_pe.append(len([x for x in myset_dfpe[myset[i, 1]] if x < myset_dfpe[myset[i, 1]][-1]]) / float(
        len(myset_dfpe[myset[i, 1]])))
    myset_totalpe.append(len([x for x in myset_totaldfpe[myset[i, 1]] if x < myset_totaldfpe[myset[i, 1]][-1]]) / float(
        len(myset_totaldfpe[myset[i, 1]])))
    myset_pb.append(len([x for x in myset_dfpb[myset[i, 1]] if x < myset_dfpb[myset[i, 1]][-1]]) / float(
        len(myset_dfpb[myset[i, 1]])))
    myset_totalpb.append(len([x for x in myset_totaldfpb[myset[i, 1]] if x < myset_totaldfpb[myset[i, 1]][-1]]) / float(
        len(myset_totaldfpb[myset[i, 1]])))
    mygain = 25 / myset_totaldfpe[myset[i, 1]][-1] + 75 * myset_totaldfpb[myset[i, 1]][-1] / \
             myset_totaldfpe[myset[i, 1]][-1]
    myset_gain.append(45 * (mygain - 4.5))
    for j in range(0, len(myset_gain)):
        if myset_gain[j] < 0:
            myset_gain[j] = 2

mytotal = pd.DataFrame({"pe": myset_pe, "totalpe": myset_totalpe, "pb": myset_pb, "totalpb": myset_totalpb},
                       index=myindex)

plt.figure(figsize=(20, 10))
plt.subplot(121)

myset_pb = [i * 100 for i in myset_pb]
myset_pe = [i * 100 for i in myset_pe]
plt.scatter(x=myset_pb, y=myset_pe, s=myset_gain, c='#929591')

xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()
xymax = max(xmax, ymax)
plt.xlim(xmax=xymax)
plt.ylim(ymax=xymax)
plt.xlim(xmin=-5)
plt.ylim(ymin=-5)
plt.title(u'中位数PEPB百分位(圆大小代表预期收益)', fontproperties=font, fontsize=16)
plt.xlabel(u'中位数PB百分位', fontproperties=font)
plt.ylabel(u'中位数PE百分位', fontproperties=font)
plt.axhline(y=10, color='#15b01a', alpha=1)
plt.axhline(y=20, color='#96f97b', alpha=1)
plt.axvline(x=10, color='#15b01a', alpha=1)
plt.axvline(x=20, color='#96f97b', alpha=1)
for i in range(len(myset)):
    plt.annotate(myset[i, 1], (100 * mytotal.iloc[i, 0], 100 * mytotal.iloc[i, 1]), fontproperties=font, fontsize=9)

plt.subplot(122)

myset_totalpb = [i * 100 for i in myset_totalpb]
myset_totalpe = [i * 100 for i in myset_totalpe]
plt.scatter(x=myset_totalpb, y=myset_totalpe, s=myset_gain, c='#929591')
xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()
xymax = max(xmax, ymax)
plt.xlim(xmax=xymax)
plt.ylim(ymax=xymax)
plt.xlim(xmin=-5)
plt.ylim(ymin=-5)
plt.title(u'整体法PEPB百分位(圆大小代表预期收益)', fontproperties=font, fontsize=16)
plt.xlabel(u'整体法PB百分位', fontproperties=font)
plt.ylabel(u'整体法PE百分位', fontproperties=font)
plt.axhline(y=10, color='#15b01a', alpha=1)
plt.axhline(y=20, color='#96f97b', alpha=1)
plt.axvline(x=10, color='#15b01a', alpha=1)
plt.axvline(x=20, color='#96f97b', alpha=1)
for i in range(len(myset)):
    plt.annotate(myset[i, 1], (100 * mytotal.iloc[i, 2], 100 * mytotal.iloc[i, 3]), fontproperties=font)

# fig = plt.figure(figsize=(20, 8))
# ax1 = fig.add_subplot(1,1,1)
# xmin,xmax= plt.xlim()
# ax1.get_xaxis().set_visible(True)
# total["Valuation"].plot(ax=ax1,color= 'blue')
# total["Valuation_pre"].plot(ax=ax1,color= 'blue',linestyle= '-.')
# total["Holding"].plot(ax=ax1,color= 'cyan')
# total["Holding_pre"].plot(ax=ax1,color= 'cyan',linestyle= '-.')
# plt.legend(['Valuation','Valuation_pre','Holding','Holding_pre'],fontsize='small',loc='best')
# ax1.set_xticks(num-1)
# ax1.set_xticklabels(total.index, fontproperties=font,fontsize='large',rotation=90)
# xmin,xmax= plt.xlim()
# plt.title(u'全市场仓位(保守)和估值',fontproperties=font,fontsize=16)
# plt.hlines(25,xmin,xmax+1,color= 'green',linestyle= '-.')
# plt.hlines(75,xmin,xmax+1,color= 'red',linestyle= '-.')
# plt.hlines(50,xmin,xmax+1,color= 'yellow',linestyle= '-.')

endtime = datetime.now()
print(u'程序运行时间(秒):'),
print(endtime - starttime).seconds


"""
数据缓存日期:20200207
最新日期:2020-02-17
沪深A股进度:
时间域百分位: 35%(上月:37%)
沪深A股 当前中位数PB: 2.4(上月:2.5)    中位数PB百分位:20%(上月:27%)
沪深A股 当前整体法PB:1.7(上月:1.8)       整体法PB百分位:44%(上月:46%)
低于当前PB时间(月):37.1
沪深A股 综合估值百分位（PB，时间）:30%(上月:34%)
当前整体法PE:17.9(上月:18.0)
当前买入预期年化收益率（不考虑估值变化）:8.7%(上月:8.7%)
仓位2P-1（激进）:38%(上月:31%)
仓位(2P-1)/2(保守):19%(上月:15%)
沪深A股 定投比例:0%(上月:0%)
"""
