import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

TZ_TAIPEI = ZoneInfo("Asia/Taipei")
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# 載入環境變數
load_dotenv()

app = FastAPI()

# 設定靜態檔案路由 (供網頁取得 CSS, JS, HTML)
# Note: 確保有 static 資料夾
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
# 取得 Zeabur 提供的 AI API Key
ZEABUR_AI_API_KEY = os.getenv("ZEABUR_AI_API_KEY")

client = None
if ZEABUR_AI_API_KEY:
    # 透過 Zeabur AI Gateway 呼叫 OpenAI 模型
    client = OpenAI(
        api_key=ZEABUR_AI_API_KEY,
        base_url="https://hnd1.aihub.zeabur.ai/"
    )

# 限制設定
LIMIT_PER_DAY = 5
# 使用絕對路徑以確保在不同啟動目錄下都能正確讀取
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USAGE_FILE = os.path.join(BASE_DIR, "usage_stats.json")

def get_real_ip(request: Request):
    # 優先從 Zeabur 代理讀取真實用戶 IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For 可能包含多個 IP，取第一個真實位址
        return forwarded.split(",")[0].strip()
    return request.client.host

def get_usage_db():
    try:
        if not os.path.exists(USAGE_FILE):
            # 初始化空檔案
            with open(USAGE_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"Error loading usage DB: {e}")
        return {}

def save_usage_db(db):
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

def get_usage(ip: str):
    today = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d")  # 台灣時間
    db = get_usage_db()
    day_data = db.get(today, {})
    return day_data.get(ip, 0)

def increment_usage(ip: str):
    print(f"Incrementing usage for IP: {ip}")
    today = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d")  # 台灣時間
    db = get_usage_db()
    if today not in db:
        db[today] = {}
    db[today][ip] = db[today].get(ip, 0) + 1
    save_usage_db(db)

class AnalyzeRequest(BaseModel):
    ticker: str

def get_brave_search_results(query: str):
    """透過 Brave Search API 取得搜尋結果摘要"""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {"q": query, "count": 8, "search_lang": "zh-hant"}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results_text = ""
        for item in data.get('web', {}).get('results', []):
            results_text += f"[標題]: {item.get('title')}\n[內容]: {item.get('description')}\n---\n"
        return results_text
    except Exception as e:
        print(f"Brave API Error on query '{query}': {e}")
        return ""

def get_twse_closing_price(stock_no: str):
    """
    直接從台灣證交所(TWSE)官方API取得當日收盤價。
    若TWSE無資料(如上市前或OTC股)，再嘗試TPEx櫃買中心API。
    回傳: {"price": float, "date": str, "source": str} 或 None
    """
    now = datetime.now()
    # TWSE 資料通常在收盤後約15分鐘更新，若是週末則取上一個交易日
    query_day = now
    while query_day.weekday() >= 5:
        query_day -= timedelta(days=1)
    
    date_str = query_day.strftime("%Y%m%d")   # TWSE 格式：20260331
    date_display = query_day.strftime("%Y-%m-%d")

    # --- 嘗試 TWSE 上市股票 ---
    try:
        twse_url = (
            f"https://www.twse.com.tw/exchangeReport/STOCK_DAY"
            f"?response=json&stockNo={stock_no}&date={date_str}"
        )
        r = requests.get(twse_url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        rows = data.get("data", [])
        if rows:
            # 最後一筆是最新交易日，欄位: 日期/成交股數/成交金額/開盤/最高/最低/收盤/漲跌/成交筆數
            last_row = rows[-1]
            close_price = float(last_row[6].replace(",", ""))
            trade_date_raw = last_row[0]   # 民國年，例：115/03/31
            # 轉換民國年 → 西元年
            parts = trade_date_raw.split("/")
            trade_date = f"{int(parts[0]) + 1911}-{parts[1]}-{parts[2]}"
            print(f"[TWSE] {stock_no} 收盤價: {close_price} ({trade_date})")
            return {"price": close_price, "date": trade_date, "source": "台灣證交所(TWSE)"}
    except Exception as e:
        print(f"[TWSE] Error for {stock_no}: {e}")

    # --- 嘗試 TPEx 上櫃股票 ---
    try:
        tpex_date = f"{query_day.year - 1911}/{query_day.strftime('%m/%d')}"  # 民國年
        tpex_url = (
            f"https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php"
            f"?l=zh-tw&d={tpex_date}&stkno={stock_no}&_=1"
        )
        r = requests.get(tpex_url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        rows = data.get("aaData", [])
        if rows:
            last_row = rows[-1]
            close_price = float(last_row[6].replace(",", ""))
            trade_date_raw = last_row[0]
            parts = trade_date_raw.split("/")
            trade_date = f"{int(parts[0]) + 1911}-{parts[1]}-{parts[2]}"
            print(f"[TPEx] {stock_no} 收盤價: {close_price} ({trade_date})")
            return {"price": close_price, "date": trade_date, "source": "櫃買中心(TPEx)"}
    except Exception as e:
        print(f"[TPEx] Error for {stock_no}: {e}")

    print(f"[Price] 無法取得 {stock_no} 的收盤價")
    return None

def get_stock_info(keyword: str):
    """
    同時解析「公司簡稱」與「4位數字股票代號」。
    支援仿入：「中光電」/ 「5371」 / 「5371 中光電」 等幾種格式。
    回傳: (company_name: str, stock_no: str | None)
    """
    import re as _re
    # 先嘗試直接從輸入提取 4 位數字代號
    numbers = _re.findall(r'\d{4}', keyword)
    quick_no = numbers[0] if numbers else None

    query = f"台股 {keyword} 股票代號 公司名稱"
    search_context = get_brave_search_results(query)

    if not search_context and quick_no:
        return keyword.strip(), quick_no
    if not search_context:
        return keyword.strip(), None

    try:
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[
                {"role": "system", "content": """您是精通台股的助手。請從搜尋結果中提取：
1. 公司簡稱（中文，例：中光電、台積電）
2. 4位數字股票代號（例：5371、
