import pandas as pd

def simple_zigzag(df, pct=5):
    zz = pd.Series(0, index=df.index)
    last_pivot = df['close'].iloc[0]
    trend = 0
    for i in range(1, len(df)):
        change = (df['close'].iloc[i] - last_pivot) / last_pivot * 100
        if trend <= 0 and change >= pct:
            zz.iloc[i] = 1
            last_pivot = df['close'].iloc[i]
            trend = 1
        elif trend >= 0 and change <= -pct:
            zz.iloc[i] = -1
            last_pivot = df['close'].iloc[i]
            trend = -1
    return zz

def detect_divergence_with_zigzag(df, indicator, pct=5):
    if len(df) < 10:
        return "ND"
    zz = simple_zigzag(df, pct)
    highs_idx = zz[zz==1].index
    lows_idx = zz[zz==-1].index
    result = False
    if len(lows_idx) >= 2:
        p1, p2 = df['close'][lows_idx[-2]], df['close'][lows_idx[-1]]
        i1, i2 = indicator[lows_idx[-2]], indicator[lows_idx[-1]]
        if (p2 < p1 and i2 > i1) or (p2 > p1 and i2 < i1):
            result = True
    if len(highs_idx) >= 2:
        p1, p2 = df['close'][highs_idx[-2]], df['close'][highs_idx[-1]]
        i1, i2 = indicator[highs_idx[-2]], indicator[highs_idx[-1]]
        if (p2 > p1 and i2 < i1) or (p2 < p1 and i2 > i1):
            result = True
    return result
