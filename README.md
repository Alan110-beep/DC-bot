# DC Discord Bot

一個模組化、多功能的 Discord 機器人，支援股票與幣價追蹤、天氣查詢與自動推播、音樂播放、地震速報、任務管理等功能。

---

## 📦 功能模組

| 模組             | 指令 / 功能說明                                             |
|------------------|----------------------------------------------------------|
| 音樂播放          | `play <YouTube網址>`、`skip`、`stop`                    |
| 御神籤抽籤        | `omikuji`                                                |
| 天氣查詢          | `天氣`、`報時 now12` / `now18` / `tomorrow`             |
| 天氣預警推播      | 紫外線、濕度、強風、豪雨自動監測推播                        |
| 地震通知          | `地震` 查詢最近一筆台灣本島 ≥4 級地震，自動推播            |
| 股票提醒          | `2330 700` → 價格達標推播，`清單`、`取消 <股票>`、`查 <股票>` |
| 加密幣提醒        | `BTC 70000` → 達標推播，`清單`、`取消 BTC`、`BTC` 查價     |
| 任務管理          | `任務 明天 繳費`、`完成 繳費`、`刪任務 繳費` 等            |

---

## 🚀 快速開始

### 1. 建立並啟動虛擬環境
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate  # macOS/Linux
```

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 建立 `.env` 設定檔
```env
DISCORD_TOKEN=你的機器人Token
CWB_TOKEN=你的中央氣象局API金鑰
WEATHER_LOCATION=新北市
```

### 4. 啟動 Bot
```bash
python bot.py
```

---

## ☁️ 推送到 GitHub

### 初始化 Git 並推送
```bash
git init
git add .
git commit -m "🎉 初始提交：上傳 DC Discord Bot"
git branch -M main
git remote add origin https://github.com/你的帳號/你的repo.git
git push -u origin main
```

### 常用 Git 指令
```bash
git status          # 查看當前變更狀態
git add .           # 將所有變更加入暫存區
git commit -m "訊息"  # 提交變更
git log             # 查看提交歷史
git pull            # 拉取遠端最新程式碼
git push            # 推送程式碼到 GitHub
```

---

## 🔒 資安提醒
請確保 `.env` 未被加入 Git，應加入 `.gitignore` 內容如下：
```gitignore
.env
data/
__pycache__/
*.pyc
```

---

## 📁 專案結構
```
Bot/
├── bot.py
├── .env.example
├── requirements.txt
├── README.md
├── cogs/
│   ├── music.py
│   ├── auto_response.py
│   ├── weather.py
│   ├── weather_alerts.py
│   ├── earthquake.py
│   ├── stock_alerts.py
│   └── task.py
├── utils/
│   └── cwb.py
└── data/  # 設定儲存與資料暫存（不加入 Git）
```

---

