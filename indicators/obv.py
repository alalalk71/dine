import pandas as pd
import numpy as np

def compute_obv(df):
    """
    محاسبه OBV ساده
    """
    obv = [0]
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)


def detect_divergence_obv(df, obv_series):
    """
    شناسایی واگرایی OBV با استفاده از الگوریتم زیگزاگ ساده
    خروجی:
    - dn_signal: True اگر واگرایی نزولی پیدا شد
    - ds_signal: True اگر واگرایی صعودی پیدا شد
    - last_dn_index: اندیس آخرین واگرایی نزولی
    - last_ds_index: اندیس آخرین واگرایی صعودی
    """
    highs = df['high'].values
    lows = df['low'].values
    closes = df['close'].values
    obv = obv_series.values

    dn_signal, ds_signal = False, False
    last_dn_index, last_ds_index = None, None

    for i in range(2, len(obv)):
        # بررسی قله (نزولی)
        if obv[i-2] < obv[i-1] > obv[i] and closes[i-2] < closes[i-1] > closes[i]:
            dn_signal = True
            last_dn_index = i

        # بررسی کف (صعودی)
        if obv[i-2] > obv[i-1] < obv[i] and closes[i-2] > closes[i-1] < closes[i]:
            ds_signal = True
            last_ds_index = i

    return dn_signal, ds_signal, last_dn_index, last_ds_index


def analyze_obv(df):
    """
    تحلیل OBV:
    - obv_dn: واگرایی بالا (نشان نزولی)
    - obv_ds: واگرایی پایین (نشان صعودی)
    - obv_m: True/False اگر OBV بالای میانگین خودش باشد
    """
    obv = compute_obv(df)
    obv_ma = obv.rolling(10).mean()

    dn_signal, ds_signal, last_dn_idx, last_ds_idx = detect_divergence_obv(df, obv)

    # جلوگیری از همزمان سبز شدن
    if dn_signal and ds_signal:
        if last_dn_idx is not None and last_ds_idx is not None:
            if last_dn_idx > last_ds_idx:
                ds_signal = False
            else:
                dn_signal = False
        else:
            # اگر نتوانستیم تشخیص بدهیم، هر دو را False می‌کنیم
            dn_signal = False
            ds_signal = False

    obv_m = bool(obv.iloc[-1] > obv_ma.iloc[-1])

    return {
        "obv": obv,
        "obv_dn": dn_signal,
        "obv_ds": ds_signal,
        "obv_m": obv_m
    }