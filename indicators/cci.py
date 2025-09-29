# indicators/cci.py
import pandas as pd
import numpy as np
from .zigzag import simple_zigzag

def compute_cci(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    محاسبه CCI با فرمول استاندارد
    (min_periods=1 برای جلوگیری از NaN بیش از حد)
    """
    tp = (df['high'] + df['low'] + df['close']) / 3.0
    sma = tp.rolling(period, min_periods=1).mean()
    mean_dev = tp.rolling(period, min_periods=1).apply(
        lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
    )
    denom = 0.015 * mean_dev
    denom = denom.replace(0, np.nan)  # جلوگیری از تقسیم بر صفر
    cci = (tp - sma) / denom
    return cci

def analyze_cci(df: pd.DataFrame, period: int, ma_period: int, pct: float = 5.0):
    """
    محاسبهٔ سیگنال‌های CCI برای یک دوره مشخص.
    خروجی‌ها: cci (Series), ob, os, div_s (bearish), div_n (bullish), above_ma
    - above_ma همیشه True یا False خواهد بود وقتی دیتا قابل استفاده وجود دارد.
    - اگر دیتا کاملاً خالی باشد، ob/os/div_* = "ND" و above_ma = False برگردانده می‌شود.
    """
    # اگر دیتای ورودی خالی است
    if df is None or df.empty:
        return {"cci": pd.Series(dtype=float), "ob": "ND", "os": "ND",
                "div_s": "ND", "div_n": "ND", "above_ma": False}

    # حذف آخرین کندل ناقص (اگر وجود داشته باشد)
    df2 = df.iloc[:-1] if len(df) > 1 else df.copy()

    cci_series = compute_cci(df2, period)

    # آخرین ایندکس با مقدار معتبر CCI
    last_valid = cci_series.last_valid_index()
    if last_valid is None:
        # هیچ مقدار معتبری وجود ندارد
        return {"cci": cci_series, "ob": "ND", "os": "ND",
                "div_s": "ND", "div_n": "ND", "above_ma": False}

    last_cci = float(cci_series.loc[last_valid])

    # حساب MA با min_periods=1 تا حتی با داده‌های کم مقدار داشته باشد
    ma_series = cci_series.rolling(ma_period, min_periods=1).mean()

    # تلاش برای گرفتن مقدار MA در همان ایندکس؛ اگر NaN بود، از مقادیر قبلی میانگین می‌گیریم
    try:
        last_ma = float(ma_series.loc[last_valid])
    except Exception:
        last_ma = np.nan

    if pd.isna(last_ma):
        subset = cci_series.loc[:last_valid].dropna()
        if len(subset) > 0:
            # میانگین از آخرین مقادیر تا طول ma_period (fallback)
            last_ma = float(subset.tail(ma_period).mean())
        else:
            # هیچ مقدار معتبری وجود نداشت — در این حالت MA را برابر CCI قرار می‌دهیم تا above_ma = False شود
            last_ma = last_cci

    # اکنون above_ma همیشه بولین است (True/False)
    above_ma = bool(last_cci > last_ma)

    # OB / OS
    ob = bool(last_cci > 100)
    os = bool(last_cci < -100)

    # واگرایی‌ها با استفاده از simple_zigzag (همان منطق قبل)
    zz = simple_zigzag(df2, pct=pct)
    highs = list(zz[zz == 1].index)
    lows = list(zz[zz == -1].index)

    div_s = False  # bearish divergence (price HH, ind LH)
    div_n = False  # bullish divergence (price LL, ind HL)

    if len(highs) >= 2:
        i1, i2 = highs[-2], highs[-1]
        try:
            if (df2['close'].loc[i2] > df2['close'].loc[i1]) and (cci_series.loc[i2] < cci_series.loc[i1]):
                div_s = True
        except Exception:
            div_s = False

    if len(lows) >= 2:
        i1, i2 = lows[-2], lows[-1]
        try:
            if (df2['close'].loc[i2] < df2['close'].loc[i1]) and (cci_series.loc[i2] > cci_series.loc[i1]):
                div_n = True
        except Exception:
            div_n = False

    return {
        "cci": cci_series,
        "ob": ob,
        "os": os,
        "div_s": div_s,
        "div_n": div_n,
        "above_ma": above_ma,
    }

def cci_analysis(df: pd.DataFrame, ma_period_14: int = 10, ma_period_50: int = 20, pct: float = 5.0):
    """
    آنالیز CCI برای دوره‌های 14 و 50 با ma_period جداگانه.
    """
    res14 = analyze_cci(df, 14, ma_period_14, pct=pct)
    res50 = analyze_cci(df, 50, ma_period_50, pct=pct)
    return {"cci14": res14, "cci50": res50}
