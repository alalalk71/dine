import ccxt, time, pandas as pd
from indicators.rsi import compute_rsi, compute_rsi_ma
from indicators.macd import compute_macd
from indicators.ma import compute_ma_cross, compute_ma_cross_lookback
from indicators.zigzag import detect_divergence_with_zigzag
from indicators.stochrsi import stoch_rsi
from indicators.cci import cci_analysis
from indicators.obv import analyze_obv
from utils import format_cell, save_html
from data_storage import init_structure, load_data, update_coin, save_data, save_html_dynamic

API_KEY = "87AE73883EA94CFA974DACFCB02C5981"
API_SECRET = "677BB651D0628A51F8F357B78D3BE2897171ECFA5"
PROXY = "socks5h://127.0.0.1:2080"

MAX_CANDLES = 500
SLEEP_BETWEEN_REQS = 1.25
RETRY_COUNT = 3

def load_categories(file_path="categories.json"):
    import json
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

    # فقط تایم‌فریم‌های معتبر
    REQUEST_TFS = [
        "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "12h",
        "1d", "3d",
        "1w"
    ]

    INDICATORS = [
        "CM55","M55","M200","CM200","DM","DR","MR","SROS","SROB","SRD",
        "CCI14_OB","CCI14_OS","CCI14_S","CCI14_N","CCI14_M",
        "CCI50_OB","CCI50_OS","CCI50_S","CCI50_N","CCI50_M",
        "OBV_DN","OBV_DS","OBV_M"
    ]

    results_all = load_data()
    if not results_all:
        results_all = init_structure(categories, REQUEST_TFS, INDICATORS)

    MA_CANDLES = {
        "1m": {"m55": 55, "m200": 200}, "3m": {"m55": 55, "m200": 200}, "5m": {"m55": 55, "m200": 200},
        "15m": {"m55": 55, "m200": 200}, "30m": {"m55": 55, "m200": 200},
        "1h": {"m55": 55, "m200": 200}, "2h": {"m55": 55, "m200": 200}, "4h": {"m55": 55, "m200": 100},
        "6h": {"m55": 55, "m200": 100}, "12h": {"m55": 55, "m200": 60},
        "1d": {"m55": 55, "m200": 60}, "3d": {"m55": 55, "m200": 60},
        "1w": {"m55": 55, "m200": 60},
    }

    for category_name, symbols in categories.items():
        print(f"\n📂 دسته‌بندی: {category_name} ({len(symbols)} نماد)")

        for idx, symbol in enumerate(symbols, start=1):
            try:
                for tf in REQUEST_TFS:
                    # دریافت دیتا با چند بار تلاش
                    for attempt in range(RETRY_COUNT):
                        try:
                            ohlcv = ex.fetch_ohlcv(symbol, timeframe=tf, limit=MAX_CANDLES)
                            break
                        except Exception as e:
                            print(f"⚠️ تلاش {attempt+1}/{RETRY_COUNT} برای {symbol} ({tf}) شکست خورد: {e}")
                            time.sleep(SLEEP_BETWEEN_REQS)
                    else:
                        print(f"❌ {tf}: بعد از {RETRY_COUNT} تلاش، موفق نشدیم")
                        continue

                    if not ohlcv:
                        continue

                    df = pd.DataFrame(ohlcv, columns=["ts", "open", "high", "low", "close", "volume"])
                    df["dt"] = pd.to_datetime(df["ts"], unit="ms")
                    df.set_index("dt", inplace=True)
                    last_low, last_high = df["low"].iloc[-1], df["high"].iloc[-1]

                    # --- محاسبه اندیکاتورها ---
                    df["rsi"] = compute_rsi(df["close"])
                    df["rsi_ma"] = compute_rsi_ma(df["rsi"])
                    df["macd"], df["signal"], df["hist"] = compute_macd(df["close"])

                    m55_val = compute_ma_cross(df["close"], MA_CANDLES[tf]["m55"], last_low, last_high)
                    cm55_val = compute_ma_cross_lookback(df["close"], MA_CANDLES[tf]["m55"])
                    m200_val = compute_ma_cross(df["close"], MA_CANDLES[tf]["m200"], last_low, last_high)
                    cm200_val = compute_ma_cross_lookback(df["close"], MA_CANDLES[tf]["m200"])

                    dm_val = detect_divergence_with_zigzag(df, df["macd"])
                    dr_val = detect_divergence_with_zigzag(df, df["rsi"])
                    mr_val = df["rsi"].iloc[-1] > df["rsi_ma"].iloc[-1]

                    stoch_df = stoch_rsi(df)
                    sros_val = stoch_df["sros"].iloc[-1] == 1
                    srob_val = stoch_df["srob"].iloc[-1] == 1
                    srd_val = stoch_df["srd"].iloc[-1] != 0

                    cci_vals = cci_analysis(df)
                    cci14, cci50 = cci_vals["cci14"], cci_vals["cci50"]

                    obv_vals = analyze_obv(df)

                    coin_data = {
                        "CM55": m55_val, "M55": cm55_val, "M200": m200_val, "CM200": cm200_val,
                        "DM": dm_val, "DR": dr_val, "MR": mr_val, "SROS": sros_val, "SROB": srob_val, "SRD": srd_val,
                        "CCI14_OB": cci14["ob"], "CCI14_OS": cci14["os"], "CCI14_S": cci14["div_s"], "CCI14_N": cci14["div_n"], "CCI14_M": cci14["above_ma"],
                        "CCI50_OB": cci50["ob"], "CCI50_OS": cci50["os"], "CCI50_S": cci50["div_s"], "CCI50_N": cci50["div_n"], "CCI50_M": cci50["above_ma"],
                        "OBV_DN": obv_vals["obv_dn"], "OBV_DS": obv_vals["obv_ds"], "OBV_M": obv_vals["obv_m"]
                    }

                    update_coin(results_all, category_name, symbol, tf, coin_data)

                print(f"[{idx}/{len(symbols)}] {symbol} ✅ پردازش شد")

            except Exception as e:
                print(f"🚨 خطا در {symbol}: {e}")
                time.sleep(SLEEP_BETWEEN_REQS)
                continue

        # ذخیره داده‌ها و HTML بعد از پردازش هر دسته
        save_data(results_all)
        save_html_dynamic(results_all[category_name], REQUEST_TFS, category_name)

        print(f"✅ دسته‌بندی {category_name} پردازش شد و داده‌ها ذخیره شدند.")

    print("\n🎉 تمام دسته‌بندی‌ها پردازش شدند و داده‌ها ذخیره شدند.")

if __name__ == "__main__":
    main()
