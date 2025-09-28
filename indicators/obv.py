# indicators/obv.py

def compute_obv(close_prices, volumes):
    """
    close_prices: لیستی از قیمتِ بسته شدن
    volumes: لیستی از حجم متناظر با هر دوره
    return: لیستی از مقادیر OBV (شروع از 0 یا None برای اولین)
    """
    obv = [None] * len(close_prices)
    obv[0] = 0  # یا None، بسته به اینکه می‌خواهی
    for i in range(1, len(close_prices)):
        if close_prices[i] > close_prices[i - 1]:
            obv[i] = obv[i - 1] + volumes[i]
        elif close_prices[i] < close_prices[i - 1]:
            obv[i] = obv[i - 1] - volumes[i]
        else:
            obv[i] = obv[i - 1]
    return obv
