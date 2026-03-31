import os
import re
import json
import asyncio
import httpx
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

TZ_TAIPEI = ZoneInfo("Asia/Taipei")
load_dotenv()

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
ZEABUR_AI_API_KEY = os.getenv("ZEABUR_AI_API_KEY")

client = None
if ZEABUR_AI_API_KEY:
    client = OpenAI(
        api_key=ZEABUR_AI_API_KEY,
        base_url="https://hnd1.aihub.zeabur.ai/"
    )

LIMIT_PER_DAY = 20
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USAGE_FILE = os.path.join(BASE_DIR, "usage_stats.json")

def get_real_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def get_usage_db():
    try:
        if not os.path.exists(USAGE_FILE):
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
    today = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d")
    db = get_usage_db()
    return db.get(today, {}).get(ip, 0)

def increment_usage(ip: str):
    print(f"Incrementing usage for IP: {ip}")
    today = datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d")
    db = get_usage_db()
    if today not in db:
        db[today] = {}
    db[today][ip] = db[today].get(ip, 0) + 1
    save_usage_db(db)

class AnalyzeRequest(BaseModel):
    ticker: str

# ── 【優化1】Brave 並行搜尋 ──────────────────────────────────────
async def brave_search_async(client_http: httpx.AsyncClient, query: str) -> str:
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {"q": query, "count": 8, "search_lang": "zh-hant"}
    try:
        response = await client_http.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        results_text = ""
        for item in data.get('web', {}).get('results', []):
            results_text += f"[標題]: {item.get('title')}\n[內容]: {item.get('description')}\n---\n"
        return results_text
    except Exception as e:
        print(f"Brave API Error on query '{query}': {e}")
        return ""

async def brave_search_all(queries: list[str]) -> list[str]:
    async with httpx.AsyncClient() as client_http:
        tasks = [brave_search_async(client_http, q) for q in queries]
        results = await asyncio.gather(*tasks)
    return list(results)

# ── 【優化2】TWSE / TPEx 同時送出 ───────────────────────────────
async def _fetch_twse(client_http: httpx.AsyncClient, stock_no: str, date_str: str):
    try:
        url = (
            f"https://www.twse.com.tw/exchangeReport/STOCK_DAY"
            f"?response=json&stockNo={stock_no}&date={date_str}"
        )
        r = await client_http.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        rows = data.get("data", [])
        if rows:
            last_row = rows[-1]
            close_price = float(last_row[6].replace(",", ""))
            parts = last_row[0].split("/")
            trade_date = f"{int(parts[0]) + 1911}-{parts[1]}-{parts[2]}"
            print(f"[TWSE] {stock_no} 收盤價: {close_price} ({trade_date})")
            return {"price": close_price, "date": trade_date, "source": "台灣證交所(TWSE)"}
    except Exception as e:
        print(f"[TWSE] Error for {stock_no}: {e}")
    return None

async def _fetch_tpex(client_http: httpx.AsyncClient, stock_no: str, query_day):
    try:
        tpex_date = f"{query_day.year - 1911}/{query_day.strftime('%m/%d')}"
        url = (
            f"https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php"
            f"?l=zh-tw&d={tpex_date}&stkno={stock_no}&_=1"
        )
        r = await client_http.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        rows = data.get("aaData", [])
        if rows:
            last_row = rows[-1]
            close_price = float(last_row[6].replace(",", ""))
            parts = last_row[0].split("/")
            trade_date = f"{int(parts[0]) + 1911}-{parts[1]}-{parts[2]}"
            print(f"[TPEx] {stock_no} 收盤價: {close_price} ({trade_date})")
            return {"price": close_price, "date": trade_date, "source": "櫃買中心(TPEx)"}
    except Exception as e:
        print(f"[TPEx] Error for {stock_no}: {e}")
    return None

async def get_twse_closing_price_async(stock_no: str):
    now = datetime.now(TZ_TAIPEI)
    query_day = now
    while query_day.weekday() >= 5:
        query_day -= timedelta(days=1)
    date_str = query_day.strftime("%Y%m%d")
    async with httpx.AsyncClient() as client_http:
        results = await asyncio.gather(
            _fetch_twse(client_http, stock_no, date_str),
            _fetch_tpex(client_http, stock_no, query_day),
            return_exceptions=True
        )
    twse_result = results[0] if not isinstance(results[0], Exception) else None
    tpex_result = results[1] if not isinstance(results[1], Exception) else None
    return twse_result or tpex_result

# ── 【優化3】get_stock_info：有4位數字直接跳過AI ──────────────────
def get_stock_info(keyword: str):
    numbers = re.findall(r'\d{4}', keyword)
    quick_no = numbers[0] if numbers else None

    if quick_no:
        company_name = re.sub(r'\d+', '', keyword).strip() or quick_no
        print(f"[StockInfo] 快速解析: name={company_name}, no={quick_no}")
        return company_name, quick_no

    # 純中文才 fallback Brave + AI
    query = f"台股 {keyword} 股票代號 公司名稱"
    search_context = asyncio.run(brave_search_all([query]))[0]
    if not search_context:
        return keyword.strip(), None
    try:
        sys_prompt = (
            "您是精通台股的助手。請從搜尋結果中提取：\n"
            "1. 公司簡稱（中文，例：中光電、台積電）\n"
            "2. 4位數字股票代號（例：5371、2330）\n"
            "請回傳：「代號:XXXX,名稱:公司簡稱」格式，不可加其他内容。"
        )
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"查詢：{keyword}\n\n搜尋結果：\n{search_context}"}
            ],
            temperature=0,
            max_tokens=30
        )
        result = response.choices[0].message.content.strip()
        print(f"[StockInfo] AI result: {result}")
        code_match = re.search(r'代號[\uff1a:]+\s*(\d{4})', result)
        name_match = re.search(r'名稱[\uff1a:]+\s*([^\s,，]+)', result)
        stock_no = code_match.group(1) if code_match else None
        company_name = name_match.group(1) if name_match else keyword.strip()
        print(f"[StockInfo] name={company_name}, no={stock_no}")
        return company_name, stock_no
    except Exception as e:
        print(f"[StockInfo] Error: {e}")
        return keyword.strip(), None

# ── 路由 ────────────────────────────────────────────────────────
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.get("/api/limit-status")
def get_limit_status(request: Request):
    ip = get_real_ip(request)
    count = get_usage(ip)
    return {"limit": LIMIT_PER_DAY, "used": count, "remaining": max(0, LIMIT_PER_DAY - count)}

@app.post("/api/analyze")
async def analyze_stock(req: AnalyzeRequest, request: Request):
    ip = get_real_ip(request)
    print(f"Analyzing for real IP: {ip}")
    used = get_usage(ip)
    if used >= LIMIT_PER_DAY:
        raise HTTPException(status_code=429, detail=f"您今日的分析次數已達上限 ({LIMIT_PER_DAY} 次)，請明天再試。")
    if not BRAVE_API_KEY or not ZEABUR_AI_API_KEY:
        raise HTTPException(status_code=500, detail="API Keys 未設定齊全，請檢查您 Zeabur 中的 Variables。")

    keyword = req.ticker
    now = datetime.now(TZ_TAIPEI)
    today_date = now.strftime("%Y-%m-%d")
    current_year = now.year
    past_5_yr_start = current_year - 5
    past_5_yr_end = current_year - 1
    recent_trading_day = now
    while recent_trading_day.weekday() >= 5:
        recent_trading_day -= timedelta(days=1)
    recent_date_str = f"{recent_trading_day.year}年{recent_trading_day.month}月{recent_trading_day.day}日"

    # Step 1: 解析名稱與代號
    company_name, stock_no = get_stock_info(keyword)
    print(f"Resolved: name={company_name}, stock_no={stock_no}, trading_day={recent_date_str}")

    # Step 2: 【優化2+1】TWSE/TPEx 與 Brave 7次搜尋同時並行
    name_ticker = f"{company_name} {keyword}"
    queries = [
        f"公司簡介 業務範圍 經營項目 台股 {name_ticker}",
        f"{name_ticker} 毛利率 毛利 gross margin 歷年 goodinfo.tw OR statementdog.com",
        f"{name_ticker} EPS 每股盈餘 {past_5_yr_start} {past_5_yr_end} 財報 cmoney OR goodinfo",
        f"{name_ticker} 年報 {past_5_yr_start}-{past_5_yr_end} 股利 配息 殖利率",
        f"{name_ticker} 近期 新聞 {current_year} 營運 轉型 展望 工商時報 OR 經濟日報 OR 鉅亨網",
        f"{name_ticker} 技術分析 均線 RSI 支撐壓力 {current_year}",
        f"{name_ticker} 籌碼 外資 投信 融資 {current_year}",
    ]

    # 股價 + 所有 Brave 搜尋 全部同時送出
    price_task = get_twse_closing_price_async(stock_no) if stock_no else asyncio.sleep(0, result=None)
    brave_task = brave_search_all(queries)
    price_info, brave_results = await asyncio.gather(price_task, brave_task)

    # 組裝 verified price block
    if price_info:
        verified_price_block = (
            f"\n【已驗證官方股價（不得覆蓋或自行修改）】\n"
            f"收盤價：{price_info['price']}元\n"
            f"交易日期：{price_info['date']}\n"
            f"資料來源：{price_info['source']}\n"
            f"【此數據來自政府官方交易所 API，為 100% 正確的收盤價，AI 必須直接
