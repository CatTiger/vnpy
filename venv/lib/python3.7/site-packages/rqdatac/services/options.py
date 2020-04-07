# -*- coding: utf-8 -*-
import datetime

import pandas as pd

from rqdatac.validators import (
    check_items_in_container,
    ensure_date_int,
    ensure_order_book_ids,
)
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api

VALID_GREEKS_FIELDS = ['iv', 'delta', 'gamma', 'vega', 'theta', 'rho']


@export_as_api(namespace='options')
def get_greeks(order_book_ids, start_date=None, end_date=None, fields=None, model='implied_forward', market="cn"):
    """获取指定股票期权的隐含波动率iv， 以及5个希腊字母数值(delta, gamma, bega, theta, rho)
    :param order_book_ids: 股票 order_book_id or order_book_id list
    :param start_date: 开始日期, 必要参数
    :param end_date: 结束日期；默认为今天
    :param fields: str或list类型. 默认为None, 返回所有fields.
    :param model: str类型， last: 代表用每日close价格， implied_forward 代表用隐含风险收益率计算
    :param market: 默认值为"cn"
    """

    order_book_ids = ensure_order_book_ids(order_book_ids, market=market)
    check_items_in_container(model, ['implied_forward', 'last'], 'model')
    if start_date is not None:
        start_date = ensure_date_int(start_date)
    else:
        raise ValueError('start_date is expected')
    if end_date is not None:
        end_date = ensure_date_int(end_date)
    else:
        end_date = ensure_date_int(datetime.datetime.now().date())
    if end_date < start_date:
        raise ValueError("invalid date range: [{!r}, {!r}]".format(start_date, end_date))

    if fields is None:
        fields = VALID_GREEKS_FIELDS
    else:
        check_items_in_container(fields, VALID_GREEKS_FIELDS, 'Greeks')

    data = get_client().execute("options.get_greeks", order_book_ids, start_date, end_date, fields, model, market=market)
    if not data:
        return None

    df = pd.DataFrame(data)
    df.set_index(["order_book_id", "trading_date"], inplace=True)
    df.sort_index(inplace=True)
    return df[fields]
