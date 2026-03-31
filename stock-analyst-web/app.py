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
LIMIT_PER_DAY = 10
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

def get_company_name(ticker: str):
    """先找出股票代號對應的公司名稱，避免後續搜尋偏移"""
    query = f"台股 {ticker} 公司名稱 官方全名"
    search_context = get_brave_search_results(query)
    
    if not search_context:
        return ticker
        
    try:
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[
                {"role": "system", "content": "您是一位精通台股的助手。請從搜尋結果中提取該股票代號的『公司簡稱』，並只回傳該名稱（例如：台積電、聯嘉）。若找不到請回傳原始代號。"},
                {"role": "user", "content": f"代號：{ticker}\n搜尋結果：\n{search_context}"}
            ],
            temperature=0,
            max_tokens=20
        )
        name = response.choices[0].message.content.strip()
        return name if name else ticker
    except:
        return ticker

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.get("/api/limit-status")
def get_limit_status(request: Request):
    ip = get_real_ip(request)
    print(f"Checking limit for real IP: {ip}")
    count = get_usage(ip)
    return {"limit": LIMIT_PER_DAY, "used": count, "remaining": max(0, LIMIT_PER_DAY - count)}

@app.post("/api/analyze")
def analyze_stock(req: AnalyzeRequest, request: Request):
    ip = get_real_ip(request)
    print(f"Analyzing for real IP: {ip}")
    
    used = get_usage(ip)
    if used >= LIMIT_PER_DAY:
        raise HTTPException(status_code=429, detail=f"您今日的分析次數已達上限 ({LIMIT_PER_DAY} 次)，請明天再試。")
        
    if not BRAVE_API_KEY or not ZEABUR_AI_API_KEY:
        raise HTTPException(status_code=500, detail="API Keys 未設定齊全，請檢查您 Zeabur 中的 Variables。")
        
    keyword = req.ticker
    now = datetime.now(TZ_TAIPEI)  # 台灣時間
    today_date = now.strftime("%Y-%m-%d")
    current_year = now.year
    past_5_yr_start = current_year - 5
    past_5_yr_end = current_year - 1

    # 計算最近的交易日（週一到週五）
    recent_trading_day = now
    while recent_trading_day.weekday() >= 5:  # 5=週六, 6=週日
        recent_trading_day -= timedelta(days=1)
    recent_date_str = recent_trading_day.strftime("%Y年%-m月%-d日")  # 例：2026年3月31日
    recent_date_str_tw = recent_trading_day.strftime("%Y-%m-%d")    # 例：2026-03-31
    # Windows 不支援 %-m，改用 lstrip('0') 方式
    recent_date_str = f"{recent_trading_day.year}年{recent_trading_day.month}月{recent_trading_day.day}日"
    
    # 第一步：先解析公司名稱
    company_name = get_company_name(keyword)
    print(f"Resolved company name: {company_name}, recent trading day: {recent_date_str}")
    
    # 第二步：直接從 TWSE/TPEx 官方 API 取得收盤價（不依賴搜尋，100% 正確）
    # 嘗試解析純數字的股票代號（例如「中光電 5371」→「5371」）
    import re as _re
    clean_ticker = _re.sub(r'[^\d]', '', keyword)[:4]  # 取前4位數字
    if not clean_ticker:
        clean_ticker = keyword  # fallback
    
    price_info = get_twse_closing_price(clean_ticker)
    if price_info:
        verified_price_block = (
            f"\n【已驗證官方股價（不得覆蓋或自行修改）】\n"
            f"收盤價：{price_info['price']}元\n"
            f"交易日期：{price_info['date']}\n"
            f"資料來源：{price_info['source']}\n"
            f"【此數據來自政府官方交易所 API，為 100% 正確的收盤價，AI 必須直接使用，絕對不得替换成其他數字】\n"
        )
    else:
        verified_price_block = "\n【官方股價查詢失敗，請從搜尋結果中判斷最新收盤價】\n"
    
    # 使用「名稱 + 代號」組合搜尋，分類搜尋財報與新聞（股價已有官方 API，不需搜尋）
    name_ticker = f"{company_name} {keyword}"
    queries = [
        # 1. 公司基本資料
        f"公司簡介 業務範圍 經營項目 台股 {name_ticker}",
        # 2. 財報數據 - 分開查詢提升毛利率命中率
        f"{name_ticker} 毛利率 毛利 gross margin 歷年 goodinfo.tw OR statementdog.com",
        f"{name_ticker} EPS 每股盈餘 {past_5_yr_start} {past_5_yr_end} 財報 cmoney OR goodinfo",
        f"{name_ticker} 年報 {past_5_yr_start}-{past_5_yr_end} 股利 配息 殖利率",
        # 3. 近期新聞與展望
        f"{name_ticker} 近期 新聞 {current_year} 營運 轉型 展望 工商時報 OR 經濟日報 OR 鉅亨網",
        # 4. 技術面與籌碼
        f"{name_ticker} 技術分析 均線 RSI 支撐壓力 {current_year}",
        f"{name_ticker} 籌碼 外資 投信 融資 {current_year}"
    ]
    
    full_search_context = verified_price_block  # 官方股價放在最前面
    for q in queries:
        full_search_context += f"【搜尋關鍵字：{q}】\n"
        full_search_context += get_brave_search_results(q) + "\n"
        
    # AI 報告模板 Prompt
    prompt_template = """
    您是一位專業且極具獨立批判性的資深台股分析師。請主要依據「網路搜尋資料」來評估該公司的商業模式、近期轉型與最新動態。
    
    【優先參考資料來源】
    - 股價：Yahoo股市(tw.stock.yahoo.com)、鉅亨網(cnyes.com)、玩股網(wantgoo.com)
    - 財報/毛利率/EPS：Goodinfo台灣股市資訊網(goodinfo.tw)、財報狗(statementdog.com)、CMoney(cmoney.tw)
    - 月營收：公開資訊觀測站(mops.twse.com.tw)、CMoney
    - 新聞：工商時報(ctee.com.tw)、經濟日報(money.udn.com)、鉅亨網
    - 籌碼：玩股網、鉅亨網
    
    對於近期的股價、籌碼、重大新聞與「最新的商業模式 / 轉投資領域」，請務必嚴格依照搜尋結果填寫，切勿僅依賴舊知識。
    財報數據（毛利率、EPS、營收）應優先從 Goodinfo、財報狗、CMoney 的搜尋結果中提取。若搜尋結果有提及具體數字，請務必使用，不可標示「資訊不足」。
    只有在歷史財報數據搜尋結果完全沒有提到時，才可運用您的內建知識庫補齊。
    若內建知識庫也完全沒有該筆資料，才可標示「資訊不足」。
    
    【時間基準提醒】
    本報告產出時間為 {current_year} 年。因此「近 5 年」的財報與股利數據，必須嚴格鎖定在 {past_5_yr_start} 年至 {past_5_yr_end} 年，絕對不可拿 2020 年以前的舊資料充數！若缺乏最新年度數據，請標註「資訊不足」或「預估」。
    
    【極為重要：防幻覺與準確性指令】
    1. 關於「股價 (現價)」：**必須直接使用【已驗證官方股價】區塊中的數据**，該數據來自政府交易所官方 API，為最正確的數字。不得替換成搜尋結果中出現的其他數字。
    2. 關於「日期」：本報告搜尋時間為 {recent_date_str}（{today_date}）。報告中一律使用【已驗證官方股價】區塊中的日期，不可自行推測或填寫日期。
    3. 關於「業務範圍」：嚴禁腦補或將此公司與其他相似名稱的公司混淆。**絕對不要** 提及其未在搜尋結果中明確出現的新事業（例如 AI 算力、餐飲等），除非資料中確實有提到該公司「近期轉型」且有具體進度。
    4. 若發現搜尋資料與股票代號 {keyword} 明顯不符，請在報告開頭標註「警告：搜尋資料可能存在偏移」。
    
    【搜尋資料】：
    (報告基準日：{date})
    {context}
    
    【報告格式要求 (嚴格遵守完整 11 大區塊與 Markdown 語法，請畫表格)】：
    ### 1. 基本資訊 (資料日期：{date})
    - 股票：[代號] [名稱] | 產業：[產業]
    - 現價：[價格]元 | 市值：[市值]
    - 股本：[價格]元
    
    ### 2. 執行摘要
    - **論點**：說明看好/看淡理由
    - **評級**：短期/中期/長期  買進/持有/觀望
    - **目標價**：[低]–[高]元
    
    ### 3. 公司產業與最新動態
    - 商業模式、主要客戶、競爭者
    - 產業週期：衰退/復甦/成長/高峰
    - **近期新聞**：摘要近一個月的重大消息與營運影響
    
    ### 4. 財務表（近5年：{past_5_yr_start}~{past_5_yr_end}）
    | 年度 | 營收 | 毛利% | EPS |
    觀察：近5年成長趨勢與獲利品質變化
    
    ### 5. 配股配息與殖利率（近5年：{past_5_yr_start}~{past_5_yr_end}）
    | 年度 | 現金股利 | 股票股利 | 殖利率 |
    觀察：配發穩定性與近期殖利率水準
    
    ### 6. 估值
    同業平均本益比 或 股價淨值比，本公司評價
    
    ### 7. 技術面
    - MA：均線排列
    - RSI：
    - 支撐：[S1]、壓力：[R1]
    
    ### 8. 籌碼
    - 外資：
    - 融資：
      
    ### 9. 交易計畫
    - **買點**：
    - **停損**：
    - **目標**：
    
    ### 10. 核心風險與燈號評估（🔴紅燈 / 🟡黃燈 / 🟢綠燈）
    - **[燈號] 風險 1**：說明風險事件與潛在影響
    - **[燈號] 風險 2**：說明風險事件與潛在影響
    - **[燈號] 風險 3**：說明風險事件與潛在影響
    *(註：🔴紅燈=高度威脅，🟡黃燈=中度需持續關注，🟢綠燈=低度或已受控)*
    
    ### 11. 綜合結論與建議
    **短線評級：[買進/持有/賣出/觀望]**  
    - 理由點評：
    
    **波段評級：[買進/持有/賣出/觀望]**  
    - 理由點評：
    
    **長期評級：[買進/持有/賣出/觀望]**
    - 理由點評：
    
    ---
    **【投資警語】**
    *本報告由 AI 自動彙整網路資訊生成，僅供研究參考之用，不構成任何形式的投資建議、勸誘、推薦、要約或指導。投資行為具有風險，閣下應審慎評估並自負投資損益，本系統不保證資訊之絕對正確性與即時性。*
    """
    final_prompt = prompt_template.format(
        context=full_search_context, 
        date=today_date,
        today_date=today_date,
        recent_date_str=recent_date_str,
        current_year=current_year,
        past_5_yr_start=past_5_yr_start,
        past_5_yr_end=past_5_yr_end,
        keyword=keyword
    )
    
    try:
        # 使用 OpenAI GPT-4o-mini 模型
        response = client.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        # 成功完成後，增加使用次數
        increment_usage(ip)
        return {"markdown": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
