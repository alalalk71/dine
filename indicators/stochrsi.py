# indicators/stochrsi.py
import pandas as pd
import numpy as np
from .rsi import compute_rsi
from .zigzag import detect_divergence_with_zigzag

def stoch_rsi(df,
              rsi_period: int = 14,
              stoch_period: int = 14,
              smooth_k: int = 3,
              smooth_d: int = 3,
              overbought: float = 0.8,
              oversold: float = 0.2):
    """
    محاسبهٔ StochRSI با خروجی مشابه ساختار پروژه:
    ستون‌ها:
      - stoch_rsi_k
      - stoch_rsi_d
      - sros    (stochastic oversold -> 1/0)
      - srob    (stochastic overbought -> 1/0)
      - kd_cross_up, kd_cross_down
      - srd     (divergence flag broadcast شده روی تمام ایندکس‌ها: 1 اگر واگرایی وجود داشته باشد)
    """
    # امن‌سازی برای دیتاهای خیلی کوتاه
    min_len = max(rsi_period, stoch_period, smooth_k, smooth_d)
    if len(df) < 2 or len(df) < min_len:
        res = pd.DataFrame(index=df.index)
        res['stoch_rsi_k'] = np.nan
        res['stoch_rsi_d'] = np.nan
        res['sros'] = 0
        res['srob'] = 0
        res['kd_cross_up'] = 0
        res['kd_cross_down'] = 0
        res['srd'] = 0
        return res

    # 1) محاسبه RSI با تابع موجود در پروژه
    rsi = compute_rsi(df['close'], period=rsi_period)

    # 2) محاسبه StochRSI
    rsi_min = rsi.rolling(stoch_period, min_periods=1).min()
    rsi_max = rsi.rolling(stoch_period, min_periods=1).max()
    stochrsi = (rsi - rsi_min) / (rsi_max - rsi_min)

    # جلوگیری از تقسیم بر صفر باعث NaN می‌شود که رفتار منطقی است
    k = stochrsi.rolling(smooth_k, min_periods=1).mean()
    d = k.rolling(smooth_d, min_periods=1).mean()

    result = pd.DataFrame(index=df.index)
    result['stoch_rsi_k'] = k
    result['stoch_rsi_d'] = d

    # 3) Overbought / Oversold
    result['sros'] = (k < oversold).astype(int)   # oversold zone
    result['srob'] = (k > overbought).astype(int) # overbought zone

    # 4) K/D cross signals
    result['kd_cross_up'] = ((k > d) & (k.shift(1) <= d.shift(1))).astype(int)
    result['kd_cross_down'] = ((k < d) & (k.shift(1) >= d.shift(1))).astype(int)

    # 5) واگرایی — از zigzag موجود در پروژه استفاده می‌کنیم
    div = detect_divergence_with_zigzag(df, k)  # این تابع در indicators/zigzag.py موجود است
    # detect_divergence_with_zigzag ممکن است "ND" یا True/False برگرداند.
    if div == "ND":
        result['srd'] = 0
    else:
        result['srd'] = 1 if div else 0

    return result
