from duckduckgo_search import DDGS

import sys
sys.stdout.reconfigure(encoding='utf-8')

queries = [
    "台股 中光電 股票代號",
    "中光電 5371 毛利率",
    "新聞 中光電 5371 營運 展望",
]

with DDGS() as ddgs:
    for q in queries:
        print(f"\n--- Query: {q} ---")
        try:
            results = ddgs.text(q, region='tw-tzh', safesearch='off', max_results=3)
            if not results:
                print("NO RESULTS")
            for res in results:
                print(f"[{res.get('title')}] {res.get('body')}")
        except Exception as e:
            print(f"Error: {e}")
