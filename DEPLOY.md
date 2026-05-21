# 🍜 美食資料庫 - 後台管理系統部署指南

## 系統架構

```
┌─────────────────────────────────────────────────────────────────┐
│                        使用者瀏覽器                               │
│  ┌──────────────────┐         ┌──────────────────────────────┐ │
│  │  GitHub Pages    │         │    Flask 後端伺服器            │ │
│  │  (靜態網站)       │  ───▶  │  ┌────────────────────────┐   │ │
│  │                  │         │  │  Flask App + ChromaDB  │   │ │
│  │  index.html      │         │  │  admin.html (管理介面)  │   │ │
│  │  food.html       │         │  └────────────────────────┘   │ │
│  └──────────────────┘         │         ↓                       │ │
│                              │  ┌────────────────────────┐   │ │
│                              │  │     ChromaDB            │   │ │
│                              │  │  (向量資料庫)          │   │ │
│                              │  └────────────────────────┘   │ │
│                              └──────────────────────────────┘ │
│                                        ↑                       │
│                              可部署到 Railway / Render / Fly.io │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 方式一：本地端測試（用 ngrok 對外暴露）

```bash
cd /home/captor/food-rag/backend

# 安裝依賴
pip install -r requirements.txt

# 複製 ChromaDB 資料（從 food-rag 主目錄）
cp -r ../chromadb_data ./chromadb_data

# 啟動伺服器
python app.py

# 另一個 terminal：安裝 ngrok 並啟動
# npm install -g ngrok
ngrok http 5000

# 複製 ngrok 給你的 URL，例如：https://abc123.ngrok.io
# 那就是你的後台 URL：https://abc123.ngrok.io/admin
```

### 方式二：Docker 部署

```bash
cd /home/captor/food-rag/backend

# 建構並啟動
docker-compose up -d

# 查看日誌
docker-compose logs -f
```

---

## ☁️ 免費部署到雲端

### 選項 1：Railway（推薦，最簡單）

1. 前往 [railway.app](https://railway.app) 並用 GitHub 登入
2. 點 **New Project** → **Deploy from GitHub repo**
3. 選擇 `samtwgt1-arch/sam-tw` 倉庫（或創建新倉庫 `food-rag-admin`）
4. Railway 會自動偵測需要部署的服務

**手動設定：**
1. 在 Railway Dashboard 點 **New Project** → **Empty Project**
2. 點 **Add a Service** → **GitHub**
3. 連結你的 `food-rag/backend` 資料夾（需要把 backend 獨立成一個 GitHub 倉庫）
4. Railway 會自動偵測 Dockerfile

**環境變數設定：**
- `ADMIN_PASSWORD`: 管理密碼（預設 `admin123`，請更換！）
- `CHROMA_DATA_PATH`: `/app/chromadb_data`
- `PORT`: `5000`
- `FLASK_DEBUG`: `false`

**部署完成後的 URL：**
- 管理介面：`https://your-project.railway.app/admin`
- API：`https://your-project.railway.app/api/health`

---

### 選項 2：Render（需要手動設定）

1. 前往 [render.com](https://render.com) 並用 GitHub 登入
2. 點 **New** → **Web Service**
3. 連結你的 GitHub 倉庫（需要把 `backend/` 獨立成一個倉庫）
4. 設定：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 app:app`

**環境變數（在 Render Dashboard 設定）：**
- `ADMIN_PASSWORD`: 你的管理密碼
- `CHROMA_DATA_PATH`: `/app/chromadb_data`
- `FLASK_DEBUG`: `false`

---

### 選項 3：Fly.io（需要 Docker）

```bash
# 安裝 flyctl
curl -L https://fly.io/install.sh | sh

# 登入
fly auth login

# 部署
cd /home/captor/food-rag/backend
fly launch
fly deploy
```

---

## 📝 部署後更新網站連結

部署完成後，拿到你的後端 URL（例如 `https://food-admin.railway.app`），編輯：

**`/home/captor/sam-tw/index.html`** 和 **`/home/captor/sam-tw/food.html`**

把：
```javascript
onclick="alert('請先部署後端服務！...')"
```

替換成：
```javascript
href="https://your-backend-url.railway.app/admin"
```

---

## 🔐 安全設定

### 1. 更換預設密碼

```bash
# 環境變數設定
export ADMIN_PASSWORD='你的強密碼'

# 或在 Railway/Render 的 Dashboard 設定環境變數
```

### 2. 啟用 HTTPS

所有主流部署平台（Railway、Render、Fly.io）都會自動提供 HTTPS，無需額外設定。

---

## 📊 功能說明

### 管理介面（`/admin`）

1. **資料檢視**：瀏覽所有 Collection 和文件
2. **語意搜尋**：用自然語言搜尋餐廳（例如：「龍蝦吃到飽」）
3. **新增資料**：新增吃到飽餐廳的詳細介紹
4. **刪除資料**：刪除不需要的記錄
5. **Collection 管理**：建立、刪除 Collection

### API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health` | GET | 健康檢查 |
| `/api/collections` | GET | 列出所有 Collections |
| `/api/collections/<name>` | GET | 取得 Collection 資訊 |
| `/api/collections/<name>/items` | GET | 取得所有文件（分頁） |
| `/api/collections/<name>/query` | POST | 語意搜尋 |
| `/api/collections/<name>/add` | POST | 新增文件 |
| `/api/collections/<name>/delete` | POST | 刪除文件 |

所有 API 需要 Header：`X-Auth-Password: <你的密碼>`

---

## 🔧 資料遷移

### 從本地搬到 Railway

1. 本地打包：
```bash
cd /home/captor/food-rag
tar -czvf chromadb_backup.tar.gz chromadb_data/
```

2. 上傳到 GitHub Release 或雲端儲存

3. 在 Railway SSH 環境下下載並解壓：
```bash
# 在 Railway 的 Shell 環境執行
wget <你的備份URL>
tar -xzvf chromadb_backup.tar.gz
mv chromadb_data backend/
```

---

## ❓ 常見問題

**Q: ChromaDB 資料會保存在哪裡？**
A: 預設在 `./chromadb_data/` 目錄。Railway 部署時會自動掛在一個持久化的 volume。

**Q: 可以不用部署，直接本地使用嗎？**
A: 可以！用 `ngrok` 對外暴露本地端就可以讓外部存取。

**Q: 如何備份資料？**
A: 把 `chromadb_data/` 資料夾複製到雲端儲存（如 GitHub Gist、Google Drive）。

**Q: 管理密碼忘記了怎麼辦？**
A: 刪除 Railway/Render 的 Web Service 環境變數 `ADMIN_PASSWORD`，然後重新設定。

---

## 📁 目錄結構

```
food-rag/
├── backend/
│   ├── app.py              # Flask 主程式
│   ├── admin.html          # 管理介面（嵌入式）
│   ├── requirements.txt    # Python 依賴
│   ├── Dockerfile          # Docker 建構檔
│   ├── docker-compose.yml  # Docker Compose
│   ├── Procfile            # Render 部署用
│   ├── static/             # 靜態檔案
│   └── templates/          # HTML 模板
└── chromadb_data/          # 向量資料庫（本地）
```