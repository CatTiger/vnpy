# -*- coding: utf-8 -*-
#
# Copyright 2017 Ricequant, Inc
import numpy as np


FIELD_METHOD_MAP = {
    "open": "first",
    "close": "last",
    "iopv": "last",
    "high": np.maximum,
    "low": np.minimum,
    "limit_up": np.maximum,
    "limit_down": np.minimum,
    "total_turnover": np.add,
    "volume": np.add,
    "num_trades": np.add,
    "acc_net_value": "last",
    "unit_net_value": "last",
    "discount_rate": "last",
    "settlement": "last",
    "prev_settlement": "last",
    "open_interest": "last",
    "basis_spread": "last",
    "date": "last",
    "trading_date": "last",
    "datetime": "last",
}


def resample_day_bar(array, n, field):
    length = len(array)
    how = FIELD_METHOD_MAP[field]
    if how == 'first':
        return array[::n]

    # python2.7 `/` equals '//'
    slices = np.arange(0, int(np.ceil(length / float(n))) * n + 1, n)
    slices[-1] = length
    if how == 'last':
        return array[slices[1:] - 1]

    return how.reduceat(array, slices[:-1])
