import os
import json
from datetime import datetime
from utils import save_html

JSON_FILE = "data.json"

def init_structure(categories, tfs, indicators):
    structure = {}
    for cat_name, symbols in categories.items():
        structure[cat_name] = {}
        for symbol in symbols:
            structure[cat_name][symbol] = {}
            for tf in tfs:
                structure[cat_name][symbol][tf] = {ind: "ND" for ind in indicators}
    return structure

def load_data(file_path=JSON_FILE):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری {file_path}: {e}")
            return {}
    return {}

def serialize_data(data):
    """
    تبدیل تمام مقادیر bool, None و tuple به string برای JSON
    """
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(v) for v in data]
    elif isinstance(data, tuple):
        # اگر tuple (value, class) بود فقط value رو ذخیره کن
        return str(data[0])
    elif data is True:
        return "✅"
    elif data is False:
        return "❌"
    elif data is None:
        return "ND"
    else:
        return str(data)

def save_data(data, file_path=JSON_FILE):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serialize_data(data), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"🚨 خطا در ذخیره {file_path}: {e}")

def update_coin(data, category, symbol, tf, coin_data):
    if category not in data:
        data[category] = {}
    if symbol not in data[category]:
        data[category][symbol] = {}
    # حتما قبل از ذخیره serialize کنیم
    data[category][symbol][tf] = serialize_data(coin_data)

def save_html_dynamic(results, tfs, file_name="scan.html"):
    save_html(results, tfs, file_name)
