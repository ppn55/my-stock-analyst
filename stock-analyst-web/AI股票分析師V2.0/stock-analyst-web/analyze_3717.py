import sys
sys.path.append('.')
from app import analyze_stock, AnalyzeRequest
from unittest.mock import MagicMock

def main():
    ticker = "3717"
    print(f"開始分析「{ticker}」...")
    try:
        req = AnalyzeRequest(ticker=ticker)
        # 模擬 FastAPI Request 並帶入 localhost IP 以繞過限制 (測試用)
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}
        
        res = analyze_stock(req, mock_request)
        
        filename = f"{ticker}_萬潤_分析報告.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(res['markdown'])
        print(f"✅ 分析成功！報表已存入 {filename}")
        print("\n--- 報告內容摘要 ---\n")
        print(res['markdown'][:1000] + "...")
    except Exception as e:
        print(f"❌ 分析失敗: {e}")

if __name__ == "__main__":
    main()
