import ccxt, time, pandas as pd, json
from indicators.rsi import compute_rsi, compute_rsi_ma
from indicators.macd import compute_macd
from indicators.ma import compute_ma_cross, compute_ma_cross_lookback
from indicators.zigzag import detect_divergence_with_zigzag
from utils import format_cell, save_html

API_KEY = ""
API_SECRET = ""
PROXY = 'socks5h://127.0.0.1:2080'
REQUEST_TFS = ["12h","1d","3d","1w"]
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
    with open(file_path,"r",encoding="utf-8") as f:
        return json.load(f)

def main():
    ex = ccxt.coinex({'apiKey': API_KEY,'secret': API_SECRET,'enableRateLimit': True,'timeout':30000,'proxies':{'http':PROXY,'https':PROXY}})
    categories = load_categories()
    for category_name, symbols in categories.items():
        results = {}
        print(f"\n📂 دسته‌بندی: {category_name} ({len(symbols)} نماد)")
        for idx, symbol in enumerate(symbols, start=1):
            results[symbol] = {}
            try:
                for tf in REQUEST_TFS:
                    for attempt in range(RETRY_COUNT):
                        try:
                            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=MAX_CANDLES)
                            break
                        except Exception as e:
                            print(f"⚠️ {symbol} {tf} تلاش {attempt+1}: {e}")
                            time.sleep(SLEEP_BETWEEN_REQS)
                    else:
                        continue

                    if not ohlcv:
                        results[symbol][tf] = None
                        continue

                    df = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','volume'])
                    df['dt'] = pd.to_datetime(df['ts'], unit='ms')
                    df.set_index('dt', inplace=True)
                    last_low = df['low'].iloc[-1]
                    last_high = df['high'].iloc[-1]

                    df['rsi'] = compute_rsi(df['close'])
                    df['rsi_ma'] = compute_rsi_ma(df['rsi'])
                    df['macd'], df['signal'], df['hist'] = compute_macd(df['close'])

                    m55_val = compute_ma_cross(df['close'], MA_CANDLES[tf]["m55"], last_low, last_high)
                    cm55_val = compute_ma_cross_lookback(df['close'], MA_CANDLES[tf]["m55"])
                    m200_val = compute_ma_cross(df['close'], MA_CANDLES[tf]["m200"], last_low, last_high)
                    cm200_val = compute_ma_cross_lookback(df['close'], MA_CANDLES[tf]["m200"])
                    dm_val = detect_divergence_with_zigzag(df, df['macd'])
                    dr_val = detect_divergence_with_zigzag(df, df['rsi'])
                    mr_val = "✅" if df['rsi'].iloc[-1] > df['rsi_ma'].iloc[-1] else "❌"

                    results[symbol][tf] = {
                        "m55_fmt": format_cell(m55_val),
                        "cm55_fmt": format_cell(cm55_val),
                        "m200_fmt": format_cell(m200_val),
                        "cm200_fmt": format_cell(cm200_val),
                        "dm_fmt": format_cell(dm_val),
                        "dr_fmt": format_cell(dr_val),
                        "mr_fmt": format_cell(mr_val),
                    }

                print(f"[{idx}/{len(symbols)}] {symbol} پردازش شد.")
            except Exception as e:
                print(f"⚠️ خطا در {symbol}: {e}")
                time.sleep(SLEEP_BETWEEN_REQS)
                continue

        file_name = f"{category_name.replace(' ','_')}.html"
        save_html(results, REQUEST_TFS, file_name)
        print(f"✅ فایل {file_name} ساخته شد.")

    print("\n🎉 تمام دسته‌بندی‌ها پردازش شدند.")

if __name__=="__main__":
    main()
