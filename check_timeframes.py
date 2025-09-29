import ccxt
import time
import json

# تنظیمات
API_KEY = "87AE73883EA94CFA974DACFCB02C5981"
API_SECRET = "677BB651D0628A51F8F357B78D3BE2897171ECFA5"
PROXY = "socks5h://127.0.0.1:2080"

MAX_CANDLES = 500
SLEEP_BETWEEN_REQS = 1.25
RETRY_COUNT = 3

# تایم‌فریم‌ها برای بررسی
REQUEST_TFS = [
    "1m", "3m", "5m", "15m", "30m",
    "1h", "2h", "3h", "4h", "6h", "8h", "12h",
    "1d", "2d", "3d", "4d", "5d",
    "1w", "2w"
]

# بارگذاری دسته‌بندی‌ها
def load_categories(file_path="categories.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    ex = ccxt.coinex({
        "apiKey": API_KEY,
        "secret": API_SECRET,
        "enableRateLimit": True,
        "timeout": 30000,
        "proxies": {"http": PROXY, "https": PROXY}
    })

    categories = load_categories()

    for category_name, symbols in categories.items():
        print(f"\n📂 دسته‌بندی: {category_name} ({len(symbols)} نماد)")
        for symbol in symbols:
            print(f"\nنماد: {symbol}")
            for tf in REQUEST_TFS:
                for attempt in range(RETRY_COUNT):
                    try:
                        ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=MAX_CANDLES)
                        if not ohlcv or len(ohlcv) < 2:
                            print(f"⚠️ {tf}: داده ناکافی یا خالی")
                        else:
                            last_candle = ohlcv[-1]
                            print(f"✅ {tf}: Close={last_candle[4]}, High={last_candle[2]}")
                        break
                    except Exception as e:
                        print(f"⚠️ تلاش {attempt+1}/{RETRY_COUNT} برای {tf} شکست خورد: {e}")
                        time.sleep(SLEEP_BETWEEN_REQS)
                else:
                    print(f"❌ {tf}: بعد از {RETRY_COUNT} تلاش، موفق نشدیم")

if __name__ == "__main__":
    main()
