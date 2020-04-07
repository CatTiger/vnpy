from typing import Any

from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarData,
    TradeData,
    OrderData,
    ArrayManager,
)
from vnpy.trader.constant import Direction


class PosDetail:
    """仓位详情"""
    # 当前仓位的ID
    pos_id: int
    # 合约数量
    contract_size: int
    # 标的数量
    quantity: int
    # 期望买入价格
    expect_price: float
    # atr震动幅度
    atr: float
    # 实际买入价格
    buy_price: float
    # 止损价格
    stop_loss_price: float
    # 实际卖出价格
    sell_price: float

    def __init__(self, pos_id, contract_size, quantity, expect_price, atr, stop_loss_price):
        self.pos_id = pos_id
        self.contract_size = contract_size
        self.quantity = quantity
        self.expect_price = expect_price
        self.atr = atr
        self.stop_loss_price = stop_loss_price


class RuntimeParam:
    """运行状态参数"""
    from typing import Dict, Set

    # 允许的仓位份数(不可变)
    _allow_pos_size: int
    # 每手最少单位(不可变)
    _least_contract_unit: int

    # 可用资金
    available_capital: float
    # 可买合约数量
    available_contract_size: int

    # 当前持有仓位详情
    _hold_pos_detail: Dict[int, PosDetail] = {}

    # 交易完成仓位信息
    _finished_pos_detail: Set[PosDetail] = {}

    # 仓位ID生成
    _pos_id_idx = 0

    def __init__(self, init_capital, allow_pos_size, least_contract_unit):
        self.available_capital = init_capital
        self._allow_pos_size = allow_pos_size
        self._least_contract_unit = least_contract_unit

    def current_pos(self):
        return len(self._hold_pos_detail)

    def subscribe_one_pos(self, close_price, atr, stop_loss_price):
        """订购一个仓位的标的数量"""
        hold_pos_num = len(self._hold_pos_detail)
        if hold_pos_num >= self._allow_pos_size:
            # 当前已经满仓
            print('error 预定不到，已经满仓！！！')
            return
        # 当前仓位使用资金
        pos_capital = self.available_capital / (self._allow_pos_size - hold_pos_num)
        # 合约份数
        contract_size = int(pos_capital / close_price / self._least_contract_unit)
        self._pos_id_idx += 1
        return PosDetail(self._pos_id_idx, contract_size, contract_size * self._least_contract_unit, close_price, atr,
                         stop_loss_price)

    def confirm_buy_pos(self, pos_detail: PosDetail, buy_price: float):
        """确认购买仓位"""
        pos_detail.buy_price = buy_price
        if not self._hold_pos_detail.__contains__(pos_detail.pos_id):
            self._hold_pos_detail[pos_detail.pos_id] = pos_detail
        else:
            print("error, can not confirm buy pos!!!")

    def apply_release_pos(self, pos_detail: PosDetail, sell_expect_price):
        """申请释放仓位"""
        pos_detail.sell_expect_price = sell_expect_price

    def confirm_sell_pos(self, pos_detail: PosDetail, sell_price: float):
        """确认卖出仓位"""
        pos_detail.sell_price = sell_price
        if not self._hold_pos_detail.__contains__(pos_detail.pos_id):
            print("error, can not confirm sell pos!!!")
        self._hold_pos_detail.pop(pos_detail.pos_id)
        self._finished_pos_detail.add(pos_detail)


class PosRelation:
    """仓位与订单关系"""
    order_id: int
    pos_detail: PosDetail
    # 仓位状态，buy_subscribe\sell_subscribe\buy_done\sell_done
    status: str
    # 仓位类型, sensitive\normal
    p_type: str

    def __init__(self, order_id, pos_detail, p_type, status):
        self.order_id = order_id
        self.pos_detail = pos_detail
        self.p_type = p_type
        self.status = status


class RSRSStrategy(CtaTemplate):
    from typing import Dict
    # 允许的最大损失系数
    allow_loss_point = 2

    # 初始化资金
    initial_capital = 10000
    # 允许的仓位份数
    allow_pos_size = 1
    # 每手最少单位
    least_contract_unit = 100

    # 内部仓位关系
    pos_relations: Dict[str, PosRelation] = {}

    # mach相关变量
    hist0 = 0.0
    hist1 = 0.0

    # 趋势相关（状态、购入价格、atr）
    trend_status = 'off'
    trend_buy_price = 0.0
    tread_atr = 0.0

    # ma
    f_fast_ma0 = 0.0
    f_fast_ma1 = 0.0

    fast_ma0 = 0.0
    fast_ma1 = 0.0

    slow_ma0 = 0.0
    slow_ma1 = 0.0

    def __init__(self, cta_engine: Any, strategy_name: str, vt_symbol: str, setting: dict):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        # dict, key: 当前日期， val：第二天开盘价
        self.his_data_dict = setting['his_data_dict']
        self.am = ArrayManager(1, setting['zscore_data'], 18)
        # 初始化参数转运行参数
        self.runtime_param = RuntimeParam(self.initial_capital, self.allow_pos_size, self.least_contract_unit)

    def on_init(self):
        self.write_log("策略初始化")
        self.load_bar(1)

    def _query_available_pos_cnt(self, p_type) -> int:
        """查询可用仓位数量，sensitive：1个，normal：3个"""
        result = 3
        if p_type == 'sensitive':
            result = 1
        for key in self.pos_relations:
            if self.pos_relations[key].p_type == p_type and (
                    self.pos_relations[key].status == 'buy_subscribe' or self.pos_relations[key].status == 'buy_done'):
                result = result - 1
        return result

    def _extract_order_id(self, order_id):
        if len(order_id) != 1:
            print('error can not extract order id!!')
        return order_id[0]

    def on_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)

        if not am.inited:
            return

        rsrs = am.rsrs_std()
        next_day_open_price = self.his_data_dict.get(bar.datetime.strftime('%Y-%m-%d'), -1)
        metric_atr = am.atr(14)
        print('date:%s, rsrs:%s' % (bar.datetime.strftime('%Y-%m-%d'), rsrs))
        # print('date:%s, rsrs:%s' % (bar.datetime.strftime('%Y-%m-%d'), rsrs))
        if rsrs > 0.7:
            print('---')
            # print('date:%s, rsrs:%s' % (bar.datetime.strftime('%Y-%m-%d'), rsrs))
            # current_pos = self.runtime_param.current_pos()
            # if current_pos < self.allow_pos_size and self._query_available_pos_cnt('sensitive') > 0:
            #     pos_detail = self.runtime_param.subscribe_one_pos(bar.close_price,
            #                                                       metric_atr,
            #                                                       next_day_open_price - self.allow_loss_point * metric_atr)
            #     order_id = self.buy(next_day_open_price, pos_detail.quantity)
            #     self.pos_relations[self._extract_order_id(order_id)] = PosRelation(self._extract_order_id(order_id),
            #                                                                        pos_detail, 'sensitive',
            #                                                                        'buy_subscribe')
            #     print('buy, date:%s, buy price:%s, quantity:%s, rsrs:%s' % (
            #         bar.datetime.strftime('%Y-%m-%d'), next_day_open_price, pos_detail.quantity, rsrs))
        if rsrs < -0.7:
            print('---')
            # print('date:%s, rsrs:%s' % (bar.datetime.strftime('%Y-%m-%d'), rsrs))
            # for key in list(self.pos_relations):
            #     pos_relation = self.pos_relations[key]
            #     if pos_relation.p_type == 'sensitive' and pos_relation.status == 'buy_done':
            #         order_id = self.sell(next_day_open_price, pos_relation.pos_detail.quantity)
            #         pos_relation.status = 'sell_subscribe'
            #         self.pos_relations[self._extract_order_id(order_id)] = pos_relation
            #         print('sell, date:%s, sell price:%s, quantity:%s, rsrs:%s' % (
            #             bar.datetime.strftime('%Y-%m-%d'), next_day_open_price, pos_relation.pos_detail.quantity, rsrs))

    def on_order(self, order: OrderData):
        """接收订单信息"""

    def on_trade(self, trade: TradeData):
        """接收交易信息"""
        order_id = trade.gateway_name + '.' + trade.orderid
        pos_relation = self.pos_relations[order_id]
        if pos_relation is None:
            print('error can not find pos by order id')
        if trade.direction == Direction.LONG:
            pos_relation.status = 'buy_done'
            pos_relation.pos_detail.buy_price = trade.price
        if trade.direction == Direction.SHORT:
            pos_relation.status = 'sell_done'
            pos_relation.pos_detail.sell_price = trade.price
