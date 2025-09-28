import pandas as pd

def compute_ma_cross(close_series, period, last_low, last_high, min_data=10):
    if len(close_series) < min_data:
        return "ND"
    ma_series = close_series.rolling(period, min_periods=1).mean()
    last_ma = ma_series.iloc[-1]
    last_close = close_series.iloc[-1]
    last_open = close_series.iloc[-2] if len(close_series) >= 2 else last_close
    if (last_low <= last_ma <= last_high) or \
       (last_open <= last_ma <= last_close) or \
       (last_close <= last_ma <= last_open):
        return "✅"
    return "❌"

def compute_ma_cross_lookback(close_series, period, lookback=3):
    if len(close_series) < period + lookback:
        return "ND"
    ma_series = close_series.rolling(period, min_periods=1).mean()
    crossed = False
    for i in range(-lookback, 0):
        prev_close = close_series.iloc[i-1]
        last_close = close_series.iloc[i]
        prev_ma = ma_series.iloc[i-1]
        last_ma = ma_series.iloc[i]
        if (prev_close < prev_ma and last_close > last_ma) or \
           (prev_close > prev_ma and last_close < last_ma):
            crossed = True
            break
    return "✅" if crossed else "❌"
