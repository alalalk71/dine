# indicators/cci.py

import numpy as np

def compute_cci(high, low, close, period=14):
    """
    high, low, close: لیست یا آرایه هم‌اندازه
    period: دوره CCI
    return: لیستی از مقادیر CCI
    """
    length = len(high)
    cci = [None] * length
    typical_price = [(high[i] + low[i] + close[i]) / 3.0 for i in range(length)]
    # برای هر نقطه i ≥ period-1 محاسبه کن
    for i in range(period - 1, length):
        window = typical_price[i - period + 1 : i + 1]
        sma = sum(window) / period
        mean_dev = sum(abs(tp - sma) for tp in window) / period
        if mean_dev == 0:
            cci[i] = 0
        else:
            cci[i] = (typical_price[i] - sma) / (0.015 * mean_dev)
    return cci
