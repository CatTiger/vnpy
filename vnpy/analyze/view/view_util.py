import pandas as pd


def relative_strength_index(df, n):
    """Calculate Relative Strength Index(RSI) for given data.

    :param df: pandas.DataFrame
    :param n:
    :return: pandas.DataFrame
    """
    i = 0
    UpI = [0]
    DoI = [0]
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i + 1, 'high'] - df.loc[i, 'high']
        DoMove = df.loc[i, 'low'] - df.loc[i + 1, 'low']
        if UpMove > DoMove and UpMove > 0:
            UpD = UpMove
        else:
            UpD = 0
        UpI.append(UpD)
        if DoMove > UpMove and DoMove > 0:
            DoD = DoMove
        else:
            DoD = 0
        DoI.append(DoD)
        i = i + 1
    UpI = pd.Series(UpI)
    DoI = pd.Series(DoI)
    PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
    NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean())
    RSI = pd.Series(100 * PosDI / (PosDI + NegDI), name='RSI_' + str(n))
    df = df.join(RSI)
    return df


def macd(df, n_fast=12, n_slow=26, diff_dea=9):
    """Calculate MACD, MACD Signal and MACD difference

    :param df: pandas.DataFrame
    :param n_fast: 12
    :param n_slow: 26
    :param diff_dea: 9
    :return: pandas.DataFrame
    """
    df_macd = pd.DataFrame(columns=('DIFF', 'DEA', 'MACD'))
    fast_ema = pd.Series(df['close'].ewm(span=n_fast, min_periods=n_fast).mean())
    slow_ema = pd.Series(df['close'].ewm(span=n_slow, min_periods=n_slow).mean())
    diff = pd.Series(fast_ema - slow_ema, name='DIFF')
    dea = pd.Series(diff.ewm(span=diff_dea, min_periods=diff_dea).mean(), name='DEA')
    macd = pd.Series(2 * (diff - dea), name='MACD')
    df_macd['DIFF'] = diff
    df_macd['DEA'] = dea
    df_macd['MACD'] = macd
    return df_macd
