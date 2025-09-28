# indicators/stoch_rsi.py
import numpy as np
from .rsi import compute_rsi  # فرض می‌کنیم تابع محاسبه RSI در rsi.py است

def compute_stoch_rsi(close_prices, period=14, smooth_k=3, smooth_d=3):
    """
    return tuple (stoch_rsi_k, stoch_rsi_d) arrays (یا لیست‌ها)
    """
    # ابتدا RSI را محاسبه کن
    rsi = compute_rsi(close_prices, period=period)
    stoch_rsi = [None] * len(rsi)
    # محاسبه استوک RSI خام
    for i in range(len(rsi)):
        if i < period - 1:
            stoch_rsi[i] = None
        else:
            window = rsi[i - period + 1 : i + 1]
            if window and None not in window:
                min_r = min(window)
                max_r = max(window)
                if max_r - min_r == 0:
                    stoch_rsi[i] = 0.0
                else:
                    stoch_rsi[i] = (rsi[i] - min_r) / (max_r - min_r)
            else:
                stoch_rsi[i] = None
    # smooth کردن %K
    stoch_k = [None] * len(rsi)
    for i in range(len(rsi)):
        if i < period - 1 + (smooth_k - 1):
            stoch_k[i] = None
        else:
            window = stoch_rsi[i - smooth_k + 1 : i + 1]
            if None not in window:
                stoch_k[i] = sum(window) / smooth_k
            else:
                stoch_k[i] = None
    # محاسبه %D (میانگین روی K)
    stoch_d = [None] * len(rsi)
    for i in range(len(rsi)):
        if i < period - 1 + (smooth_k - 1) + (smooth_d - 1):
            stoch_d[i] = None
        else:
            window = stoch_k[i - smooth_d + 1 : i + 1]
            if None not in window:
                stoch_d[i] = sum(window) / smooth_d
            else:
                stoch_d[i] = None

    return stoch_k, stoch_d
