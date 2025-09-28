import pandas as pd

RSI_PERIOD = 14
RSI_MA_PERIOD = 14
RSI_MA_TYPE = "SMA"

def compute_rsi(series, period=RSI_PERIOD):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    ma_up = up.ewm(com=period-1, adjust=False).mean()
    ma_down = down.ewm(com=period-1, adjust=False).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def compute_rsi_ma(rsi_series, ma_period=RSI_MA_PERIOD, ma_type=RSI_MA_TYPE):
    if ma_type.upper() == "SMA":
        return rsi_series.rolling(ma_period, min_periods=1).mean()
    else:
        return rsi_series.ewm(span=ma_period, adjust=False).mean()
