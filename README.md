# 星語助手 Discord Bot


# 🤖 DC 多功能 Discord Bot

這是一款模組化設計的 Discord 機器人，支援股票、加密貨幣、任務管理、天氣查詢、地震通知、音樂播放與自動回覆等功能，適用於日常群組管理與投資者輔助。

## 🚀 功能模組一覽

### 📈 股票查詢與提醒
- `-2330 / -AAPL`：查詢即時價格與圖表（台股/美股自動判斷）
- `-2330 600`：設定價格提醒
- `-取消 2330`：取消提醒
- `-清單`：查看追蹤清單

### 💰 加密貨幣查詢與提醒
- `BTC / ETH`：查詢幣價與 TradingView 圖表
- `BTC 70000`：設定幣價通知
- `取消 BTC`：取消提醒
- `清單`：顯示幣價清單

### 📝 任務系統
- `任務 明天 洗衣服`：新增任務
- `刪任務 洗衣服`：刪除任務
- `完成 洗衣服`：標記完成
- `延後 洗衣服 2天`：延後任務
- `週計畫`：甘特圖任務視覺化
- `日曆圖`：任務熱力圖
- `回顧`：已完成任務回顧

### 🌦️ 天氣查詢與報時
- `天氣`：即時天氣（含體感與紫外線）
- `報時 now12`：中午天氣推播
- `報時 now18`：晚上天氣推播
- `報時 tomorrow`：明天預報

### 🌍 地震通知
- `地震`：查詢最近台灣本島 ≥ 4 的地震（含地圖）

### ▶️ 音樂播放
- `play <url>`：播放 YouTube 音樂
- `skip`：跳過
- `stop`：停止並離開語音

### 🎴 自動回應
- `omikuji`：抽御神籤（支援 12 段運勢）

---

## 🛠 安裝與執行

### 安裝套件
```bash
pip install -r requirements.txt
```

### 啟動機器人
```bash
python bot.py
```

---

## ⚙️ 設定檔 `.env` 範例
```
DISCORD_TOKEN=你的機器人 Token
CWB_TOKEN=你的中央氣象局 API 金鑰
WEATHER_LOCATION=新北市
CHROMEDRIVER_PATH=chromedriver
GOOGLE_CHROME_BIN=chrome.exe
```

---

## 📁 專案結構
```
project/
├── bot.py
├── cogs/
│   ├── auto_response.py
│   ├── crypto_alerts.py
│   ├── earthquake.py
│   ├── music.py
│   ├── stock_alerts.py
│   ├── task.py
│   ├── weather.py
│   └── weather_alerts.py
├── utils/
│   └── cwb.py
├── data/
│   ├── stock_alerts.db
│   └── crypto_alerts.json
├── .env
├── requirements.txt
└── README.md
```

---
