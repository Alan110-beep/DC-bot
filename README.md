# DC Discord Bot

一個功能強大的多模組 Discord 機器人，整合天氣查詢、地震速報、股票與加密貨幣追蹤、任務管理與音樂播放。

---

## 📁 專案結構

```
DC-bot/
├── bot.py
├── .env.example
├── requirements.txt
├── README.md
├── .gitignore
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
└── data/
    └── stock_alerts.db
```

---

## ⚙️ 安裝與執行

```bash
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數（複製 .env.example 並改名為 .env）

# 啟動機器人
python bot.py
```

---

## 🔐 .env.example 設定範例

```env
DISCORD_TOKEN=你的 Discord Bot Token
CWB_TOKEN=你的中央氣象局 API Token
WEATHER_LOCATION=新北市
CHROMEDRIVER_PATH=chromedriver.exe 絕對路徑（若使用 selenium）
GOOGLE_CHROME_BIN=chrome.exe 絕對路徑（若使用 selenium）
```

---

## 🧠 支援功能模組

- `music.py`：YouTube 音樂播放
- `auto_response.py`：御神籤互動（omikuji）
- `weather.py`：天氣查詢、定時報時、紫外線與體感溫度
- `weather_alerts.py`：豪雨、強風、濕度與紫外線警示
- `earthquake.py`：地震速報與查詢（限台灣本島 M≥4）
- `stock_alerts.py`：股票查詢、K線圖、突破通知、價格追蹤（台美股）
- `crypto_alerts.py`：加密幣即時查詢與價格通知（CoinGecko）
- `task.py`：任務新增、延後、刪除、完成與甘特圖/日曆圖顯示

---

## ✅ 指令總覽

| 模組       | 指令內容                            | 範例                         |
|------------|-------------------------------------|------------------------------|
| 音樂播放   | `play <網址>` `skip` `stop`         | play https://...             |
| 御神籤     | `omikuji`                            | omikuji                      |
| 天氣查詢   | `天氣` `報時 now12/now18/tomorrow` | 天氣 / 報時 now12           |
| 地震查詢   | `地震`                               | 地震                         |
| 股票查詢   | `-2330` 或 `-AAPL` 或 `-2330 600`   | -2330 / -AAPL / -2330 600    |
| 股票清單   | `-清單` `-取消 <代碼>`              | -清單 / -取消 2330          |
| 幣價查詢   | `BTC` / `ETH` / `DOGE`              | BTC / ETH 20000              |
| 幣價清單   | `清單` `取消 <代碼>`                | 清單 / 取消 BTC             |
| 任務管理   | `任務`, `完成`, `刪任務`, `延後`, `週計畫`, `回顧`, `日曆圖` | 任務 6/10~6/12 報告撰寫 |

---

## 🧪 Git 操作教學

### 初始化專案
```bash
git init
git remote add origin https://github.com/你的帳號/DC-bot.git
git add .
git commit -m "🎉 初始提交：上傳 DC Discord Bot"
git push -u origin main  # 或 master
```

### 常用 Git 指令
```bash
git status         # 查看目前變更

# 如果 push 被拒絕（遠端有內容）
git pull origin main --allow-unrelated-histories  # 合併遠端內容
git push -u origin main

# 強制推送（會覆蓋遠端）
git push -f origin main

#下載一份新的資料夾 DC-bot，裡面包含遠端所有檔案與 .git 記錄。
git clone https://github.com/Alan110-beep/DC-bot.git
---

## 📦 .gitignore 建議
```
.env
__pycache__/
*.log
*.sqlite3
data/
*.db
venv/
```

---

## 📜 授權
MIT License
