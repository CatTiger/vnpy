from vnpy.analyze.object import IndexInfo
from vnpy.trader.database import database_manager
from vnpy.trader.constant import Interval
from vnpy.analyze.util.data_source import DataSource
from datetime import datetime, timedelta
from vnpy.analyze.view.main_view import MainView
from vnpy.analyze.util.mean_reversion import MeanReversion
from vnpy.trader.constant import IndexType
import vnpy.analyze.data.etf_codes as etfs

class Main:

    def main(self, index_info: IndexInfo):
        self.data_step(index_info)
        if index_info.cal_sr:
            # 1、最近1年的k线数据
            ds = DataSource()
            df = ds.load_bar_data(index_info.symbol, index_info.alias, start_date=datetime.now() - timedelta(365),
                                  end_data=datetime.now())
            mv = MainView(df)
            mv.draw_main()
        # 2、历史数据分析
        mean_reversion = MeanReversion(datetime(2010, 1, 1), datetime.now(), index_info.index_code,
                                       load_finance=index_info.cal_finance)
        if index_info.cal_close:
            # 价格相关
            mean_reversion.append_poly_line()
            mean_reversion.draw_close()
        if index_info.cal_finance:
            # 财务相关
            mean_reversion.append_expected_profit()
            mean_reversion.append_finance(n=index_info.rolling_gap_year)
            mean_reversion.append_pos(show=False)
            mean_reversion.print_detail()
            mean_reversion.draw_reference()

    def data_step(self, index_info: IndexInfo):
        """
        数据准备阶段
        :param index_info:
        :return:
        """
        newest_bar = database_manager.get_newest_bar_data(index_info.symbol, index_info.exchange, Interval.DAILY)
        if newest_bar is None:
            print('当前数据未初始化')
        filling_days = (datetime.now() - newest_bar.datetime).days + 3  # 需要补齐数据的天数
        ds = DataSource()
        if index_info.cal_close:
            # 保存最近收盘数据
            ds.save_bar_data(index_info.symbol, index_info.alias, filling_days)
        if index_info.cal_finance:
            # 保存最近金融相关数据
            trade_dates = [bar.datetime for bar in
                           database_manager.load_bar_data(index_info.symbol, index_info.exchange, Interval.DAILY,
                                                          datetime.now() - timedelta(days=filling_days),
                                                          datetime.now())]
            ds.save_index_finance(trade_dates=trade_dates, index_code=index_info.index_code)


if __name__ == "__main__":
    main = Main()
    # main.main(IndexInfo('000300.XSHG', '', '', datetime(2009, 1, 1), IndexType.WIDE_BASE))
    # main.main(IndexInfo('000015.XSHG', '', '', datetime(2009, 1, 1), IndexType.INDUSTRY))
    # main.main(IndexInfo('513100.XSHG', '', '', datetime(2014, 1, 1), IndexType.INDUSTRY, inited=True, cal_finance=False,
    #                     rolling_gap_year=3))
