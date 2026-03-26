import os
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
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

class AnalyzeRequest(BaseModel):
    ticker: str

def get_brave_search_results(query: str):
    """透過 Brave Search API 取得搜尋結果摘要"""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {"q": query, "count": 5, "search_lang": "zh-hant"}
    
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

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

@app.post("/api/analyze")
def analyze_stock(req: AnalyzeRequest):
    if not BRAVE_API_KEY or not ZEABUR_AI_API_KEY:
        raise HTTPException(status_code=500, detail="API Keys 未設定齊全，請檢查您 Zeabur 中的 Variables。")
        
    keyword = req.ticker
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # 組合多個關鍵字確保擷取全面數據
    queries = [
        f"公司簡介 業務範圍 轉投資 轉型 台股 {keyword}",
        f"現價 市值 台股 {keyword} 2026",
        f"近5年財報 EPS 毛利率 台股 {keyword} 2026",
        f"近5年 配股配息 殖利率 台股 {keyword}",
        f"近一個月 最新動態 重大新聞 鉅亨網 經濟日報 工商時報 Yahoo股市 台股 {keyword} 2026",
        f"技術面 均線 RSI 支撐壓力 台股 {keyword} 2026",
        f"外資買賣超 融資餘額 台股 {keyword} 2026"
    ]
    
    full_search_context = ""
    for q in queries:
        full_search_context += f"【搜尋關鍵字：{q}】\n"
        full_search_context += get_brave_search_results(q) + "\n"
        
    # AI 報告模板 Prompt
    prompt_template = """
    您是一位專業且極具獨立批判性的資深台股分析師。請主要依據「網路搜尋資料」來評估該公司的商業模式、近期轉型與最新動態。
    對於近期的股價、籌碼、重大新聞與「最新的商業模式 / 轉投資領域」，請務必嚴格依照搜尋結果填寫，切勿僅依賴舊知識（特別注意公司是否已跨足新產業，例如無人機、AI、半導體等）。
    只有在 2021-2023 年之前的歷史財報數據確實查不到時，才可運用您的內建知識庫補齊。
    若各界資料都完全找不到，才可標示「資訊不足」。
    
    【極為重要：投資評級必須客觀、無私且具備批判性】
    身為專業分析師，請絕對不要有「預設看多」或「避諱給出負面評價」的 AI 包袱！如果發現營收衰退、毛利下滑、技術線型轉弱（如跌破重要支撐），或是有負面重大新聞、外資連日賣超，請毫不猶豫地在第 11 項結論中給出「賣出」建議。請展現真實華爾街分析師的冷酷與客觀。
    
    【搜尋資料】：
    (資料日期：{date})
    {context}
    
    【報告格式要求 (嚴格遵守完整 11 大區塊與 Markdown 語法，請畫表格)】：
    ### 1. 基本資訊 (資料日期：{date})
    - 股票：[代號] [名稱] | 產業：[產業]
    - 現價：[價格]元 | 市值：[市值]
    
    ### 2. 執行摘要
    - **論點**：說明看好/看淡理由
    - **評級**：短期/中期/長期  買進/持有/觀望
    - **目標價**：[低]–[高]元
    
    ### 3. 公司產業與最新動態
    - 商業模式、主要客戶、競爭者
    - 產業週期：衰退/復甦/成長/高峰
    - **近期新聞**：摘要近一個月的重大消息與營運影響
    
    ### 4. 財務表（近5年）
    | 年度 | 營收 | 毛利% | EPS |
    觀察：近5年成長趨勢與獲利品質變化
    
    ### 5. 配股配息與殖利率（近5年）
    | 年度 | 現金股利 | 股票股利 | 殖利率 |
    觀察：配發穩定性與近期殖利率水準
    
    ### 6. 估值
    同業平均 P/E 或 P/B，本公司評價
    
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
    """
    
    final_prompt = prompt_template.format(context=full_search_context, date=today_date)
    
    try:
        # 使用 OpenAI GPT-4o-mini 模型
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        return {"markdown": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
