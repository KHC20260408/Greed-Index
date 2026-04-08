# Greed-Index

自動每日抓取 CNN Fear & Greed Index（及其子指標）並記錄為 `greed-index-data.csv`。

CSV 欄位（columns）:
- date: YYYY-MM-DD（UTC）
- timestamp: ISO8601 timestamp（UTC）
- fear_greed, fear_greed_label
- market_momentum, market_momentum_label
- stock_strength, stock_strength_label
- junk_bond, junk_bond_label
- volatility, volatility_label
- put_call, put_call_label
- breadth, breadth_label
- safe_haven, safe_haven_label

部署步驟（快速）:
1. 在 GitHub 建立 repository: `KHC20260408/Greed-Index`（public 或 private）
2. 將上述檔案放到 repo 根目錄（或用 web UI 新增檔案）
3. Push 後，Actions 會在排程時間執行，第一次執行會產生 `greed-index-data.csv` 並推回 repo

手動執行（本機）:
- 安裝依賴: `pip install -r requirements.txt`
- 執行: `python greed-index-scraper.py`