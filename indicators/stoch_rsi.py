# indicators/stoch_rsi.py
import pandas as pd
import numpy as np

def stoch_rsi_from_close(close: pd.Series,
                         rsi_period: int = 14,
                         stoch_period: int = 14,
                         k_period: int = 3,
                         d_period: int = 3,
                         scale_0_100: bool = True):
    """
    محاسبه Stochastic RSI فقط از سری close
    خروجی: DataFrame با ستون‌های ['rsi', 'stoch_k', 'stoch_d', 'signal']
    - rsi: مقدار RSI (0..100)
    - stoch_k: مقدار %K (0..100 اگر scale_0_100 True، در غیر اینصورت 0..1)
    - stoch_d: مقدار %D (میانگین متحرک %K)
    - signal: 1 برای کراس صعودی (%K از پایین %D را قطع کند)، -1 برای کراس نزولی، 0 یا NaN برای بی‌سیگنال
    """
    close = close.astype(float).copy()

    # 1) RSI (ساده، با SMA برای شروع)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.rolling(window=rsi_period, min_periods=1).mean()
    avg_loss = loss.rolling(window=rsi_period, min_periods=1).mean()

    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(0)

    # 2) Stochastic on RSI
    min_rsi = rsi.rolling(window=stoch_period, min_periods=1).min()
    max_rsi = rsi.rolling(window=stoch_period, min_periods=1).max()
    denom = (max_rsi - min_rsi).replace(0, np.nan)

    stoch_k = (rsi - min_rsi) / denom
    stoch_k = stoch_k.fillna(0)

    if scale_0_100:
        stoch_k = stoch_k * 100.0

    # smooth K to produce D
    if scale_0_100:
        stoch_d = stoch_k.rolling(window=d_period, min_periods=1).mean()
    else:
        stoch_d = stoch_k.rolling(window=d_period, min_periods=1).mean()

    # 3) signal: detect K x D crosses
    prev_k = stoch_k.shift(1)
    prev_d = stoch_d.shift(1)

    signal = pd.Series(data=0, index=close.index, dtype=int)
    signal[(prev_k < prev_d) & (stoch_k > stoch_d)] = 1     # bullish cross
    signal[(prev_k > prev_d) & (stoch_k < stoch_d)] = -1    # bearish cross

    # return DataFrame
    out = pd.DataFrame({
        'rsi': rsi,
        'stoch_k': stoch_k,
        'stoch_d': stoch_d,
        'signal': signal
    }, index=close.index)

    return out

def stoch_rsi(df: pd.DataFrame,
              close_col: str = 'close',
              rsi_period: int = 14,
              stoch_period: int = 14,
              k_period: int = 3,
              d_period: int = 3,
              scale_0_100: bool = True):
    """
    Wrapper که یک DataFrame (با ستونی به نام close_col) می‌گیرد
    و DataFrame خروجی با ایندکس همان df بازمی‌گرداند.
    """
    if close_col not in df.columns:
        raise ValueError(f"stoch_rsi: column '{close_col}' not found in df")

    close = df[close_col]
    return stoch_rsi_from_close(close,
                                rsi_period=rsi_period,
                                stoch_period=stoch_period,
                                k_period=k_period,
                                d_period=d_period,
                                scale_0_100=scale_0_100)
