# main.py

import ccxt
import time
import pandas as pd
import json

from indicators.rsi import compute_rsi, compute_rsi_ma
from indicators.macd import compute_macd
from indicators.ma import compute_ma_cross, compute_ma_cross_lookback
from indicators.zigzag import detect_divergence_with_zigzag

# اندیکاتورهای جدید
from indicators.stoch_rsi import compute_stoch_rsi
from indicators.obv import compute_obv
from indicators.cci import compute_cci

from utils import format_cell, save_html

API_KEY = ""
API_SECRET = ""
PROXY = 'socks5h://127.0.0.1:2080'

REQUEST_TFS = ["12h", "1d", "3d", "1w"]
MAX_CANDLES = 500
SLEEP_BETWEEN_REQS = 1.25
RETRY_COUNT = 3

MA_CANDLES = {
    "12h": {"m55": 55, "m200": 200},
    "1d": {"m55": 55, "m200": 200},
    "3d": {"m55": 55, "m200": 100},
    "1w": {"m55": 55, "m200": 60},
}

def load_categories(file_path="categories.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def process_symbol_for_tf(df, tf):
    """
    دریافت DataFrame دارای ستون‌های open, high, low, close, volume 
    و محاسبه تمام اندیکاتورها برای آن تایم‌فریم.
    برمی‌گرداند دیکشنری از مقادیر قالب‌بندی‌شده برای ذخیره در results.
    """
    result = {}

    # محاسبه اندیکاتورهای پایه
    df['rsi'] = compute_rsi(df['close'])
    df['rsi_ma'] = compute_rsi_ma(df['rsi'])
    df['macd'], df['signal'], df['hist'] = compute_macd(df['close'])

    # محاسبه MA cross ها
    last_low = df['low'].iloc[-1]
    last_high = df['high'].iloc[-1]
    m55_val = compute_ma_cross(df['close'], MA_CANDLES[tf]["m55"], last_low, last_high)
    cm55_val = compute_ma_cross_lookback(df['close'], MA_CANDLES[tf]["m55"])
    m200_val = compute_ma_cross(df['close'], MA_CANDLES[tf]["m200"], last_low, last_high)
    cm200_val = compute_ma_cross_lookback(df['close'], MA_CANDLES[tf]["m200"])

    # تشخیص واگرایی
    dm_val = detect_divergence_with_zigzag(df, df['macd'])
    dr_val = detect_divergence_with_zigzag(df, df['rsi'])

    # MR (مثلاً مقایسه rsi با میانگینش)
    mr_val = "✅" if df['rsi'].iloc[-1] > df['rsi_ma'].iloc[-1] else "❌"

    # محاسبه اندیکاتورهای جدید
    stoch_k, stoch_d = compute_stoch_rsi(df['close'])
    obv = compute_obv(df['close'], df['volume'])
    cci14 = compute_cci(df['high'], df['low'], df['close'], period=14)
    cci50 = compute_cci(df['high'], df['low'], df['close'], period=50)

    # قالب‌بندی مقادیر برای HTML
    result["m55_fmt"] = format_cell(m55_val)
    result["cm55_fmt"] = format_cell(cm55_val)
    result["m200_fmt"] = format_cell(m200_val)
    result["cm200_fmt"] = format_cell(cm200_val)
    result["dm_fmt"] = format_cell(dm_val)
    result["dr_fmt"] = format_cell(dr_val)
    result["mr_fmt"] = format_cell(mr_val)

    result["stoch_k_fmt"] = format_cell(stoch_k[-1] if stoch_k else "ND")
    result["stoch_d_fmt"] = format_cell(stoch_d[-1] if stoch_d else "ND")
    result["obv_fmt"] = format_cell(obv[-1] if obv else "ND")
    result["cci14_fmt"] = format_cell(cci14[-1] if cci14 else "ND")
    result["cci50_fmt"] = format_cell(cci50[-1] if cci50 else "ND")

    return result

def main():
    ex = ccxt.coinex({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'timeout': 30000,
        'proxies': {'http': PROXY, 'https': PROXY}
    })

    categories = load_categories()
    for category_name, symbols in categories.items():
        results = {}
        print(f"\nدسته‌بندی: {category_name} ({len(symbols)} نماد)")
        for idx, symbol in enumerate(symbols, start=1):
            results[symbol] = {}
            try:
                for tf in REQUEST_TFS:
                    # تلاش چندباره برای دریافت داده
                    ohlcv = None
                    for attempt in range(RETRY_COUNT):
                        try:
                            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=MAX_CANDLES)
                            break
                        except Exception as e:
                            print(f"⚠️ {symbol} {tf} تلاش {attempt+1}: {e}")
                            time.sleep(SLEEP_BETWEEN_REQS)
                    if not ohlcv:
                        results[symbol][tf] = None
                        continue

                    # ساخت DataFrame
                    df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','volume'])
                    df['dt'] = pd.to_datetime(df['ts'], unit='ms')
                    df.set_index('dt', inplace=True)

                    # پردازش اندیکاتورها برای این نماد و تایم‌فریم
                    result = process_symbol_for_tf(df, tf)
                    results[symbol][tf] = result

                print(f"[{idx}/{len(symbols)}] {symbol} پردازش شد.")
            except Exception as e:
                print(f"⚠️ خطا در {symbol}: {e}")
                time.sleep(SLEEP_BETWEEN_REQS)
                # ادامه با نماد بعدی
                continue

        file_name = f"{category_name.replace(' ','_')}.html"
        save_html(results, REQUEST_TFS, file_name)
        print(f"✅ فایل {file_name} ساخته شد.")

    print("\nتمام دسته‌بندی‌ها پردازش شدند.")

if __name__ == "__main__":
    main()
