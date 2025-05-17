DC Discord Bot
一個功能強大的多模組 Discord Bot，支援天氣查詢、地震速報、股幣查價、自選與提醒、任務管理、音樂播放、中文互動回覆等功能。

📁 專案結構
shell
複製
編輯
DC-bot/
├── bot.py
├── requirements.txt
├── .env.example
├── README.md
├── .gitignore
├── triggers.py
├── cogs/
│   ├── auto_response.py
│   ├── help.py
│   ├── music.py
│   ├── task.py
│   ├── weather.py
│   ├── weather_alerts.py
│   ├── earthquake.py
│   └── stock_alerts.py
├── data/
│   └── tasks.json
└── ...
⚙️ 安裝與啟動
bash
複製
編輯
# 進入你的專案資料夾
cd DC-bot

# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境（Windows）
.venv\Scripts\activate

# 或（macOS/Linux）
source .venv/bin/activate

# 安裝所有套件
pip install -r requirements.txt

# 建立 .env 設定（可參考 .env.example）
# 修改成你的 DISCORD_TOKEN、CWB_TOKEN、WEATHER_LOCATION 等

# 啟動機器人
python bot.py
🛠️ 主要功能一覽
互動回覆：「抽」「笑話」「安慰我」等超多趣味互動

天氣查詢：「天氣」「報時 now12」「報時 tomorrow」…支援自動推播/定時預報

地震速報：台灣地區有感地震自動/手動查詢

股市查詢：查詢台股、美股、幣圈現價，自選追蹤、價格提醒

任務管理：純文字新增、延後、完成、刪除任務，週計畫甘特圖、月熱力日曆

音樂播放：YouTube 連結/關鍵字播放、暫停、繼續、重播、播放清單

help 說明：全功能中文 help 指令（help/幫助/說明/指令）

超多隱藏彩蛋：更多彩蛋可在 triggers.py 增減

📝 .env 參數說明（建議建立 .env.example）
env
複製
編輯
DISCORD_TOKEN=你的 Discord Bot Token
CWB_TOKEN=你的中央氣象局 Token
WEATHER_LOCATION=查詢天氣預設地區（例如：新北市）
📄 License
MIT

.gitignore 範例
gitignore
複製
編輯
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
env/
.venv/
venv/
ENV/
env.bak/
*.sqlite3
*.log

# Env
.env
.env.*
.envrc

# VSCode
.vscode/
*.code-workspace

# 系統
.DS_Store
Thumbs.db

# Playwright
playwright/.cache/

# Data 資料夾
data/*
!data/.gitkeep
🟢 常見問題（FAQ）
Q1. 為什麼「地震/天氣」功能無法取得資料？
A：請檢查本機網路 nslookup opendata.cwb.gov.tw 是否查得到 IP。若查不到，通常是 DNS 或網路問題，程式碼無需修改。
如換用 4G 熱點、公司網路或部署到雲端（如 Render、Railway）通常可解決。

Q2. 播放音樂顯示 PyNaCl library needed？
A：請在虛擬環境安裝 pynacl：pip install pynacl，並補到 requirements.txt。

Q3. 播放音樂顯示 youtube_dl 解析錯誤？
A：請改用 yt-dlp，安裝：pip install yt-dlp，並將 music.py 改用 from yt_dlp import YoutubeDL。

Q4. 有新指令、功能要怎麼讓 help/說明同步？
A：新增互動回覆→只需補 triggers.py，其他主要指令請同步更新 cogs/help.py 的 GROUPED_COMMANDS。

Q5. 如何保護敏感資訊不外流？
A：.env、.env.*、資料庫、token 等敏感檔案皆已在 .gitignore 中排除，不要上傳到公開倉庫。

🟢 快速指令範例（可放 README 最後一節）
分類	指令範例	功能簡述
互動回覆	抽、笑話、安慰我、抱抱、嗆我...	趣味互動/彩蛋
音樂播放	播放 <網址/關鍵字>、暫停、重播、清單	播放 YouTube 音樂
任務管理	任務 明天 交報告、完成 報告、週計畫	管理個人任務甘特圖
股市查詢	查 2330、查 AAPL、追蹤 2330、提醒 2330	股價查詢/自選/提醒
天氣查詢	天氣、報時 now12、報時 tomorrow	即時天氣/預報/定時
地震速報	地震	最近有感地震查詢
說明	help、幫助、指令、說明	列出所有主要指令

🟢 初次專案 Git 操作流程
1. 初始化 Git 倉庫
bash
複製
cd DC-bot      # 進入你的專案資料夾
git init       # 初始化本地 git
2. 建立 .gitignore，避免敏感檔案誤上傳
（你已經有了就不用再新建，只要 git add 時包含這個檔案即可）

3. 連接到 GitHub（假設你已在 GitHub 建好 DC-bot 倉庫）
bash
複製
git remote add origin https://github.com/你的帳號/DC-bot.git
4. 第一次提交與推送
bash
複製
git add .                    # 加入所有檔案
git commit -m "init commit"  # 首次提交
git branch -M main           # 設 main 為主分支（若還不是）
git push -u origin main      # 推送到 GitHub
🟢 以後日常同步與版本管理
新增或修改後：
bash
複製
git status              # 看看哪些檔案改動
git add .               # 加入所有改動（也可 git add 檔案名）
git commit -m "說明"    # 提交變更，建議填寫清楚的 commit message
git push                # 推送到遠端
🟢 拉取遠端更新（避免衝突/多人協作時必做）
bash
複製
git pull                # 拉最新的遠端 main 分支
🟢 常見小技巧與補充說明
git log：查看歷史紀錄

git diff：比對目前變動內容

git checkout 檔案名：還原單一檔案到最後一次 commit 狀態

建議主資料夾只放 code，資料、日誌、venv、.env 都列入 .gitignore

每次修改完盡量 git commit 一次，備份/還原都方便

🟢 簡單口訣
加新東西 → add → commit → push

上班/換電腦/和別人同步 → pull

🟢 VS Code 使用者福利
你可以用 VS Code 內建 Git 面板直接點選操作（加檔案、寫 commit、同步）超直覺！

🟢 如果想備份 env 範例
通常把 .env.example 上傳，.env 本身絕對不要傳！